import io
import logging
import requests


def http_get(url, localFile):
    logging.info('Downloading from %s to %s', url, localFile)
    request = requests.get(url)
    # TODO: Check response code is a 200 before writing
    outFile = io.open(localFile, 'wb')
    outFile.write(request.content)



