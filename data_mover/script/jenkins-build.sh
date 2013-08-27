#!/bin/bash

if [ -z "$WORKSPACE" ]; then
    echo "Guessing WORKSPACE is .."
    WORKSPACE='..'
fi

DATA_MOVER_DIR="$WORKSPACE/data_mover"
BIN_DIR="$DATA_MOVER_DIR/bin"

PIP="$BIN_DIR/pip"
NOSETESTS="$BIN_DIR/nosetests"
COVERAGE="$BIN_DIR/coverage"

echo "Using WORKSPACE $WORKSPACE"
cd $WORKSPACE

echo "Setting up virtualenv in $WORKSPACE"
curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.tar.gz
tar -xvzf virtualenv-1.9.tar.gz
cd virtualenv-1.9
/usr/bin/env python26 virtualenv.py -p /usr/local/bin/python2.7 $DATA_MOVER_DIR
cd $DATA_MOVER_DIR
source bin/activate

echo "Python version:"
python --version

echo "Deleting all .pyc files"
find . -name "*.pyc" | xargs rm -rf

$PIP install -r requirements.txt
$NOSETESTS --with-xunit
RESULT=$?

$COVERAGE xml --omit=./lib/*/*.py,./tests/*/*.py

# So that Jenkins can see the source
sed 's/filename="/filename=$WORKSPACE/data_mover//g' coverage.xml > coverage-fixed.xml

# So the build fails in Jenkins when unit tests fail
exit $RESULT