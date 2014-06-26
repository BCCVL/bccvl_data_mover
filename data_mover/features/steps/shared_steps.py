from xmlrpclib import ServerProxy
import time
import os
from data_mover.util.file_utils import listdir_fullpath


@given('I am connected to the Data Mover server')
def step_impl(context):
    context.server_proxy = ServerProxy('http://0.0.0.0:8888/data_mover')

@then('I should see "{num}" files in my temp directory')
def step(context, num):
    files = listdir_fullpath(context.temp_dir)
    print "Number of files: " + str(len(files))
    assert int(num) == len(files)

@then('I should see a file with suffix "{suffix}" in my temp directory')
def step(context, suffix):
    print 'temp dir: ' + context.temp_dir
    files = listdir_fullpath(context.temp_dir)
    file_exist = len([i for i in files if i.endswith('.' + suffix)]) >= 1
    assert file_exist

@then('I should see a file in my temp directory named "{filename}" with content "{content}"')
def step(context, filename, content):
    expected_file = os.path.join(context.temp_dir, filename)
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        out_content = f.read().replace('\n', '')
        print "content: " + out_content
        assert content == out_content

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

@then('I check if the status of the job is "{expected}" for at most {total_time} seconds')
def step(context, expected, total_time):
    end_time = time.time()+float(total_time)
    while time.time() <= end_time:
        context.response = context.server_proxy.check_move_status(context.response['id'])
        if context.response['status'] == expected:
            assert True
            return
        time.sleep(5)
    context.response = context.server_proxy.check_move_status(context.response['id'])
    assert expected == context.response['status']


