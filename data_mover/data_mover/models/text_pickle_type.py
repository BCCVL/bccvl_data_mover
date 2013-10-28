from sqlalchemy.types import PickleType, Text


class TextPickleType(PickleType):
    """
    Custom PickleType so we can pickle dict objects as json to the database
    """
    impl = Text
