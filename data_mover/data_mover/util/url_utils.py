import urllib
import urllib2
import urlparse


def path_to_url(path):
    """
    Converts a local file system path to a file:// URL
    @param path: The local file system path to convert
    @type path: str
    @rtype: str
    """
    return urlparse.urljoin("file:", urllib.pathname2url(path))

def url_to_path(url):
    """
    Converts a file:// URL to a local file system path
    @param url: The URL to convert to a local file system path
    @type url: str
    @rtype: str
    """
    return urllib2.unquote(urlparse.urlparse(url).path)