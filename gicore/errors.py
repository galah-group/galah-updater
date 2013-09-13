class VerificationError(Exception):
	"""
	The exception raised when a file received over some network fails
	verification.

	"""

	def __init__(self, url, *args, **kwargs):
		"""
		:param url: The URL of the file that failed verification.

		"""

		self.url = url

		Exception.__init__(self, *args, **kwargs)

	def __str__(self):
		return "File at '%s' failed verification." % (self.url, )
