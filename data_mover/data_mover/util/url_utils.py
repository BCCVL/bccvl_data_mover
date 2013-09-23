import urllib
import urlparse


def path_to_url(path):
    """
    Converts a local file system path to a file:// URL
    """
    return urlparse.urljoin("file:", urllib.pathname2url(path))