# Discovery Protocol version 1

The installer uses a very simple protocol for requesting the location of
software packages. It is an ASCII-text-based protocol that runs over SSL
over TCP/IP.

This protocol aims to be as simple to implement securely as possible.

## Initiating a Request

In order to initiate a request, the client opens up an SSL connection with
the server. The client MUST verify the server's certificate. It SHOULD do
this by comparing the server's certificate for *equality* with a known,
trusted certificate. Certificate chains should not be used, nor should
certificate authorities.

If the client deems that the server's certificate is not trusted, it MUST
alert the user and close the connection immediately.

Once a secure connection is established and the authenticity of the server
is verified, the client MUST send a message of the following form

*protocol_version*,*payload_size*,*payload*

The *protocol_version* MUST be a positive integer (encoded in ASCII, ex: 12)
denoting the version of the protocol. If conforming to this document, this
number MUST be `1`.

The *payload_size* MUST be a positive integer (encoded in ASCII like the
*protocol_version*) that corresponds to the number of bytes present in the
*payload*.

Note that there are no spaces permitted in the *protocol_version* and
*payload_size* sections. The regular expression `[0-9]+,[0-9]+,` MUST match
the message up to the start of the *payload* field.

The *payload* MUST be a JSON list of objects each with the fields *software*
and *version*. The JSON object MUST be exactly *payload_size* bytes large,
and the entirety of it MUST be valid JSON. The client MUST NOT add any other
fields to the objects in the list, and the client MUST NOT omit any of the
fields specified.

The *software* field corresponds to the name of the software the client wishes
to discover the URI for, and the *version* corresponds to the version of the
software to discover the URI for. *version* may have the value `LATEST` in
order to ask for the most recent version of the software.

## Responding to a Request

The server MUST wait for a request to be made before sending any data over an
established connection. The server SHOULD timeout after an appropriate amount
of time (recommend 10 seconds) has passed without new client data being
received. The server SHOULD timeout if a particular connection is open for
too long (recommend 30 seconds). The server SHOULD close a connection if the
size of a request is larger than 5000 bytes. These measures are an attempt to
prevent accidental denial of service attacks due to malfunctioning clients.

Upon reception of a request, the server should respond with a message of the
form

*payload_size*,*payload*

The *payload_size* MUST be a positive integer (encoded in ASCII like the
*payload_size* field of a request) that corresponds to the number of bytes
present in the *payload*.

The *payload* MUST be a JSON list of objects such that the first object in the
list is a response to the first object in the request's list, etc. Each object
MUST have the fields *software*, *version*, and *uri*.

The *software* field MUST exactly match the software field of the object in
the request that the object is associated with. The *version* field is the
version of the software that *uri* points at and should match the request's
object unless the request's object was `LATEST`.

If a matching URI could not be found that satisfies the client's request, the
server MUST return an object with the *version* and *uri* fields set to the
JSON value `null`.

If the client sends a poorly formed request, or the connection times out and
the server wishes to cut the connection, an error response should be sent,
which is of similar form to a typical response, except the the *payload* MUST
be a JSON object with a single field *error_string*. The *error_string* SHOULD
only have one of two values: `"TIMEOUT"` or `"BAD REQUEST"`.
