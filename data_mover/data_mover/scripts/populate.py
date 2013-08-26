from data_mover.models.protocol import Protocol
from data_mover.models.host import Host


def populate_protocol(dbSession):
    scp = Protocol('SCP', 'scp', '')
    dbSession.add(scp)
    dbSession.flush()
    return


def populate_host(dbSession):
    scpProtocol = dbSession.query(Protocol).filter_by(name='SCP').first()
    bccvl_hpc = Host('BCCVL_HPC', '115.146.85.28', scpProtocol.id, 'ubuntu', 'password')
    dbSession.add(bccvl_hpc)
    dbSession.flush()
    return