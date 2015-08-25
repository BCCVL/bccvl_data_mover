import logging
from urlparse import urlparse
from data_mover.protocols.swift_client import swift_put, swift_get

class SwiftService():
    """
    SwiftService used to interface with Nectar Object data store
    """

    _logger = logging.getLogger(__name__)

    def __init__(self):
        # openstack credential and password for Nectar swift service
        self._authurl = None
        self._authver = None
        self._tenant = None
        self._user = None
        self._key = None
        
    def configure(self, settings, key):
        """
        Configures the Swift Service
        @param settings: The settings to configure with
        @type settings: dict
        @param key: The key to use when extracting settings from the dictionary
        @type key: str
        """
        self._authurl = settings[key + 'nectar.auth_url']
        self._authver = settings[key + 'nectar.auth_version']
        self._tenant = settings[key + 'nectar.tenant_name']
        self._user = settings[key + 'nectar.user']
        self._key = settings[key + 'nectar.key']
            
    def download_from_swift(self, swift_url, local_dest_dir):
        """
        Download files from a remote SWIFT source
        @param swift_url: The full SWIFT path to download from.
        @type swift_url: str
        @param local_dest_dir: The local directory to store the files in (before they are sent to the destination)
        @type local_dest_dir: str
        @return: True if download is successful. Otherwise False.
        """        
        if not self.has_credential():
            self._logger.error('Credential for Nectar swift service is not configured.')
            return False
        
        # swift url: swift://nectar/my-container/path/to/file
        path_tokens = urlparse(swift_url).path.split('/', 2)        
        container = path_tokens[1]
        src_path = path_tokens[2]
        return swift_get(self._authurl, self._user, self._key, self._tenant, self._authver, src_path, local_dest_dir, container)

    def has_credential(self):
        return self._authurl and self._authver and self._tenant and self._user and self._key
        
    def upload_to_swift(self, local_src_path, dest_path):
        """
        Upload file to a remote SWIFT store
        @param local_src_path: The full source path to upload from.
        @type local_src_path: str
        @param dest_path: The swift destination to upload the file at the remore machine
        @type dest_path: str
        @return: True if upload is successful. Otherwise False.
        """
        path_tokens = dest_path.split('/', 2)  
        container = path_tokens[1]
        dest_path = path_tokens[2]
        return swift_put(self._authurl, self._user, self._key, self._tenant, self._authver, local_src_path, dest_path, container)