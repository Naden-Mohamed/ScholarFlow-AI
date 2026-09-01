#!/bin/bash

<< 'COMMENT'
Shebang (#!) put on the very first line of the script.
 It is a special directive that tells the system which interpreter to use to execute the script.
COMMENT

set -e
# by default if any of the commands failed it will show an error and run the following commands
# but this -e raise error and stops running

echo "Running database migrations..."
cd /app/models/db_schemas/scholarflow/
alembic upgrade head
cd /app

exec "$@"

# it's a separated script used to run commands we want to execute after docker image build
# not through the process of building

<< 'COMMENT'
running the alembic upgrade in a separat script cuz it will raise an error if we but it in Dockerfile
cuz it needs pgvector to be set and while running the image, the pgvector service is not added yet
COMMENT
