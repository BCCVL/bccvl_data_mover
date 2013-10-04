import io
import json
import logging
import os
from data_mover.domain.dataset import *
from data_mover.util.file_utils import *


class DatasetProviderService():

    _logger = logging.getLogger(__name__)

    def __init__(self):
        self.destination_dir = None

    def configure(self, settings, key):
        self.destination_dir = settings[key + 'dest_dir']

    def deliver_dataset(self, dataset):
        """
        Delivers the provided dataset to the dataset manager by writing a file
        @param dataset: The dataset to deliver
        """
        destination = os.path.join(self.destination_dir, dataset.title + ".json")
        create_parent(destination)
        f = io.open(destination, mode='wb')
        json.dump(dataset, f, indent=2, cls=DatasetProviderService.DatasetEncoder)
        f.close()


    class DatasetEncoder(json.JSONEncoder):
        def default(self, obj):
            if not isinstance(obj, Dataset) and not isinstance(obj, DatasetFile) and not isinstance(obj, DatasetProvenance):
                return super(DatasetProviderService.DatasetEncoder, self).default(obj)
            return obj.__dict__


