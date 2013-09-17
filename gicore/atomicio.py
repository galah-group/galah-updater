# stdlib
import tempfile
import os
import stat

def check_filesystems(path_a, path_b):
    """
    Determines if two files are on the same filesystem.

    :param path_a: The path to the first file.
    :param path_b: The path to the second file. If this file does not exist,
            then `os.path.dirname(path_b)` will be checked instead (which will
            be the filesystem that the file will be on when it is created).

    """

    dev_a = os.lstat(path_a).st_dev
    try:
        dev_b = os.lstat(path_b).st_dev
    except OSError:
        deb_b = os.lstat(os.path.dirname(path_b)).st_dev
    return dev_a == dev_b

def safe_mkstemp(dir, mode, suffix = ".atomicproxy"):
    """
    Creates a temporary file in the given directory as safely as possible.

    If an exception occurs for whatever reason, the file will be destroyed and
    the exception reraised.

    :param dir: The directory to create the temporary file in.
    :param mode: The mode to open the temporary file with (as given to
            `open()`).

    :returns: An open file object.

    """

    os_handle, path = tempfile.mkstemp(dir = dir, prefix = prefix)
    f = None
    try:
        f = os.fdopen(os_handle, mode)
    except:
        # f could be none if the call to fdopen raises an exception.
        if f is None:
            os.close(os_handle)
        else:
            f.close()
        os.remove(path)
        raise
    return f

class AtomicFile:
    supported_modes = ["wb", "w"]

    def __init__(self, path, mode):
        if mode not in supported_modes:
            raise NotImplemented("mode must be one of %s" %
                (str(supported_modes), ))

        self.path = path
        self.mode = mode

        try:
            # This is more of a convenience check and can be defeated by
            # various potential race conditions.
            if stat.S_ISLNK(os.lstat(path).st_mode):
                raise ValueError("path may not be a symlink.")
        except OSError:
            # If file doesn't exist yet
            pass

        self.proxy = self._create_proxy()
        self._check_filesystems()

    def _create_proxy(self):
        try:
            # Try making the proxy in the same directory as the file
            return safe_mkstemp(os.path.dirname(self.path), self.mode)
        except IOError:
            # If that fails, try to make it in the default temp directory
            return safe_mkstemp(None, mode)

    def _check_filesystems(self):
        if not check_filesystems(self.proxy.name, self.path):
            raise RuntimeError(
                "proxy file and original file are not on same filesystem. "
                "Cannot guarentee atomic renames."
            )

    def fileno(self):
        return self.proxy.fileno()

    def flush(self):
        self.proxy.flush()
        os.fsync(self.proxy.fileno())
        self.proxy.close()

        self._check_filesystems()
        os.rename(self.proxy.name, self.path)

        self.proxy = None
        self._create_proxy()

    def read(self, *args, **kwargs):
        raise NotImplemented()

    def write(self, data):
