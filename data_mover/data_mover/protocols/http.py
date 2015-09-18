import logging
import mimetypes
import os
import shutil
import urllib
import zipfile

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
    temp_file_path, content_type = _inner_http_get(url)
    if temp_file_path is None:
        return False

    if os.path.getsize(temp_file_path) == 0:
        os.remove(temp_file_path)
        return False

    file_suffix = _guess_file_suffix(content_type, dest_filename_suffix)
    out_file_path = os.path.join(dest_dir, dest_filename + '.' + file_suffix)
    shutil.move(temp_file_path, out_file_path)
    return True


def http_get_unzip(url, source_filenames, dest_dir, dest_filenames, dest_file_suffixes):
    """
    Performs a HTTP-GET on the provided URL and expects a zip file in return.
    It will unzip the zip file and will copy source_filenames to the destination directory named dest_filenames
    @param url: The URL to download
    @type url: str
    @param source_filenames: The source filenames to extract
    @type source_filenames: list
    @param dest_dir: The name of the directory to store the retrieved files to.
    @type dest_dir: str
    @param dest_filenames: The dest filenames to write the source files to
    @type dest_filenames: list
    @param dest_file_suffixes: The file suffixes to write the destination filenames with.
    @type dest_file_suffixes: list
    """
    temp_file_path, content_type = _inner_http_get(url)
    if temp_file_path is None:
        return False

    # Decompress content
    success = True
    try:
        with zipfile.ZipFile(temp_file_path) as z:
            for (source, dest, suffix) in zip(source_filenames, dest_filenames, dest_file_suffixes):
                z.getinfo(source)
                z.extract(source, dest_dir)
                file_suffix = _guess_file_suffix(content_type, suffix)
                os.rename(os.path.join(dest_dir, source), os.path.join(dest_dir, dest + '.' + file_suffix))
    except KeyError:
        _logger.error("Cannot find file %s in downloaded zip file", source)
        success = False
    except Exception:
        _logger.error("The file %s is not a zip file", source)
        success = False

    # Remove temp file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    return success


def _inner_http_get(url):
    """
    Performs the actual HTTP-GET and returns the content and the content type.
    @param url: The URL to GET
    @return: Temporary file containing the content and Content Type or (None, None) if unsuccessful
    """
    _logger.info('Performing HTTP GET to URL %s', url)
    try:
        temp_file, headers = urllib.urlretrieve(url)
    except:
        _logger.error('Could not download from url %s', url)
        return None, None
    return temp_file, headers['content-type']


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
