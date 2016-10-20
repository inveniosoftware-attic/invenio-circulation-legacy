#!/bin/sh

DIR=`dirname "$0"`

cd $DIR
export FLASK_APP=app.py

# clean environment
[ -e "$DIR/instance" ] && rm -Rf $DIR/instance
[ -e "$DIR/static" ] && rm -Rf $DIR/static

# Delete the database
flask db drop --yes-i-know

# Delete indices
flask index destroy --yes-i-know --force
