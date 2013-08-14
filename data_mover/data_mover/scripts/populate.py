from data_mover.models import *

def populate_protocol():
	scp = Protocol('SCP', 'scp', '')
	DBSession.add(scp)
	DBSession.flush()
	return

def populate_host():
	bccvl_hpc = Host('BCCVL_HPC', '115.146.85.28', 2, 'ubuntu', 'password')
	DBSession.add(bccvl_hpc)
	DBSession.flush()
	return