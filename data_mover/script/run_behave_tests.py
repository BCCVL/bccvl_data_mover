"""
This script drop existing tables, re creates the tables, starts up the data mover app on port 8888, and then runs
'behave' tests that can be found in ../features/

NOTE:   You will need psycopg2 installed in your virtualenv to run this script.
        To install it, make sure you have source activate and then run:
            pip install psycopg2
"""
import os
import shutil
import subprocess
from test_server import TestServer
import psycopg2


# Setup Database
# Drop all tables in data_mover_test
conn = psycopg2.connect("dbname='data_mover_test' user='data_mover' password='data_mover'")
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS ala_jobs;')
cur.execute('DROP TABLE IF EXISTS ala_occurrences;')
conn.commit()
cur.close()
conn.close()

# Re-initialize db
devnull = open('/dev/null', 'w')
subprocess.Popen(['./bin/initialize_data_mover_db', 'test.ini'], stdout=devnull, stderr=subprocess.STDOUT)

# Start the test server
test_server = TestServer()
test_server.start()

# Run tests
subprocess.call(['./bin/behave'])

# Stop test server
test_server.stop()

# Clean up the directory
if os.path.isdir('behave_test'):
    shutil.rmtree('behave_test')