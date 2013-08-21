import subprocess

def scp_from(host, source, destination):
	remote_location = "%s@%s:%s" % (host.user, host.server, source)
	destination_path = "./%s" % (destination)
	try:
		subprocess.call(['scp', '-r', remote_location, destination_path])
	except:
		return False
	return True

def scp_to(host, source, destination):
	remote_location = "%s@%s:%s" % (host.user, host.server, destination)
	source_path = "./%s" % (source)
	print remote_location
	print source_path
	try:
		subprocess.call(['scp', '-r', source_path, remote_location])
	except:
		return False
	return True