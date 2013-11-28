import os
import tempfile
from data_mover.util.file_utils import listdir_fullpath


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
    out_files = listdir_fullpath(context.temp_dir)
    assert 3 == len(out_files)
    occurrences_exist = 1 == len([i for i in out_files if i.endswith('_ala_occurrence.csv')])
    metadata_exist = 1 == len([i for i in out_files if i.endswith('_ala_metadata.json')])
    dataset_exist = 1 == len([i for i in out_files if i.endswith('_ala_dataset.json')])
    assert occurrences_exist
    assert metadata_exist
    assert dataset_exist
