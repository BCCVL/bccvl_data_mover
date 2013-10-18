from xmlrpclib import ServerProxy
import time
import os


@given('I want to move a file to "{dest_host}" with file path "{dest_path}"')
def step(context, dest_host, dest_path):
    context.destination_dict = {'host':dest_host, 'path':dest_path}

@given('my file type is "{type}" with id "{id}"')
def step(context, type, id):
    context.source_dict = {'type':type, 'id':id}

@given('I want to move a file to "{dest_host}" with source path "{dest_path}"')
def step(context, dest_host, dest_path):
    context.destination_dict = {'host':dest_host, 'source_path':dest_path}

@given('my file protocol is "{type}" with url "{id}"')
def step(context, type, id):
    context.source_dict = {'protocol':type, 'url':id}


@when('I request a move with the defined requirements')
def step(context):
    response = context.server_proxy.move(context.destination_dict, context.source_dict)
    context.response = response

@then('I should see that the response is PENDING or IN_PROGRESS')
def step(context):
    status = context.response['status']
    context.move_job_id = context.response['id']
    assert status == 'PENDING' or status == 'IN_PROGRESS'

@then('I should see that the response status is REJECTED and the reason is "{expected_reason}"')
def step(context, expected_reason):
    status = context.response['status']
    reason = context.response['reason']
    assert status == 'REJECTED'
    assert reason == expected_reason

@when('I check the status of the move job')
def step_impl(context):
    response = context.server_proxy.checkMoveStatus(context.move_job_id)
    context.job_status = response['status']
    if 'reason' in response:
        context.job_reason = response['reason']

@then('I should see that the move job status is "{expected_status}"')
def step(context, expected_status):
    assert context.job_status == expected_status

@then('I should see that the reason is "{expected_reason}"')
def step(context, expected_reason):
    assert context.job_reason == expected_reason