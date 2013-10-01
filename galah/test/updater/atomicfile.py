#!/usr/bin/env python

"""
.. note::

    This code was adapted from code available at
    https://github.com/sashka/atomicfile. It was originally licensed under
    the MIT license, but any modifications since then are not. Please see
    the *AtomicFile Licensing Considerations* document for more
    information.

"""

# stdlib
import os
import unittest
import errno
import random
import tempfile
import stat

# gicore
import gicore.atomicfile

def create_temp_file():
    "Creates a temporary file, closes it, and returns the path to it."

    os_handle, path = tempfile.mkstemp()
    os.close(os_handle)
    return path

def get_pseudo_random_bytes(nbytes):
    return "".join([chr(random.getrandbits(8)) for i in xrange(nbytes)])

class AtomicFileTest(unittest.TestCase):
    def setUp(self):
        random.seed(int(os.environ.get("RANDOM_SEED", 1)))

        self.temp_path = create_temp_file()

    def tearDown(self):
        os.remove(self.temp_path)

    def test_write(self):
        expected = get_pseudo_random_bytes(256)
        f = gicore.atomicfile.AtomicFile(self.temp_path)
        f.write(expected)
        f.close()

        with open(self.temp_path, "rb") as f:
            self.assertEqual(f.read(), expected)

    def test_discard(self):
        not_expected = get_pseudo_random_bytes(256)
        f = gicore.atomicfile.AtomicFile(self.temp_path)
        f.write(not_expected)
        f.discard()

        with open(self.temp_path, "rb") as f:
            self.assertNotEqual(f.read(), not_expected)

    def test_discard_close(self):
        "Ensures that a file is closed after discard() is called."

        not_expected = get_pseudo_random_bytes(256)
        f = gicore.atomicfile.AtomicFile(self.temp_path)
        f.write(not_expected)
        f.discard()
        self.assertRaises(ValueError, f.write, get_pseudo_random_bytes(256))

    def test_close(self):
        f = gicore.atomicfile.AtomicFile(self.temp_path)
        f.write(get_pseudo_random_bytes(256))
        f.close()
        self.assertRaises(ValueError, f.write, get_pseudo_random_bytes(256))

    def test_with(self):
        with gicore.atomicfile.AtomicFile(self.temp_path) as f:
            f.write(get_pseudo_random_bytes(256))
        self.assertRaises(ValueError, f.write, get_pseudo_random_bytes(256))

    def test_permissions(self):
        f = gicore.atomicfile.AtomicFile(self.temp_path)
        f.write(get_pseudo_random_bytes(256))
        f.close()

        st_mode = stat.S_IMODE(os.lstat(self.temp_path).st_mode)
        self.assertEqual(st_mode, 0600)

if __name__ == "__main__":
    unittest.main()
