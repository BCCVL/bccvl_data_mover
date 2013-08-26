import unittest
from data_mover.models.job import Job
from data_mover.models.protocol import Protocol
from data_mover.models.host import Host


class TestModels(unittest.TestCase):

    def testJobModel(self):
        theType = 'someType'
        data_id = 7
        destination = 'someDestination'
        job = Job(theType, data_id, destination)
        self.assertEqual(theType, job.type)
        self.assertEqual(data_id, job.data_id)
        self.assertEquals(destination, job.destination)
        self.assertEquals(Job.STATUS_PENDING, job.status)
        self.assertIsNone(job.start_timestamp)
        self.assertIsNone(job.end_timestamp)
        self.assertEqual('sample/sample_source', job.source)

    def testProtocolModel(self):
        name = 'RCP'
        command = 'rcp'
        options = '-x -t -z'
        protocol = Protocol(name, command, options)
        self.assertEqual(name, protocol.name)
        self.assertEqual(command, protocol.command)
        self.assertEqual(options, protocol.options)

    def testHostModel(self):
        name = 'someHost'
        server = '192.168.0.1'
        protocol = Protocol('SCP', 'scp', '')
        user = 'admin'
        password = 'myPass'
        host = Host(name, server, protocol, user, password)
        self.assertEqual(name, host.name)
        self.assertEquals(server, host.server)
        self.assertEquals(protocol, host.protocol)
        self.assertEquals(user, host.user)
        self.assertEquals(password, host.password)
