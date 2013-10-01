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

	def __repr__(self):
		return "VerificationError(url = %s)" % (self.url, )

	def __str__(self):
		return "File at '%s' failed verification." % (self.url, )

class CriticalError(Exception):
	"""
	Exception raised when critical assumptions are not met. Human intervention
	nearly always required.

	"""

	def __init__(self, message, *args, **kwargs):
		self.message = message
		Exception.__init__(self, *args, **kwargs)

	def __repr__(self):
		return "CriticalError(%s)" % (message, )

	def __str__(self):
		msg = "A critical error has occurred: %s" % (message, )
		return msg
