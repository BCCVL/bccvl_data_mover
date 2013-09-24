Data Mover API for BCCVL
================
The Data Mover is a component in the system responsible for moving files around. It should have a "registry" of destinations where it can move files to, which contains configuration about the location of the destination, credentials to access the destination and file transmission protocol details.
One of these destinations should be the visualizer, since it needs datasets in order to render map visualizations to be displayed on the front-end.
The component requesting the data of the data mover should be responsible for telling the data mover which directory/location it wants the file to be placed.
The data mover shall be listening for inbound requests via an XML-RPC based API.
The data mover shall be asynchronous. When a request to move a file is made via the XML-RPC API, it shall initially validate the move request and respond with a unique "job id" that can be used later to query the status of the move (since large files can potentially take time to be copied to destinations). This can be used by clients to ensure the file has been successfully transmitted before using the file for processing.

### Developer Setup

    $ git clone https://github.com/BCCVL/bccvl_data_mover.git
    $ cd bccvl_data_mover/data_mover
    $ virtualenv .
    $ source bin/activate

    # if you have an old virtualenv - note, it should always be safe to run this
    $ pip install distribute --upgrade

    $ python bootstrap.py
    $ ./bin/buildout


**Configuration File**

You will need to configure the development.ini file.
Make sure that you have the follow (or similar):

    sqlalchemy.url = postgresql+psycopg2://data_mover:data_mover@localhost:5432/data_mover
    file_manager.data_directory = sample
    file_manager.ala_data_directory = sample/ALA

    ala_service.sleep_time = 10

**Initializing the database**

You will need to create:
* database user: data_mover (with password data_mover)
* database: data_mover (owner is data_mover)

Then run:

    $ ./bin/initialize_data_mover_db development.ini

**Start server**

    $ ./bin/pserve development.ini

**On update**

    $ ./bin/buildout
    $ ./bin/initialize_data_mover_db development.ini

**How to test XMLRPC (Python)**

    from xmlrpclib import ServerProxy
    s = ServerProxy('http://0.0.0.0:6543/data_mover')
    lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
    s.pullOccurrenceFromALA(lsid)

**Available XMLRPC functions**

* pullOccurrenceFromALA(String lsid)
* checkALAJobStatus(int job_id)
