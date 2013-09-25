import subprocess
import time


class TestServer():
    def __init__(self):
        self.proccess = None

    def start(self):
        self.proccess = subprocess.Popen(['./bin/pserve', 'test.ini'])
        print 'Sleeping for 30 seconds'
        time.sleep(30)

    def stop(self):
        self.proccess.kill()