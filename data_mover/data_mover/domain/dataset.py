

class Dataset():
    """
    A representation of a dataset, that can be serialized and sent to the dataset manager.
    """

    def __init__(self, title, description, num_occurrences, files, provenance):
        """
        Constructor

        :param title: The title of the dataset
        :param description: The description of the dataset
        :param num_occurrences: The number of occurrences in the dataset
        :param files: A list of files that belong to the dataset
        :param provenance: The provenance of the dataset
        """
        self.title = title
        self.description = description
        self.num_occurrences = num_occurrences
        self.files = files
        self.provenance = provenance

    def __eq__(self, other):
        if isinstance(other, Dataset):
            return self.title == other.title and \
                   self.description == other.description and \
                   self.num_occurrences == other.num_occurrences and \
                   self.files == other.files and \
                   self.provenance == other.provenance
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Dataset):
            return self.title != other.title or \
                   self.description != other.description or \
                   self.num_occurrences != other.num_occurrences or \
                   self.files != other.files or \
                   self.provenance != other.provenance
        return NotImplemented


class DatasetFile():
    """
    A representation of a file associated with a dataset
    """
    TYPE_OCCURRENCES = "occurrences"
    TYPE_ATTRIBUTION = "attribution"

    def __init__(self, path, dataset_type, size):
        """
        Constructor

        :param path: The path of the file
        :param dataset_type: The type of the dataset (TYPE_OCCURRENCES, TYPE_ATTRIBUTION etc...)
        """
        self.path = path
        self.dataset_type = dataset_type
        self.size = size

    def __eq__(self, other):
        if isinstance(other, DatasetFile):
            return self.path == other.path and \
                   self.dataset_type == other.dataset_type and \
                   self.size == other.size
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, DatasetFile):
            return self.path != other.path or \
                   self.dataset_type != other.dataset_type or \
                   self.size != other.size
        return NotImplemented


class DatasetProvenance():
    """
    A representation of dataset provenance information
    """
    SOURCE_ALA = "ALA"

    def __init__(self, source, url, source_date):
        """
        Constructor

        :param source: The source of the dataset
        :param url: The URL used to retrieve the dataset
        :param source_date: The date the dataset was retrieved
        """
        self.source = source
        self.url = url
        self.source_date = source_date

    def __eq__(self, other):
        if isinstance(other, DatasetProvenance):
            return self.source == other.source and \
                   self.url == other.url and \
                   self.source_date == other.source_date
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, DatasetProvenance):
            return self.source != other.source or \
                   self.url != other.url or \
                   self.source_date != other.source_date
        return NotImplemented