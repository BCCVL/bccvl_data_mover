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
