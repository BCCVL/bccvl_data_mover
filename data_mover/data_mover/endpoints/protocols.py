import logging
import requests

_logger = logging.getLogger(__name__)

def http_get(url):
    """
    Performs a HTTP-GET on the provided url, returning the raw content or None if there was a problem connecting/downloading.

    :param url: The URL to download
    """

    response = requests.get(url)
    if response.status_code is not 200:
        _logger.info('Obtained status code %s from URL %s', response.status_code, url)
        return None

    return response.content
