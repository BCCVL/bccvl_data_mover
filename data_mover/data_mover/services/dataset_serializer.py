import json
from data_mover.domain.dataset import Dataset, DatasetFile, DatasetProvenance


def serialize_dataset(dataset):
    """
    Serializes the given dataset to a string
    @param dataset: The dataset to serialize
    @type dataset: Dataset
    @return The serialized dataset
    @rtype: str
    """
    return json.dumps(dataset, indent=2, cls=DatasetEncoder)


class DatasetEncoder(json.JSONEncoder):
    """
    Internal class used to encode the dataset to proper json
    """
    def default(self, obj):
        if not isinstance(obj, Dataset) and not isinstance(obj, DatasetFile) and not isinstance(obj, DatasetProvenance):
            return super(DatasetEncoder, self).default(obj)
        return obj.__dict__
