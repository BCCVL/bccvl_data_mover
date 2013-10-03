from data_mover.destination_config import *


class DestinationManager():
    """
    Manages the configuration of destinations
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def get_destination_by_name(self, name):
        """
        Obtains a destination given its name
        @param name: The name of the destination to lookup
        @return: The details of the destination, or None if there is no such destination configured
        """
        try:
            return destinations[name]
        except KeyError:
            return None