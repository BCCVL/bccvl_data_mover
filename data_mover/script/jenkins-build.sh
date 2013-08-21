#!/bin/bash

if [ -z "$WORKSPACE" ]; then
    echo "Guessing WORKSPACE is .."
    WORKSPACE='..'
fi

WORKSPACE_PYTHON="$WORKSPACE/data_mover/bin/python26"
WORKING_DIR="$WORKSPACE/data_mover"

echo "Using WORKSPACE $WORKSPACE"
cd "$WORKSPACE"

echo "Setting up virtualenv in $WORKSPACE"
curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.tar.gz
tar -xvzf virtualenv-1.9.tar.gz
cd virtualenv-1.9
/usr/bin/env python26 virtualenv.py "$WORKING_DIR"
cd "$WORKING_DIR"
source bin/activate

"$WORKSPACE_PYTHON" setup.py develop

