import logging
import transaction


class GenericDAO:

    def __init__(self, session):
        self._logger = logging.getLogger(__name__)
        self._dbSession = session

    def add(self, object):
        try:
            self._dbSession.add(object)
            self._dbSession.flush()
            self._logger.info("Added new job in db with id %s", object.id)
            return object
        except:
            self._logger.exception('Could not create new job in db')
            return None

    def expunge(self, object):
        """
        Removes the object from the current session. This is needed so that the sessions in the other processes can
        access the object without any concurrency issues.
        :param object:
        :return:
        """
        self._dbSession.expunge(object)
        return

    def findById(self, type, id):
        try:
            result = self._dbSession.query(type).get(id)
            return result
        except:
            self._logger.exception('Could not find job in db with id %s', id)
            return None

    def update(self, object):
        try:
            id = object.id
            self._dbSession.add(object)
            transaction.commit()
            return self.findById(type(object), id)
        except:
            self._logger.exception('Could not update object in db')
            return None