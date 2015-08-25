import logging
import os
import pwd
import swiftclient

_logger = logging.getLogger(__name__)

def swift_put(authurl, user, key, tenant_name, auth_version, src_path, dest_path, container):
    """
	Uses the swift protocol to put a file on a remote host
	@param authurl: authentication URL
	@type authurl: str
    @param user: user name to authenticate as
	@type user: str
	@param key: key to authenticate with
	@type key: str
	@param tenant_name: The tenant/account name, required when connecting to an auth 2.0 system
	@type tenant_name: str
    @param auth_version: OpenStack auth version
	@type auth_version: int
    @param src_path: The source file's path
	@type src_path: str
	@param dest_path: The destination file's path
	@type dest_path: str
	@param container: The destination container at swift remote host
	@type container: str
	"""
    try:
		conn = swiftclient.Connection(authurl=authurl, user=user, key=key, tenant_name=tenant_name, auth_version=auth_version)
		
		# Create the container if not already exists
		conn.put_container(container)
		with open(src_path, 'rb') as infile:
			conn.put_object(container, dest_path.strip('/'), infile.read())
    except Exception as e:
		_logger.exception("Could not swift upload file %s to destination (%s) %s as user %s, tenant %s", src_path, container, dest_path, user, tenant_name)
		return False
    return True

def swift_get(authurl, user, key, tenant_name, auth_version, src_path, dest_path, container):
	"""
	Uses the swift protocol to get a file from a remote host
	@param authurl: authentication URL
	@type authurl: str
    @param user: user name to authenticate as
	@type user: str
	@param key: key to authenticate with
	@type key: str
	@param tenant_name: The tenant/account name, required when connecting to an auth 2.0 system
	@type tenant_name: str
    @param auth_version: OpenStack auth version
	@type auth_version: int
	@param src_path: The full path of the file to transfer from the source machine.
	@type src_path: str
	@param dest_path: The localpath in which to receive files
	@type dest_path: str
	@param container: The container at swift remote host
	@type container: str
	"""
	
	try:
		conn = swiftclient.Connection(authurl=authurl, user=user, key=key, tenant_name=tenant_name, auth_version=auth_version)
        		
		result = conn.get_object(container, src_path)
		with open(dest_path, 'wb') as outfile:
			outfile.write(result[1])
	except Exception as e:
		_logger.exception("Could not swift download file %s from source (%s) %s as user %s, tenant %s", src_path, container, dest_path, user, tenant_name)
		return False
	return True