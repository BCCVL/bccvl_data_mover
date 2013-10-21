import logging
import os
import pwd
from paramiko import SSHClient
from scp import SCPClient

_logger = logging.getLogger(__name__)


def scp_put(host, username, source_file, destination_path):
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
        _logger.exception("Could not SCP file")
        return False
    return True


def _get_current_username():
    return pwd.getpwuid(os.getuid())[0]