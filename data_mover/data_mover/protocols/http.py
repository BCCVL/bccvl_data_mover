import io
import logging
import mimetypes
import os
import requests
import zlib

_logger = logging.getLogger(__name__)


def http_get(url, dest_dir, dest_filename, dest_filename_suffix=None):
    """
    Performs a HTTP-GET on the provided url, saving content to a file specified.
    @param url: The URL to download
    @type url: str
    @param dest_dir: The local directory to store the obtained content.
    @type dest_dir: str
    @param dest_filename: The name of the file to store the content in.
    @type dest_filename: str
    @param dest_filename_suffix: The suffix of the file name will be guessed by the content's mime type. Can be overridden by this argument.
    @type dest_filename_suffix: str
    @return: True if the GET was successful and the content was written to disk, FALSE otherwise.
    """
    content, content_type = _inner_http_get(url)
    if content is None or not content:
        return False

    file_suffix = _guess_file_suffix(content_type, dest_filename_suffix)
    _write_content_to_file(content, dest_dir, dest_filename, file_suffix)

    return True


def http_get_gunzip(url, dest_dir, dest_filename, dest_filename_suffix=None):
    """
    Performs a HTTP-GET on the provided url and performs a gunzip on the content.
    @param url: The URL to download and gunzip
    @type url: str
    @param dest_dir: The local directory to store the obtained content.
    @type dest_dir: str
    @param dest_filename: The name of the file to store the content in.
    @type dest_filename: str
    @param dest_filename_suffix: The suffix of the file name will be guessed by the content's mime type. Can be overridden by this argument.
    @type dest_filename_suffix: str
    @return: True if the GET was successful and the content was written to disk, FALSE otherwise.
    """
    raw_content, content_type = _inner_http_get(url)
    if raw_content is None:
        return False

    # Decompress content
    decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
    decompressed_content = decompressor.decompress(raw_content)

    if decompressed_content is None or not decompressed_content:
        return False

    file_suffix = _guess_file_suffix(content_type, dest_filename_suffix)
    _write_content_to_file(decompressed_content, dest_dir, dest_filename, file_suffix)

    return True


def _inner_http_get(url):
    """
    Performs the actual HTTP-GET and returns the content and the content type.
    @param url: The URL to GET
    @return: Content and Content Type or None if unsuccessful
    """
    _logger.info('Performing HTTP GET to URL %s', url)
    try:
        response = requests.get(url, verify=False, timeout=180)
    except requests.Timeout:
        _logger.warning('URL %s timed out', url)
        return None, None

    if response.status_code is not 200:
        _logger.warning('Obtained status code %s from URL %s', response.status_code, url)
        return None, None
    content = response.content
    if content is None:
        return None, None

    return content, response.headers['content-type']


def _guess_file_suffix(content_type, suffix=None):
    """
    Guesses the suffix of a file based on its content_type.
    @param content_type: The content type of a file
    @type content_type: str
    @param suffix: The suffix to use (instead of guessing)
    @type suffix: str
    @return: The suffix, or 'raw' if it could not be guessed.
    """
    if suffix is not None:
        return suffix

    file_suffix = mimetypes.guess_extension(content_type.split(';')[0], False)
    if file_suffix is None:
        file_suffix = "raw"
    elif file_suffix[0] is '.':
        # Strip the leading '.'
        file_suffix = file_suffix[1:]
    return file_suffix


def _write_content_to_file(content, dest_dir, dest_filename, dest_filename_suffix):
    """
    Writes content to a file
    @param content: The content to write to the file
    @type content:
    @param dest_dir: The directory to write the file in.
    @type dest_dir: str
    @param dest_filename: The name of the file to write.
    @type dest_filename: str
    @param dest_filename_suffix: The suffix of the file to write.
    @type dest_filename_suffix: str
    """
    out_file = os.path.join(dest_dir, dest_filename + '.' + dest_filename_suffix)
    f = io.open(out_file, mode='wb')
    f.write(content)
    f.close()
