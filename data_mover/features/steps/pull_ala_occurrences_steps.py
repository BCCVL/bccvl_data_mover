import os
import tempfile


@when('I pull occurrences from ALA using the LSID "{lsid}"')
def step_impl(context, lsid):
    context.temp_dir = tempfile.mkdtemp(suffix=__name__)
    source = 'ala://ala?lsid=' + lsid
    destination = 'scp://localhost' + context.temp_dir
    response = context.server_proxy.move(source, destination)
    context.response = response
    status = response['status']
    assert len(os.listdir(context.temp_dir)) == 0
    assert status == 'PENDING' or status == 'IN_PROGRESS'

@then('I should see the ALA files in my temp directory')
def step_impl(context):
    out_files = [os.path.join(context.temp_dir, f) for f in os.listdir(context.temp_dir)]
    occurrences_exist = 1 == len([i for i in out_files if i.endswith('ala_occurrence.csv')])
    metadata_exist = 1 == len([i for i in out_files if i.endswith('ala_metadata.json')])
    dataset_exist = 1 == len([i for i in out_files if i.endswith('ala_dataset.json')])
    assert occurrences_exist
    assert metadata_exist
    assert dataset_exist
