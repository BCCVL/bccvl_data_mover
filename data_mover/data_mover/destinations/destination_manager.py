import os
import json


class DestinationManager():
    """
    Manages the configuration of destinations.
    Destinations are configured in a .json file.
    The location of this .json file is configured in the application's .ini file
    """

    def __init__(self):
        """
        Constructor
        """
        self.destinations = None

    def configure(self, settings, key):
        """
        Configures the Destination Maker
        @param settings: The settings to configure with
        @type settings: dict
        @param key: The key to use when extracting settings from the dictionary
        @type key: str
        """
        fp = os.path.abspath(settings[key + 'destinations'])
        self.destinations = json.load(open(fp))

    def get_destination_by_name(self, name):
        """
        Obtains a destination given its name
        @param name: The name of the destination to lookup
        @type name: str
        @return: The details of the destination, or None if there is no such destination configured
        """
        for dest in self.destinations:
            if name in dest:
                return dest[name]
        return None