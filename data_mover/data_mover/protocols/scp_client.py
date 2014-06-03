import logging
import os
import pwd
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient, SCPException

_logger = logging.getLogger(__name__)

# NOTE: I have tried to refactor this code, but it does not work after refactoring :(

def scp_put(host, username, password, source_path, destination_path):
    """
    Uses the SCP protocol to put a file on a remote host
    @param host: The ip-address (or hostname) of the destination machine.
    @type host: str
    @param username: The username to use when making a connection to the destination machine. If empty, it will use the current username (on the local machine)
    @type username: str
    @param password: The password.
    @type password: str
    @param source_path: The full path of the file to transfer to the destination machine.
    @type source_path: str
    @param destination_path: The full path of the directory to transfer the file to on the destination machine.
    @type destination_path: str
    @return: True if successful
    """
    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(AutoAddPolicy())

        # Use the current user if one was not specified
        if not username:
            username = _get_current_username()

        ssh.connect(host, username=username, password=password)
        scp = SCPClient(ssh.get_transport())
        scp.put(source_path, destination_path, recursive=True)
        ssh.close()
    except:
        _logger.exception("Could not SCP file %s to destination %s on %s as user %s", source_path, destination_path, host, username)
        return False
    return True


def scp_get(host, username, password, source_path, destination_path):
    """
    Uses the SCP protocol to get a file from a remote host
    @param host: The ip-address (or hostname) of the remote machine.
    @type host: str
    @param username: The username to use when making a connection to the remote machine. If empty, it will use the current username (on the local machine)
    @type username: str
    @param password: The password
    @type password: str
    @param source_path: The full path of the file to transfer from the destination machine. Shell wildcards may be used.
    @type source_path: str
    @param destination_path: The local path in which to receive files
    @type destination_path: str
    @return: True if successful
    """
    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(AutoAddPolicy())

        # Use the current user if one was not specified
        if not username:
            username = _get_current_username()

        ssh.connect(host, username=username, password=password)
        scp = SCPClient(ssh.get_transport())
        scp.get(source_path, destination_path, recursive=True)
        ssh.close()
    except SCPException:
        _logger.warning("Could not SCP file %s from %s to local destination %s as user %s", source_path, host, destination_path, username)
        return False
    return True

def _get_current_username():
    """
    @return: The current username
    """
    return pwd.getpwuid(os.getuid())[0]
