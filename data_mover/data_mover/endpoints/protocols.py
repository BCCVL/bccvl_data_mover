import logging
import requests
import zlib

_logger = logging.getLogger(__name__)


def http_get(url):
    """
    Performs a HTTP-GET on the provided url, returning the raw content or None if there was a problem connecting/downloading.

    :param url: The URL to download
    :return: The content of the response, or None if the HTTP GET did not succeed.
    """

    response = requests.get(url)
    if response.status_code is not 200:
        _logger.warning('Obtained status code %s from URL %s', response.status_code, url)
        return None
    return response.content


def http_get_gunzip(url):
    """
    Performs a HTTP-GET on the provided url and performs a gunzip on the content.

    :param url: The URL to download and gunzip
    :return: The gunzipped content of the response, or None if the HTTP GET did not succeed.
    """
    raw_content = http_get(url)
    if raw_content is None:
        return None
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    decompressed_content = decompressor.decompress(raw_content)
    return decompressed_content