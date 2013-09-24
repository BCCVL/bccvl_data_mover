import urllib
import urllib2
import urlparse


def path_to_url(path):
    """
    Converts a local file system path to a file:// URL
    """
    return urlparse.urljoin("file:", urllib.pathname2url(path))

def url_to_path(url):
    """
    Converts a file:// URL to a local file system path
    """
    return urllib2.unquote(urlparse.urlparse(url).path)