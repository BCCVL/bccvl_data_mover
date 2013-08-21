#!/bin/bash

if [ -z "$WORKSPACE" ]; then
    echo "Guessing WORKSPACE is .."
    WORKSPACE='..'
fi

WORKSPACE_PYTHON="$WORKSPACE/data_mover/python"
WORKING_DIR="$WORKSPACE/data_mover"

echo "Using WORKSPACE $WORKSPACE"
cd "$WORKSPACE"

echo "Setting up virtualenv in $WORKSPACE"
curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.tar.gz
tar -xvzf virtualenv-1.9.tar.gz
cd virtualenv-1.9
/usr/bin/env python26 virtualenv.py data_mover
cd data_mover
source bin/activate

cd "$WORKING_DIR"
pwd

"$WORKSPACE_PYTHON" setup.py develop
