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
    $ python bootstrap.py
    $ ./bin/buildout
    $ ./bin/initialize_data_mover_db development.ini

**Start server**

    $ ./bin/pserve development.ini
    
**How to test XMLRPC (Python)**

    from xmlrpclib import ServerProxy
    s = ServerProxy('http://0.0.0.0:6543/data_mover', verbose = 1)
    s.move('DATA_TYPE', 12)
    
## Redis
Redis is an open source, BSD licensed, advanced key-value store. It is often referred to as a data structure server since keys can contain strings, hashes, lists, sets and sorted sets. This is used in conjunction with Resque to store queues in Redis.

**Installation**
Redis version 2.6.13 is contained within the project directory. Go to the project root and in redis directory.

	$ cd <project_root_directory>/redis
	$ tar zxf redis-2.6.13.tar.gz
	$ cd redis-2.6.13
	$ make
	$ sudo make install

Create two directories to store your Redis config files and your data

	$ sudo mkdir /etc/redis
	$ sudo mkdir /var/redis

Copy the init script that you'll find in the Redis distribution under the utils directory into /etc/init.d. We use the name of the port of the running instance of Redis.

	$ sudo cp utils/redis_init_script /etc/init.d/redis_6379

Edit the init script.

	$ sudo vi /etc/init.d/redis_6379

Make sure to modify REDIS_PORT accordingly to the port you are using. Both the pid file path and the configuration file name depend on the port number.
Copy the template configuration file you'll find in the root directory of the Redis distribution into /etc/redis/ using the port number as name.

	$ sudo cp redis.conf /etc/redis/6379.conf

Create a directory inside /var/redis that will work as data and working directory for this Redis instance

	$ sudo mkdir /var/redis/6379

Edit the configuration file, making sure to perform the following changes:

	$ sudo vi /etc/redis/6379.conf

Set daemonize to yes (by default it is set to no).
Set the pidfile to /var/run/redis_6379.pid (modify the port if needed).
Change the port accordingly. It is not needed as the default port is already 6379.
Set your preferred loglevel.
Set the logfile to /var/log/redis_6379.log
Set the dir to /var/redis/6379 (very important step!)

**Starting up Redis service**

	$ redis-server

