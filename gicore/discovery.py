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

import config

_DISCOVERY_PROTOCOL_VERSION = 1
"""The version of the discovery protocol we're using."""

_MAX_REQUEST_SIZE = 5000
"""The maximum size of a discovery request in bytes."""

_MAX_RESPONSE_SIZE = 10000
"""The maximum size of a discovery response in bytes."""

def get_endpoint():
	"""
	Returns the location and port of the Galah Group endpoint we will
	access when discovering software in a tuple `(HOST, PORT)`.

	"""

	return config.get("gicore/DISCOVERY_ENDPOINT")

def discover(software_list):
	log.info(
		"Connecting to discovery endpoint at %s on port %d",
		endpoint[0],
		endpoint[1]
	)
	ssl_socket = _connect(get_endpoint())

	request = _form_request(software_list)
	log.debug("Sending request: %s", request)
	ssl_socket.sendall(request)

	log.info("Waiting for discovery response from server.")

	# The first part of the response, up to a comma, is the number of
	# bytes that will be in the payload.
	import StringIO
	import select
	response = StringIO.StringIO()
	timeout = utils.timeout(_RESPONSE_TIMEOUT)
	while ("," not in response.getvalue() and
			len(response.getvalue()) < _MAX_RESPONSE_SIZE and
			timeout.isdone()):
		response.write(str(ssl_socket.recv(_MAX_RESPONSE_SIZE)))

def _connect(endpoint):
	"""
	Connects to the Galah Group endpoint and returns a SSL Socket.

	:param endpoint: The endpoint to connect to in a tuple `(HOST, PORT)`.

	"""

	import socket
	raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	import ssl
	ssl_socket = ssl.wrap_socket(
		raw_socket,
		ssl_version = ssl.SSLv3,
		cert_reqs = CERT_REQUIRE
	)
	ssl_socket.connect(get_endpoint())

	return ssl_socket

def _form_request(software_list):
	"""
	Forms a discovery request through an SSL Socket for the software in
	`software_list`.

	"""

	payload = []
	for i in software_list:
		payload.append({
			"software": str(i.software),
			"version": str(i.version)
		})

	import utils
	json = utils.json_module()
	payload_text = str(json.dumps(payload))

	request = "%s,%s,%s" % (
		str(_DISCOVERY_PROTOCOL_VERSION),
		len(payload_text)
		str(payload_text)
	)

	return str(request)
