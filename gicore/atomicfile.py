"""
This module helps support atomic filesystem operations.

:note: Atomic in this context means that a particular operation will either
        succeed or fail, but will not corrupt data. A strong guarantee against
        data corruption is impossible as far as I know, but this module gets
        as close as possible.

:note: This code was adapted from code available at
        https://github.com/sashka/atomicfile

"""

# stdlib
import errno
import os
import tempfile

def _check_filesystems(path_a, path_b):
    """
    Determines if two files are on the same filesystem.

    :param path_a: The path to the first file.
    :param path_b: The path to the second file. If this file does not exist,
            then `os.path.dirname(path_b)` will be checked instead (which will
            be the filesystem that the file will be on when it is created).

    :warning: Using this function and then performing an action on a file
            introduces a potential issue in that by the time you perform the
            action the file could have been placed onto another file system
            (with the mount command on Linux for example).

    """

    dev_a = os.lstat(path_a).st_dev
    try:
        dev_b = os.lstat(path_b).st_dev
    except OSError:
        deb_b = os.lstat(os.path.dirname(path_b)).st_dev
    return dev_a == dev_b

def _make_temp(path):
    """
    Creates a temporary file in the same directory, and with a similar name, as
    another file.

    If an exception occurs for whatever reason, the file will be destroyed and
    the exception reraised.

    :param path: The path of the original file..

    :returns: An open file object.

    """

    dir_path, filename = os.path.split(path)
    os_handle, temp_path = tempfile.mkstemp(
        prefix = ".%s-" % (filename, ),
        dir = dir_path,
        text = False # binary mode
    )
    f = None
    try:
        f = os.fdopen(os_handle, "wb")
    except:
        # f could be none if the call to fdopen raises an exception.
        if f is None:
            os.close(os_handle)
        else:
            f.close()
        os.remove(temp_path)
        raise
    return f, temp_path

class AtomicFile(object):
    """
    Writeable file object that atomically writes a file.

    All writes will go to a temporary file until close() is called, at which
    point the temporary file will be moved over the original. This is *mostly*
    guarenteed to be atomic.

    If the object is destroyed without being closed, all your writes are
    discarded.

    """

    supported_modes = ["wb"]

    def __init__(self, path, mode = "wb"):
        if mode not in AtomicFile.supported_modes:
            raise NotImplemented(
                "mode must be one of %s" % (str(supported_modes), )
            )

        self._path = path  # permanent path
        self._temp_file, self._temp_path = _make_temp(path)

        # delegated methods
        self.write = self._temp_file.write
        self.fileno = self._temp_file.fileno

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type:
            return
        self.close()

    def read(self):
        raise NotImplemented()

    def close(self):
        if not self._temp_file.closed:
            self._temp_file.close()
            # Because they are in the same directory, this should never happen.
            # If it does occur, the write may not be atomic.
            assert _check_filesystems(self._temp_path, self._path)
            os.rename(self._temp_path, self._path)

    def discard(self):
        if self._temp_file.closed:
            raise ValueError("File already closed.")

        try:
            os.remove(self._temp_path)
        except OSError:
            pass
        self._temp_file.close()

    def __del__(self):
        # constructor actually did something
        temp_file = getattr(self, "_temp_file", None)
        if temp_file is not None and not temp_file.closed:
            self.discard()
