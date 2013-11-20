import os


def create_parent(destination):
    """
    Creates parent directories of the destination path if needed.
    @param destination: the final destination to create parents for
    @type destination: str
    """
    parent = os.path.dirname(destination)
    if not os.path.isdir(parent):
        os.makedirs(parent)


def listdir_fullpath(directory):
    """
    Lists the files in the provided directory using the absolute path to the files.
    @param directory: The directory to list
    @type directory: str
    @return: A list of files in the provided directory, with absolte paths.
    @rtype: list
    """
    return [os.path.join(directory, f) for f in os.listdir(directory)]