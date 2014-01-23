import unittest

from data_mover.destinations.destination_manager import *
from os.path import dirname


class TestDestinationManager(unittest.TestCase):

    def test_get_destination_by_name(self):
        to_test = DestinationManager()

        file_to_load = os.path.join(dirname(dirname(dirname(__file__))), 'data_mover', 'destination_config_test.json')
        settings = {'key.destinations': file_to_load}
        to_test.configure(settings, 'key.')

        visualiser = to_test.get_destination_by_name('visualiser')
        self.assertIsNotNone(visualiser)
        self.assertIsNotNone(visualiser['description'])
        self.assertIsNotNone(visualiser['ip-address'])
        self.assertIsNotNone(visualiser['protocol'])
        self.assertIsNotNone(visualiser['authentication'])
        self.assertIsNone(to_test.get_destination_by_name('some_bad_destination'))
