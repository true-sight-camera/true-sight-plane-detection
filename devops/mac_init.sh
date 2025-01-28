# !/bin/bash

# Initial Setup Script 

echo Making Postgres and App

# sudo service postgresql start

# Wait for db to be up
until nc -z localhost 5432
do
    echo "waiting for db container..."
    sleep 0.5
done


export FLASK_APP=main
export FLASK_ENV=development

# python3 -m pip install -r requirements.txt

#should probably ensure the tables exist in the db

#start backend
gunicorn main:app --bind 0.0.0.0:5000 --reload

# export PATH=/Library/PostgreSQL/17/bin:$PATH

# echo Creating Tables
# docker exec app python3 app/scripts/createTables.py

# echo Adding prod data 
# docker exec app python3 -m app.scripts.add_prod_data

# use for quick copy and paste while script is broken
