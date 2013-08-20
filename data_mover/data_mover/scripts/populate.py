from data_mover.models import *

def populate_protocol():
	scp = Protocol('SCP', 'scp', '')
	DBSession.add(scp)
	DBSession.flush()
	return

def populate_host():
	scpProtocol = DBSession.query(Protocol).filter_by(name='SCP').first()
	bccvl_hpc = Host('BCCVL_HPC', '115.146.85.28', scpProtocol.id, 'ubuntu', 'password')
	DBSession.add(bccvl_hpc)
	DBSession.flush()
	return