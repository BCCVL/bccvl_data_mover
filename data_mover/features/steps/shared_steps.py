from xmlrpclib import ServerProxy
import time
import os


@given('I am connected to the Data Mover server')
def step_impl(context):
    context.server_proxy = ServerProxy('http://0.0.0.0:8888/data_mover')

@then('I wait {minutes} minutes')
def step(context, minutes):
    seconds = float(minutes) * 60
    time.sleep(seconds)

@then('I wait {seconds} seconds')
def step(context, seconds):
    time.sleep(float(seconds))

@then('I should see a file with suffix "{suffix}" in my temp directory')
def step(context, suffix):
    move_job_id = str(context.response['id'])
    print 'temp dir: ' + context.temp_dir
    file = os.path.join(context.temp_dir, 'move_job_' + move_job_id + '.' + suffix)
    file_exists = os.path.exists(file)
    assert file_exists

@then('I should see that the job status is "{expected_status}"')
def step(context, expected_status):
    print 'expected: ' + expected_status + ' actual: ' + context.response['status']
    assert expected_status == context.response['status']

@then('I should see that the job status is either "{status_1}" or "{status_2}"')
def step(context, status_1, status_2):
    current_status = context.response['status']
    print 'expected: ' + status_1 + ' or ' + status_2 + ' actual: ' + current_status
    assert status_1 == current_status or status_2 == current_status

@then('I should see that the job reason is "{expected_reason}"')
def step(context, expected_reason):
    print 'expected: "' + expected_reason + '" actual: "' + context.response['reason'] + '"'
    assert  expected_reason == context.response['reason']

@when('I check the status of the move job')
def step_impl(context):
    response = context.server_proxy.check_move_status(context.response['id'])
    context.response = response