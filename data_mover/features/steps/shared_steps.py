from xmlrpclib import ServerProxy
import time
import os


@given('I am connected to the Data Mover server')
def step_impl(context):
    context.server_proxy = ServerProxy('http://0.0.0.0:8888/data_mover')

@then('I wait {minutes} minutes')
def step(context, minutes):
    seconds = float(minutes) * 60;
    time.sleep(seconds)

@then('I wait {seconds} seconds')
def step(context, seconds):
    time.sleep(float(seconds))

@then('I should see the file "{path}"')
def step(context, path):
    file_exists = os.path.exists(path)
    assert file_exists is True