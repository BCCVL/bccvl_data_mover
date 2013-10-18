from xmlrpclib import ServerProxy
import time
import os


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



# TODO: add environment.py before and after scenario, and make sure to shutdown the server after each test
# TODO: clear the database after each scenario