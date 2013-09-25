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
print "Setting up test database"
conn = psycopg2.connect("dbname='data_mover_test' user='data_mover' password='data_mover'")
cur = conn.cursor()
cur.execute('DROP SCHEMA public CASCADE;')
cur.execute('CREATE SCHEMA public;')
conn.commit()
cur.close()
conn.close()

# Re-initialize db
subprocess.call(['./bin/initialize_data_mover_db', 'test.ini'])

# Start the test server
print "Starting test server..."
test_server = TestServer()
test_server.start()
print "Test server has started."

print "Running tests..."
# Run tests
subprocess.call(['./bin/behave'])

# Stop test server
print "Shutting down test server..."
test_server.stop()

print "Cleaning test directory..."
# Clean up the directory
if os.path.isdir('behave_test'):
    shutil.rmtree('behave_test')