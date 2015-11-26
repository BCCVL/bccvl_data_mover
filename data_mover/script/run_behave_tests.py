"""
This script drop existing tables, re creates the tables, starts up the data mover app on port 8888, and then runs
'behave' tests that can be found in ../features/
"""
import os
import shutil
import subprocess
import sys
import time


class TestServer():
    def __init__(self):
        self.process = None

    def start(self):
        stderr_file = open('data_mover_test_stderr.log', 'w+')
        self.process = subprocess.Popen(['./bin/pserve', 'test.ini'], stdout=subprocess.PIPE, stderr=stderr_file)
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

sys.exit(behave_process_return_code)