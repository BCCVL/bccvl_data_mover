#!/bin/bash

if [ -z "$WORKSPACE" ]; then
	WORKSPACE=`pwd`
    echo "Guessing WORKSPACE is $WORKSPACE"
fi

DATA_MOVER_DIR="$WORKSPACE/data_mover"
BIN_DIR="$DATA_MOVER_DIR/bin"

PIP="$BIN_DIR/pip"
PYTHON="$BIN_DIR/python"
BUILDOUT="$BIN_DIR/buildout"
NOSETESTS="$BIN_DIR/nosetests"
COVERAGE="$BIN_DIR/coverage"
EPYDOC="$BIN_DIR/epydoc"
BEHAVE_TEST="$DATA_MOVER_DIR/script/run_behave_tests.py"


echo "Using WORKSPACE $WORKSPACE"
cd $WORKSPACE

echo "Setting up virtualenv in $WORKSPACE"
curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-12.0.7.tar.gz
tar -xvzf virtualenv-12.0.7.tar.gz
python virtualenv-12.0.7/virtualenv.py -p "$(which python2.7)" "$DATA_MOVER_DIR"
cd "$DATA_MOVER_DIR"
source bin/activate
easy_install setuptools==0.9.8

echo "Python version:"
"$PYTHON" --version

# Clean
echo "Deleting .pyc files"
find ./data_mover -name "*.pyc" | xargs rm -rfv
find ./tests -name "*.pyc" | xargs rm -rfv
find ./features -name "*.pyc" | xargs rm -rfv
rm -rf ./epydoc

echo "Building data_mover"
cp buildout.cfg.example buildout.cfg
"$PYTHON" bootstrap.py -v 2.2.1
"$BUILDOUT"

# Build documentation
echo "Building epydoc documentation"
"$EPYDOC" --html -v -o ./epydoc --name data_mover data_mover/

# Run unit tests
echo "Running unit tests"
"$NOSETESTS" --with-xunit
TEST_RESULT=$?

echo "Building coverage data"
"$COVERAGE" xml --omit=./lib/*/*.py,./tests/*/*.py,./eggs/*/*.py

# So that Jenkins can see the source
#sed "s#filename=\"#filename=\"$WORKSPACE/data_mover/#g" coverage.xml > coverage-fixed.xml
sed "s#<\!-- Generated by coverage.py: http:\/\/nedbatchelder.com\/code\/coverage -->#<sources><source>$WORKSPACE/data_mover<\/source><\/sources>#g" coverage.xml > coverage-fixed.xml

# Run functional tests
echo "Running functional tests"
"$PYTHON" "$BEHAVE_TEST"
BEHAVE_RESULT=$?

RESULT=`expr $TEST_RESULT \\+ $BEHAVE_RESULT`

# So the build fails in Jenkins when unit tests or functional tests fail
exit $RESULT
