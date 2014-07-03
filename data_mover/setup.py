import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'zope.sqlalchemy',
    'pyramid_xmlrpc',
    'PyYAML',
    'requests',
    'paramiko',
    'scp',
    'futures',
    ]


extras_require = {
    'test': [
        'pyramid_debugtoolbar',
        'coverage',
        'nose',
        'test',
        'mock',
        'behave',
        'epydoc',
        ],
    'pysqlite': [
        'pysqlite']
    }


setup(name='data_mover',
      version='0.5.2-dev',
      description='data_mover',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='data_mover',
      install_requires=requires,
      extras_require=extras_require,
      entry_points="""\
      [paste.app_factory]
      main = data_mover:main
      [console_scripts]
      initialize_data_mover_db = data_mover.scripts.initializedb:main
      """,
      )
