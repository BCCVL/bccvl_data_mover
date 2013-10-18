from xmlrpclib import ServerProxy
import time
import os
import shutil


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

@then('I should see the file "{path}" in my temp directory')
def step(context, path):
    full_path = os.path.join(context.temp_dir, path)
    file_exists = os.path.exists(full_path)
    if file_exists is False:
        if os.path.isdir(context.temp_dir):
            shutil.rmtree(context.temp_dir)
    assert file_exists is True