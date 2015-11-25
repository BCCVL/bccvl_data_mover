import os
import datetime
import logging
import sys
from urlparse import urlparse
from org.bccvl import movelib
from data_mover.move_job import MoveJob
from data_mover.utils import build_source, build_destination


class MoveService():
    """
    Service used to move data between endpoints
    """

    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._authurl = None
        self._authver = None
        self._tenant = None
        self._user = None
        self._key = None


    def configure(self, settings):
        # setting for swift
        for env in ('auth_url', 'tenant_name', 'tenant_id', 'user', 'key'):
            envkey = 'NECTAR_' + env.upper()
            setkey = 'swift_service.nectar.' + env
            if not settings.get(setkey):
                if os.environ.get(envkey):
                    settings[setkey] = os.environ[envkey]
        self._authurl = settings['swift_service.nectar.auth_url']
        self._authver = str(settings['swift_service.nectar.auth_version'])
        self._tenant = settings['swift_service.nectar.tenant_name']
        self._user = settings['swift_service.nectar.user']
        self._key = settings['swift_service.nectar.key']

        # plone secret for cookie
        if 'plone.cookie_secret' in settings:
            self._cookie_secret = settings['plone.cookie_secret']

    def worker(self, move_job):
        """
        Thread worker used to perform a move of data between endpoints.
        @param move_job: The move job to execute
        @type move_job: MoveJob
        """
        try:
            # Need o handle a list of sources
            self._logger.info("Starting move for job with id %s", move_job.id)
            move_job.update(status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=datetime.datetime.now())

            # source can be just 1 source or a list of sources
            if isinstance(move_job.source, str):
                sourcelist = [move_job.source]
            elif isinstance(move_job.source, list):
                sourcelist = move_job.source
            else:
                raise Exception('Invalid source {1}'.format(move_job.source))

            # Validate the destination url
            dest_url = urlparse(move_job.destination)
            if dest_url.scheme == 'swift' and not self._has_credential():
                raise Exception('Credential for Nectar swift service is not configured.')

            # Download all the files from the sources to the destination
            swift_settings = {'auth': self._authurl, 'user': self._user, 'key': self._key, 'os_tenant_name': self._tenant, 'auth_version': self._authver}
            destination = build_destination(move_job.destination, **swift_settings)
            for s in sourcelist:
                source = build_source(s, userid=move_job.userid, secret=self._cookie_secret, **swift_settings)
                print "source = ", source, destination
                movelib.move(source, destination)
            move_job.update(status=MoveJob.STATUS_COMPLETE, start_timestamp=datetime.datetime.now())
        except Exception as e:
            # catch any Exception here so that we can properly update the job state
            reason = 'Move has failed for job with id {0}. Reason: {1}'.format(move_job.id, str(e))
            self._logger.warning(reason)
            move_job.update(status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason=reason)
    
    def _has_credential(self):
        return self._authurl and self._authver and self._tenant and self._user and self._key
