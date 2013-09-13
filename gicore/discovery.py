"""
This module assists with getting the source code of particular versions of
software the installer needs. This is done by hitting a Galah Group endpoint
and asking for where to get the software desired.

We do not hit the end point using an HTTPS request because HTTP provides a lot
of features that we don't need, and the best way to use it would be through a
layer of abstraction like Requests. This is a very security-concious module
thus we want as little abstraction as possible.

In addition, I do not want to use a certificate authority. The installer ships
with a self-signed certificate to compare against the server's and the
server needs to match up exactly to that. This is significantly better than
having to bring in another party.

Thus we use the protocol described under `docs/DiscoveryProtocol.md`.

"""

import logging
log = logging.getlogger("gi.discovery")

# gicore
import config
import errors

# stdlib
import urlparse
import httplib
import tempfile
import os
import pkg_resources

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
		f = os.fdopen(os_handle, mode = "wb")
		chunk_size = chunk_size
		max_file_size = max_size
		bytes_read = 0
		CHUNK_SIZE = 1024
		while True:
			chunk = response.read(1024)
			f.write(chunk)
			bytes_read += chunk_size
			if bytes_read > max_file_size:
				raise IOError("File exceeds max download size.")
		return path
	except:
		os.remove(path)
		raise
	finally:
		# f could be none if the call to fdopen raises an exception.
		if f is None:
			os.close(os_handle)
		else:
			f.close()

def get_file(server, path, timeout, max_size):
	"""
	Securely retrieves a file from the configured discovery server (set by
	`gicore/DISCOVERY_SERVER`).

	The file's origin and integrity is checked, but the transfer of the file is
	not encrypted, thus observers could peek into your traffic and see what is
	being transferred, they would not be able to modify the file or swap it for
	their own however (unless of course they have the release private key).

	:param server: The hostname or IP address of the server.
	:param path: The path of the file on the server (ex: `/folder/file.json`).
	:param timeout: The number of seconds to wait for each blocking network
			operation (such as connection or waiting for the next chunk of
			data).
	:param max_size: The maximum size of the file in bytes.

	:returns: A path to the downloaded files as a tuple (file, signature).
			Both file's permissions are set to 600 and owned by the current
			user.

	"""

	con = httplib.HTTPConnection(host = server, timeout = timeout)
	file_path = None
	sig_path = None
	try:
		log.info("Getting file '%s'", path)
		file_path = get_file_simple(con, path, max_size)
		log.info("Getting signature for file '%s'", path)
		sig_path = get_file_simple(con, path + ".sig", max_size)

		log.info("Verifying file+signature.")
		if not verify_file(file_path, sig_path):
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
