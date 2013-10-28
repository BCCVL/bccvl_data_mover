import tempfile
import shutil
from data_mover.util.file_utils import create_parent

@given('I want to move a file to "{dest_host}" in some temp directory')
def step(context, dest_host):
    context.temp_dir = tempfile.mkdtemp(suffix=__name__)
    create_parent(context.temp_dir)
    context.destination_dict = {'host':dest_host, 'path':context.temp_dir}

@given('my source is of type "{type}" with "{arg}" of "{value}"')
def step(context, type, arg, value):
    context.source_dict = {'type':type, arg:value}

@given('I want to move a file to "{dest_host}" at path "{dest_path}"')
def step(context, dest_host, dest_path):
    context.destination_dict = {'host':dest_host, 'source_path':dest_path}

@when('I request a move with the defined requirements')
def step(context):
    response = context.server_proxy.move(context.source_dict, context.destination_dict)
    context.response = response

@then('I should not see my temp dir')
def step(context):
    shutil.rmtree(context.temp_dir)
