import logging
log = logging.getLogger("gi.discovery")

# gicore
import errors
import signatures

# stdlib
import urlparse
import httplib
import tempfile
import os
import pkg_resources
import stat

RSA_KEY_SIZE = 16384
"The number of bits in the RSA keys used in signatures."

def _get_file_simple(con, path, max_size):
	"""
	Performs a simple HTTP GET request to retrieve a particular file and stores
	it in a secure (inaccessible by other users), temporary file.

	:param con: An HTTP connection that is not awaiting a response (so it is
			safe to make a request on it).
	:param path: A path to the file on the server. Should begin with a slash.

	"""

	con.request("GET", path)
	response = con.getresponse()
	if response.status != httplib.OK:
		raise IOError("Server returned %d error code." % (response.status, ))

	os_handle, path = tempfile.mkstemp()
	f = None
	try:
		f = os.fdopen(os_handle, "wb")
		max_file_size = max_size
		bytes_read = 0
		CHUNK_SIZE = 1024
		while True:
			chunk = response.read(CHUNK_SIZE)
			if len(chunk) == 0:
				break
			f.write(chunk)
			bytes_read += len(chunk)
			if bytes_read > max_file_size:
				raise IOError("File exceeds max download size.")
	except:
		os.remove(path)
		raise
	finally:
		# f could be none if the call to fdopen raises an exception.
		if f is None:
			os.close(os_handle)
		else:
			f.close()
	os.chmod(path, stat.S_IRUSR)
	return path

def get_file(server, path, pub_key, timeout, max_size):
	"""
	Securely retrieves a file from the given server.

	The file's origin and integrity is checked, but the transfer of the file is
	not encrypted, thus observers could peek into your traffic and see what is
	being transferred, they would not be able to modify the file or swap it for
	their own however without verification failing.

	:param server: The hostname or IP address of the server. Can contain a port
			number (ex: `localhost:8080`).
	:param path: The path of the file on the server (ex: `/folder/file.json`).
	:param pub_key: The public key to use when verifying the downloaded file as
			a string (`str`).
	:param timeout: The number of seconds to wait for each blocking network
			operation (such as connection or waiting for the next chunk of
			data).
	:param max_size: The maximum size of the file in bytes.

	:raises errors.VerificationError: When the file could not be verified as
			authentic for whatever reason.

	:returns: A path to the downloaded files as a tuple (file, signature).
			Both file's permissions are set to 600 and owned by the current
			user.

	"""

	con = httplib.HTTPConnection(host = server, timeout = timeout)
	file_path = None
	sig_path = None
	try:
		log.info("Getting file '%s'", path)
		file_path = _get_file_simple(con, path, max_size)
		log.info("Getting signature for file '%s'", path)
		try:
			sig_path = _get_file_simple(con, path + ".sig", max_size)
		except IOError:
			# If server returns bad response (ex: 404) we want to consider it
			# a verification error.
			raise errors.VerificationError("%s/%s" % (server, path))

		log.info("Verifying file+signature.")
		# if pub_key_path != None:
		# 	with open(pub_key_path, "rb") as f:
		# 		pub_key_raw = f.read()
		# else:
		# 	pub_key_raw = pkg_resources.resource_string(
		# 		"gicore", "gg-release-key.pub.der")
		verified = signatures.verify_file(
				open(file_path, "rb"), open(sig_path, "rb"), pub_key)
		if not verified:
			raise errors.VerificationError("%s/%s" % (server, path))
	except:
		if file_path is not None:
			try:
				os.remove(file_path)
			except:
				log.exception("Could not delete file %s.", file_path)
		if sig_path is not None:
			try:
				os.remove(sig_path)
			except:
				log.exception("Could not delete signature file %s.", sig_path)
		raise
	finally:
		con.close()

	return file_path, sig_path
