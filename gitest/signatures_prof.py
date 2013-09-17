#!/usr/bin/env python

"""
This is a small profiling script used to determine how long it takes to verify
a file's signature.

.. note::

	John (9/13/2013): I ran this with a key size of 16384 bits and the
	verification time was negligible on my system. It is unlikely to be a
	problem for our application.

"""

# internal
import gicore.signatures
import gicore.filetransfer

# stdlib
import cProfile as profile
import random
import StringIO
import pkg_resources
import os

# pycrypto
import Crypto.PublicKey.RSA

def get_pseudo_random_bytes(nbytes):
	return "".join([chr(random.getrandbits(8)) for i in xrange(nbytes)])

key = Crypto.PublicKey.RSA.importKey(
	pkg_resources.resource_string("gitest.data", "test_rsa.pem"))

message_size = int(os.environ.get("MESSAGE_SIZE", 100000))
print "Using message with %d bytes" % (message_size, )
message = get_pseudo_random_bytes(message_size)
message_file = StringIO.StringIO(message)

print "Signing message"
sig = gicore.signatures.sign_file(message_file, key)
sig_file = StringIO.StringIO(sig)

print "Profiling gicore.signatures.verify_file"
profile.run("gicore.signatures.verify_file(message_file, sig_file, key)")
