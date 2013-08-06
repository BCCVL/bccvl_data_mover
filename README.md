bccvl_data_mover
================

Data Mover API for BCCVL

The Data Mover is a component in the system responsible for moving files around. It should have a "registry" of destinations where it can move files to, which contains configuration about the location of the destination, credentials to access the destination and file transmission protocol details.
One of these destinations should be the visualizer, since it needs datasets in order to render map visualizations to be displayed on the front-end.
The component requesting the data of the data mover should be responsible for telling the data mover which directory/location it wants the file to be placed.
The data mover shall be listening for inbound requests via an XML-RPC based API.
The data mover shall be asynchronous. When a request to move a file is made via the XML-RPC API, it shall initially validate the move request and respond with a unique "job id" that can be used later to query the status of the move (since large files can potentially take time to be copied to destinations). This can be used by clients to ensure the file has been successfully transmitted before using the file for processing.

### Developer Setup

    git clone https://github.com/BCCVL/bccvl_data_mover.git
    cd bccvl_data_mover/data_mover
    python bootstrap.py
    ./bin/buildout
    ./bin/initialize_data_mover_db development.ini

**Start server**

    ./bin/pserve development.ini
    
**How to test XMLRPC (Python)**

    from xmlrpclib import ServerProxy
    s = ServerProxy('http://0.0.0.0:6543/data_mover', verbose = 1)
    s.move('DATA_TYPE', 12)
    
