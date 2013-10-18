"""
This script drop existing tables, re creates the tables, starts up the data mover app on port 8888, and then runs
'behave' tests that can be found in ../features/

NOTE:   You will need psycopg2 installed in your virtualenv to run this script.
        To install it, make sure you have source activate and then run:
            pip install psycopg2
"""
import os
import psycopg2
import shutil
import subprocess
import sys
import time


class TestServer():
    def __init__(self):
        self.process = None

    def start(self):
        self.process = subprocess.Popen(['./bin/pserve', 'test.ini'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print 'Sleeping for 10 seconds'
        time.sleep(10)

    def stop(self):
        self.process.kill()

    def print_stdout_stderr(self):
        out, err = self.process.communicate()
        if out:
            print ""
            print "stdout:"
            print out
            print ""
        if err:
            print ""
            print "stderr:"
            print >> sys.stderr, err
            print ""

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

# Create directory for move_test
if not os.path.isdir('/tmp/behave_test/bccvl/visualizer'):
    os.makedirs('/tmp/behave_test/bccvl/visualizer')

# Start the test server
print "Starting test server..."
test_server = TestServer()
test_server.start()
print "Test server has started."

print "Running tests..."
# Run tests
behave_process_return_code = subprocess.call(['./bin/behave', '--junit'])

# Stop test server
print "Shutting down test server..."
test_server.stop()

if behave_process_return_code != 0:
    test_server.print_stdout_stderr()

print "Cleaning test directory..."
# Clean up the directory
if os.path.isdir('behave_test'):
    shutil.rmtree('behave_test')

if  os.path.isdir('/tmp/behave_test'):
    shutil.rmtree('/tmp/behave_test')

sys.exit(behave_process_return_code)