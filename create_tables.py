import os
import psycopg2
import sys

# run in the venv
# running with commandline with any single arg will drop all old tables before creating. 

def createTables():
    conn = psycopg2.connect(
        host='localhost',
        database='capstone',
        user='postgres',
        password="postgres",
        port = 5432
    )

    drop = (
        "DROP TABLE images",
        "DROP TABLE dev_images",
        "DROP TABLE users",
        )

    commands = (
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
            username VARCHAR(255) NOT NULL,
            complete_password VARCHAR(255) NOT NULL,
            salt VARCHAR(16) NOT NULL,
            email VARCHAR(255) NOT NULL,
            pub_key VARCHAR(600)
        )
        """,
        """
        CREATE TABLE images (
            id SERIAL PRIMARY KEY,
            image_hash VARCHAR(255) NOT NULL,
            user_id UUID references users(id) NOT NULL,
            last_accessed TIMESTAMP
        )
        """,
        """
        CREATE TABLE dev_images (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        mimetype VARCHAR(100) NOT NULL,
        user_id UUID references users(id) NOT NULL,
        image_hash VARCHAR(255) NOT NULL
        )
        """
        )
    try:
        cur = conn.cursor()

        # drop tables, if provided args
        if (len(sys.argv) == 2):
            print('dropping old tables')
            for d in drop:
                cur.execute(d)
        conn.commit()


        # create table one by one
        for command in commands:
            cur.execute(command)

        # close communication with the PostgreSQL database server
        cur.close()

        # commit the changes
        conn.commit()
        print("created tables")
    except (Exception, psycopg2.DatabaseError) as error:
        print('oop')
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    createTables()