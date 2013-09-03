import io
import logging
import urllib2


def http_get(url, localFile):
    logging.info('Downloading from %s to %s', url, localFile)
    source = urllib2.urlopen(url)
    destination = io.open(localFile, 'w')
    destination.write(source.read())
    destination.close()


