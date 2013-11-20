import tempfile
import shutil
import os

@given('I want to move a file to "{dest_host}" in some temp directory')
def step(context, dest_host):
    context.temp_dir = tempfile.mkdtemp(suffix=__name__)
    assert len(os.listdir(context.temp_dir)) == 0
    context.destination_dict = {'host':dest_host, 'path':context.temp_dir}

@given('my source is of type "{type}" with "{arg}" of "{value}"')
def step(context, type, arg, value):
    context.source_dict = {'type':type, arg:value}

@given('my source is of type "{type}" with host of "{host}" and path of some temporary file named "{filename}" with content "{content}"')
def step(context, type, host, filename, content):
    temp_dir = tempfile.mkdtemp(suffix=__name__)
    temp_file_name = os.path.join(temp_dir, filename)
    temp_file = open(temp_file_name, 'w')
    temp_file.write(content)
    temp_file.close()
    context.source_dict = {'type':type, 'host':host, 'path':os.path.abspath(temp_file_name)}

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