import os
import json


class DestinationManager():
    """
    Manages the configuration of destinations
    """

    def __init__(self):
        """
        Constructor
        """
        self.destinations = None

    def configure(self, settings, key):
        fp = os.path.abspath(settings[key + 'destinations'])
        self.destinations = json.load(open(fp))


    def get_destination_by_name(self, name):
        """
        Obtains a destination given its name
        @param name: The name of the destination to lookup
        @return: The details of the destination, or None if there is no such destination configured
        """
        for dest in self.destinations:
            if name in dest:
                return dest[name]
        return None