import os
import tempfile


@when('I pull occurrences from ALA using the LSID "{lsid}"')
def step_impl(context, lsid):
    context.temp_dir = tempfile.mkdtemp(suffix=__name__)
    source = {'type':'ala', 'lsid':lsid}
    destination = {'host':'local', 'path':context.temp_dir}
    response = context.server_proxy.move(source, destination)
    context.response = response
    status = response['status']
    assert len(os.listdir(context.temp_dir)) == 0
    assert status == 'PENDING' or status == 'IN_PROGRESS'

@then('I should see the ALA files in my local directory')
def step_impl(context):
    move_job_id = str(context.response['id'])
    occurrences_file = os.path.join(context.temp_dir, 'move_job_' + move_job_id + '_ala_occurrence.csv')
    metadata_file = os.path.join(context.temp_dir, 'move_job_' + move_job_id + '_ala_metadata.json')
    dataset_file = os.path.join(context.temp_dir, 'move_job_' + move_job_id + '_ala_dataset.json')
    assert os.path.isfile(occurrences_file)
    assert os.path.isfile(metadata_file)
    assert os.path.isfile(dataset_file)


# TODO: add environment.py before and after scenario, and make sure to shutdown the server after each test
# TODO: clear the database after each scenario