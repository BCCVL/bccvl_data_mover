import logging
import requests

_logger = logging.getLogger(__name__)


def http_get(url):
    """
    Performs a HTTP-GET on the provided url, returning the raw content or None if there was a problem connecting/downloading.

    :param url: The URL to download
    :return: The content of the response, or None if the HTTP GET did not succeed.
    """

    response = requests.get(url)
    if response.status_code is 200:
        return None

    _logger.warning('Obtained status code %s from URL %s', response.status_code, url)
    return response.content
