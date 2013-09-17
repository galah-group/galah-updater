#!/usr/bin/env python

# internal
import gicore.signatures
import gicore.filetransfer
import gicore.errors

# pycrypto
import Crypto.PublicKey.RSA

# stdlib
import multiprocessing
import stat
import httplib
import tempfile
import pkg_resources
import os
import signal
import unittest
import random
import SimpleHTTPServer
import SocketServer
import socket
import shutil
import time

class ForkingWebServer:
	"""
	Simple web server for testing purposes.

	:ivar listen_on: A tuple `(address, port)`.
	:ivar serve_directory: The directory to serve files from.

	:warning: This is not for serious use and was only made for use by this
			unit testing module. Usage outside of this context is a bad idea.

	"""

	def __init__(self, listen_on, serve_directory):
		self.listen_on = listen_on
		self.serve_directory = serve_directory
		self._process = None

	def _run_server(self):
		os.chdir(self.serve_directory)

		class ReusableTCPServer(SocketServer.TCPServer):
			allow_reuse_address = True
			__init__ = SocketServer.TCPServer.__init__
		httpd = ReusableTCPServer(self.listen_on,
			SimpleHTTPServer.SimpleHTTPRequestHandler)
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			return
		assert False

	def start(self):
		if self._process is not None:
			raise RuntimeError("Process still running.")
		self._process = multiprocessing.Process(
			target = ForkingWebServer._run_server, args = (self, ))
		self._process.daemon = True
		self._process.start()

	def stop(self):
		if self._process is None:
			raise RuntimeError("Process is already stopped/stopping.")
		os.kill(self._process.pid, signal.SIGINT)
		self._process.join()
		assert not self._process.is_alive()
		self._process = None

	def __del__(self):
		try:
			self.stop()
		except RuntimeError:
			pass

def get_pseudo_random_bytes(nbytes):
	return "".join([chr(random.getrandbits(8)) for i in xrange(nbytes)])

class TestFileTransfer(unittest.TestCase):
	def setUp(self):
		self.temp_dir = tempfile.mkdtemp()
		random.seed(int(os.environ.get("RANDOM_SEED", 1)))
		self.key = Crypto.PublicKey.RSA.importKey(
			pkg_resources.resource_string("gitest.data", "test_rsa.pem"))

		# Create and sign some files in the temp directory
		nfiles = int(os.environ.get("NFILES", 2))
		assert nfiles > 0
		self.test_files = []
		for i in xrange(nfiles):
			filename = "test%s.txt" % (i, )
			self.test_files.append(filename)
			filepath = os.path.join(self.temp_dir, filename)
			# Make the file
			with open(filepath, "wb") as f:
				f.write(get_pseudo_random_bytes(
					int(os.environ.get("FILE_SIZE", 2048))))
			# Create signature
			with open(filepath, "rb") as f:
				sig = gicore.signatures.sign_file(f, self.key)
			# Save signature
			with open(filepath + ".sig", "wb") as f:
				f.write(sig)

		self.listen_on = ("127.0.0.1", 8888)
		self.httpd = ForkingWebServer(self.listen_on,
			serve_directory = self.temp_dir)
		self.httpd.start()
		time.sleep(2)

	def tearDown(self):
		self.httpd.stop()
		self.httpd = None
		shutil.rmtree(self.temp_dir)
		self.temp_dir = None

	def compare_files(self, a, b):
		CHUNK_SIZE = 24
		bytes_read = 0
		while True:
			chunk_a = a.read(CHUNK_SIZE)
			chunk_b = b.read(CHUNK_SIZE)
			if chunk_a != chunk_b:
				self.fail(
					"Chunks starting at %d do not match. a = %s. b = %s." % (
						repr(chunk_a), repr(chunk_b))
				)
			elif len(chunk_a) == 0:
				break

	def test_get_file_simple(self):
		con = httplib.HTTPConnection(self.listen_on[0], self.listen_on[1],
			timeout = 5)
		for i in self.test_files:
			retrieved_file = gicore.filetransfer._get_file_simple(
				con = con,
				path = "/" + i,
				max_size = int(os.environ.get("FILE_SIZE", 2048)) + 256
			)

			# Check permissions
			stat_results = os.lstat(retrieved_file)
			mode = stat_results.st_mode
			self.assertTrue(stat.S_ISREG(mode)) # regular file
			self.assertFalse(stat.S_ISLNK(mode)) # not a symlink
			self.assertEquals(0400, stat.S_IMODE(mode)) # permissions
			self.assertEquals(os.geteuid(), stat_results.st_uid)
			self.assertEquals(os.getegid(), stat_results.st_gid)

			# Check equality to original file
			with open(os.path.join(self.temp_dir, i), "rb") as original:
				with open(retrieved_file, "rb") as received:
					self.compare_files(original, received)

	def test_get_file(self):
		for i in self.test_files:
			try:
				gicore.filetransfer.get_file(
					server = "%s:%d" % self.listen_on,
					path = "/" + i,
					pub_key = self.key,
					timeout = 5,
					max_size = int(os.environ.get("FILE_SIZE", 2048)) + 256
				)
			except gicore.errors.VerificationError as e:
				self.fail("Validation failed on valid file: %s" % (str(e), ))

if __name__ == "__main__":
    unittest.main()
