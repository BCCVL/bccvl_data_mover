from xmlrpclib import ServerProxy
import time
import os


@given('I am connected to the Data Mover server')
def step_impl(context):
    context.server_proxy = ServerProxy('http://0.0.0.0:8888/data_mover')

@when('I pull occurrences from ALA using the LSID "{lsid}"')
def step_impl(context, lsid):
    response = context.server_proxy.pullOccurrenceFromALA(lsid)
    status = response['status']
    context.job_id = response['id']
    assert status == 'PENDING' or status == 'DOWNLOADING'

@when('I check the status of the pull job')
def step_impl(context):
    response = context.server_proxy.checkALAJobStatus(context.job_id)
    context.job_status = response['status']

@then('I should see that the job status is "{expected_status}"')
def step(context, expected_status):
    assert context.job_status == expected_status

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

# TODO: add environment.py before and after scenario, and make sure to shutdown the server after each test
# TODO: clear the database after each scenario