import subprocess

# TODO CHECK IF FILES ARE TRANSFERRED PROPERLY/COMPLETELY

def scp_from(host, source, destination):
	try:
		remote_location = "%s@%s:%s" % (host.user, host.server, source)
		destination_path = "./%s" % (destination)
		subprocess.call(['scp', '-r', remote_location, destination_path])
	except:
		return False
	return True

def scp_to(host, source, destination):
	try:
		remote_location = "%s@%s:%s" % (host.user, host.server, destination)
		source_path = "./%s" % (source)
		subprocess.call(['scp', '-r', source_path, remote_location])
	except:
		return False
	return True