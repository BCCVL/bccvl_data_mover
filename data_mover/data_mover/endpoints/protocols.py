import io
import logging
import requests


def http_get(url):
    logging.info('Downloading from %s', url)
    request = requests.get(url)
    return request.content



