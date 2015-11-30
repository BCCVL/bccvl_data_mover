import os
import datetime
import logging
from urlparse import urlparse
from org.bccvl import movelib
from org.bccvl.movelib.utils import build_source, build_destination
from data_mover.move_job import MoveJob


class MoveService():
    """
    Service used to move data between endpoints
    """

    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._config = {}

    def configure(self, settings):
        # setting for swift
        for env in ('auth_url', 'tenant_name', 'tenant_id', 'user', 'key'):
            envkey = 'NECTAR_' + env.upper()
            setkey = 'swift_service.nectar.' + env
            if not settings.get(setkey):
                if os.environ.get(envkey):
                    settings[setkey] = os.environ[envkey]
        self._config['swift'] = {
            'os_auth_url': settings['swift_service.nectar.auth_url'],
            'os_auth_version': str(settings['swift_service.nectar.auth_version']),
            'os_auth_tenant_name': settings['swift_service.nectar.tenant_name'],
            'os_auth_username': settings['swift_service.nectar.user'],
            'os_auth_password': settings['swift_service.nectar.key']
        }
        self._config['cookie'] = {
            'secret': settings.get('authtkt.cookie.secret'),
            'domain': settings.get('authtkt.cookie.domain'),
            'name': settings.get('authtkt.cookie.name')
        }

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
            if dest_url.scheme in ('swift+http', 'swift+https') and not self._has_credential():
                raise Exception('Credential for Nectar swift service is not configured.')

            # Download all the files from the sources to the destination
            destination = build_destination(move_job.destination, self._config)

            for s in sourcelist:
                source = build_source(s, move_job.userid, self._config)
                movelib.move(source, destination)
            move_job.update(status=MoveJob.STATUS_COMPLETE, start_timestamp=datetime.datetime.now())
        except Exception as e:
            # catch any Exception here so that we can properly update the job state
            reason = 'Move has failed for job with id {0}. Reason: {1}'.format(move_job.id, str(e))
            self._logger.warning(reason)
            move_job.update(status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason=reason)

    def _has_credential(self):
        return self._authurl and self._authver and self._tenant and self._user and self._key
