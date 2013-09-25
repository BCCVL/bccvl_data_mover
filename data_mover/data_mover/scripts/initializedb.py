import os
import sys

from sqlalchemy import engine_from_config

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    Base,
    )

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, 'pyramid')
    engine = engine_from_config(settings, 'sqlalchemy.')

    DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.configure(bind=engine)

    # Create all the models
    Base.metadata.create_all(engine)
