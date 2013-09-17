#!/usr/bin/env python

# internal
import gicore.signatures

# pycrypto
import Crypto.PublicKey.RSA

# stdlib
import unittest
import random
import os
import StringIO

def get_pseudo_random_bytes(nbytes):
	return "".join([chr(random.getrandbits(8)) for i in xrange(nbytes)])

class TestSignatures(unittest.TestCase):
	def setUp(self):
		random.seed(int(os.environ.get("RANDOM_SEED", 1)))

		self.keys = []
		for i in xrange(int(os.environ.get("NKEYS", 3))):
			self.keys.append(Crypto.PublicKey.RSA.generate(
				bits = int(os.environ.get("KEYSIZE", 2048)),
				randfunc = get_pseudo_random_bytes
			))
		assert len(self.keys) > 1

	def test_signing(self):
		message = get_pseudo_random_bytes(
			int(os.environ.get("MESSAGE_SIZE", 2000)))
		bad_message = get_pseudo_random_bytes(
			int(os.environ.get("MESSAGE_SIZE", 2000)))

		for i, k in enumerate(self.keys):
			message_file = StringIO.StringIO(message)
			bad_message_file = StringIO.StringIO(bad_message)

			sig = gicore.signatures.sign_file(message_file, k)
			sig_file = StringIO.StringIO(sig)
			bad_sig = gicore.signatures.sign_file(
				message_file, self.keys[(i + 1) % len(self.keys)])
			bad_sig_file = StringIO.StringIO(bad_sig)

			message_file.seek(0)
			sig_file.seek(0)
			self.assertTrue(gicore.signatures.verify_file(
				message_file, sig_file, k))

			bad_message_file.seek(0)
			sig_file.seek(0)
			self.assertFalse(gicore.signatures.verify_file(
				bad_message_file, sig_file, k))

			# Signature for correct message but with wrong key
			message_file.seek(0)
			bad_sig_file.seek(0)
			self.assertFalse(gicore.signatures.verify_file(
				message_file, bad_sig_file, k))

if __name__ == '__main__':
    unittest.main()
