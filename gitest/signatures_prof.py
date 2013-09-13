#!/usr/bin/env python

# internal
import gicore.signatures
import gicore.discovery

# stdlib
import cProfile as profile
import random
import StringIO
import os

# pycrypto
import Crypto.PublicKey.RSA

def get_pseudo_random_bytes(nbytes):
	return "".join([chr(random.getrandbits(8)) for i in xrange(nbytes)])

key_size = gicore.discovery.RSA_KEY_SIZE
key = Crypto.PublicKey.RSA.importKey(open(os.environ["TEST_KEY"], "rb").read())

message_size = int(os.environ.get("MESSAGE_SIZE", 100000))
print "Using message with %d bytes" % (message_size, )
message = get_pseudo_random_bytes(message_size)
message_file = StringIO.StringIO(message)

print "Signing message"
sig = gicore.signatures.sign_file(message_file, key)
sig_file = StringIO.StringIO(sig)

print "Profiling gicore.signatures.verify_file"
profile.run("gicore.signatures.verify_file(message_file, sig_file, key)")
