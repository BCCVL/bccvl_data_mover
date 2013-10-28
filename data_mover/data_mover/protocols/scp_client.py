import logging
import os
import pwd
from paramiko import SSHClient
from scp import SCPClient

_logger = logging.getLogger(__name__)


def scp_put(host, username, source_file, destination_path):
    """
    Uses the SCP protocol to put a file on a remote host
    @param host: The ip-address (or hostname) of the destination machine.
    @type host: str
    @param username: The username to use when making a connection to the destination machine. If empty, it will use the current username (on the local machine)
    @type username: str
    @param source_file: The full path of the file to transfer to the destination machine.
    @type source_file: str
    @param destination_path: The full path of the directory to transfer the file to on the destination machine.
    @type destination_path: str
    @return: True if successful
    """
    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()

        # Use the current user if one was not specified
        if not username:
            username = _get_current_username()

        ssh.connect(host, username=username)
        scp = SCPClient(ssh.get_transport())
        scp.put(source_file, destination_path)
    except:
        _logger.exception("Could not SCP file %s to destination %s:%s", source_file, host, destination_path)
        return False
    return True


def _get_current_username():
    """
    @return: The current username
    """
    return pwd.getpwuid(os.getuid())[0]