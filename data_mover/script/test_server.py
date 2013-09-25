import subprocess
import time


class TestServer():
    def __init__(self):
        self.proccess = None

    def start(self):
        devnull = open('/dev/null', 'w')
        self.proccess = subprocess.Popen(['./bin/pserve', 'test.ini'], stdout=devnull, stderr=subprocess.STDOUT)
        time.sleep(10)

    def stop(self):
        self.proccess.kill()