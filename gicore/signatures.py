"""
All files pulled over the Internet by the installer have signatures associated
with them. These signatures are generated in accordance with RSASSA-PSS as
defined in [RFC3447](http://www.ietf.org/rfc/rfc3447.txt) (page 29), and the
implementation provided by PyCrypto is used. For some high-level analysis of
the RSASSA-PSS algorithm, see [this paper](http://rsapss.hboeck.de/rsapss.pdf).

All files should be verified against the provided signature and a trusted
public key (distributed with the installer). The hash algorithm used is
`SHA-512` (as implemented by PyCrypto).

"""

# pycrypto
import Crypto.Hash
import Crypto.Signature
import Crypto.PublicKey

def hash_file_sha512(the_file):
	CHUNK_SIZE = 1024
	file_hash = Crypto.Hash.SHA512.new()
	while True:
		chunk = the_file.read(1024)
		if len(chunk) == 0:
			break
		file_hash.update(chunk)
	return the_file

def verify_file(the_file, signature_file, pub_key_file):
	"""
	Verifies that a file and signature file pair are valid and signed with the
	appropriate public key.

	The public key to use is determined by `gicore/PUB_KEY_PATH`. If the
	signature does not correctly sign the file, or if the signature was signed
	with a private key that does not match the configured public key, the
	function will return `False`, otherwise `True` is returned.

	:param the_file: A file object to check.
	:param signature_file: A file object containing the signature file.
	:param pub_key_file: A file object containing the public key to verify
			with.

	:returns: `True` if the verification was succesful, `False` otherwise.

	"""

	# pub_key_path = config.get("gicore/PUB_KEY_PATH")
	# if pub_key_path != None:
	# 	with open(pub_key_path, "rb") as f:
	# 		pub_key_raw = f.read()
	# else:
	# 	pub_key_raw = pkg_resources.resource_string(
	# 		"gicore", "gg-release-key.pub.der")

	pub_key = Crypto.PublicKey.RSA.importKey(pub_key_file.read())
	verifier = Crypto.Signature.PKCS1_PSS.new(pub_key)
	file_hash = hash_file_sha512(the_file)
	signature = signature_file.read()
	return verifier.verify(file_hash, signature)

def sign_file(the_file, private_key_file):
	private_key = Crypto.PublicKey.RSA.importKey(private_key_file.read())
	signer = Crypto.Signature.PKCS1_PSS.new(private_key)
	file_hash = hash_file_sha512(the_file)
	return signer.sign(file_hash)