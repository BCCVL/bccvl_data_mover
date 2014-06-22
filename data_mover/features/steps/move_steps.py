import tempfile
import shutil
import os

@given('I want to use the destination "{dest_host}" and some temp directory')
def step(context, dest_host):
    context.temp_dir = tempfile.mkdtemp(suffix=__name__)
    assert len(os.listdir(context.temp_dir)) == 0
    context.destination = 'scp://' + dest_host + context.temp_dir

@given('my source is "{source}"')
def step(context, source):
    context.source = source

@given('one of my sources is "{source}"' )
def step(context, source):
    context.source.append(source)

@given('my source starts with "{url}" and path of some temporary file named "{filename}" with content "{content}"')
def step(context, url, filename, content):
    temp_dir = tempfile.mkdtemp(suffix=__name__)
    temp_file_name = os.path.join(temp_dir, filename)
    print "temp_file_name: " + temp_file_name
    temp_file = open(temp_file_name, 'w')
    temp_file.write(content)
    temp_file.close()
    context.source = url + os.path.abspath(temp_file_name)
    print context.source

@given('one of my sources starts with "{url}" and path of some temporary file named "{filename}" with content "{content}"')
def step(context, url, filename, content):
    temp_dir = tempfile.mkdtemp(suffix=__name__)
    temp_file_name = os.path.join(temp_dir, filename)
    temp_file = open(temp_file_name, 'w')
    temp_file.write(content)
    temp_file.close()
    context.source.append(url + os.path.abspath(temp_file_name))

@given('I want to move a file to "{dest_host}" at path "{dest_path}"')
def step(context, dest_host, dest_path):
    context.destination_dict = {'host':dest_host, 'source_path':dest_path}

@when('I request a move with the defined requirements')
def step(context):
    zip = False
    if hasattr(context, 'zip'):
        zip = context.zip
    response = context.server_proxy.move(context.source, context.destination, zip)
    context.response = response

@then('I should not see my temp dir')
def step(context):
    shutil.rmtree(context.temp_dir)

@given('my source is of type mixed')
def step(context):
    context.source = []

@given('I want to zip the files sent to the destination')
def step(context):
    context.zip = True