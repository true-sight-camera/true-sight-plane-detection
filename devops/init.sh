#!/bin/bash

# Initial Setup Script 

# FILE=.env
# if test -f "$FILE"; then
#     echo "$FILE found."
# else 
#     echo "Halting, $FILE not found."
#     exit
# fi

# echo Building Images
# docker-compose -f docker-dev.yml build 

# echo Starting Containers 
# docker-compose -f docker-dev.yml up -d

echo Making Postgres and App

sudo service postgresql start

# Wait for db to be up
until nc -z localhost 5432
do
    echo "waiting for db container..."
    sleep 0.5
done


export FLASK_APP=main
export FLASK_ENV=development

#should probably ensure the tables exist in the db

pip install -r requirements.txt

#start backend
# python3 -m flask run --host=0.0.0.0 --debug
gunicorn main:app --bind 0.0.0.0:5000 --reload

# echo Creating Tables
# docker exec app python3 app/scripts/createTables.py

# echo Adding prod data 
# docker exec app python3 -m app.scripts.add_prod_data

# use for quick copy and paste while script is broken
