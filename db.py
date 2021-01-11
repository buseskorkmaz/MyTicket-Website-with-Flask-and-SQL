# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 15:48:47 2020

@author: bkorkmaz
"""

import psycopg2
from config import config

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return error
    
    return conn
            

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE app_user (
            user_id SERIAL PRIMARY KEY,
            city TEXT NOT NULL,
            favourite_music_type TEXT DEFAULT NULL,
            isTheaterFan BOOL NOT NULL,
            isCinemaFan BOOL NOT NULL
        )
        """,
        """ CREATE TABLE auth (
                auth_id SERIAL PRIMARY KEY,
                email_address TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                isOrganizer BOOL NOT NULL
                )
        """,
        """
        CREATE TABLE organizer (
                organizer_id SERIAL PRIMARY KEY,
                event_type TEXT DEFAULT NULL
                )
        """,
        """
        CREATE TABLE city (
                city_id SERIAL PRIMARY KEY,
                city TEXT NOT NULL,
                country TEXT NOT NULL
                )
        """,
        """
        CREATE TABLE place (
                place_id SERIAL PRIMARY KEY,
                place TEXT NOT NULL,
                city_id INTEGER REFERENCES city
                )
        """,
        """
        CREATE TABLE comment (
                comment_id SERIAL PRIMARY KEY,
                event_comment_id TEXT NOT NULL,
                comment_date TIMESTAMP NOT NULL,
                comment TEXT NOT NULL
                )
        """,
        """
        CREATE TABLE event (
                event_id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                date TIMESTAMP NOT NULL,
                place_id INTEGER REFERENCES place, 
                price FLOAT8 NOT NULL,
                event_comment_id INTEGER REFERENCES comment,
                image_link TEXT DEFAULT NULL
               )
        """,
        """
        CREATE TABLE event_ticket (
                ticket_id SERIAL PRIMARY KEY,
                price float8 NOT NULL,
                event_id INTEGER REFERENCES event,
                amount INTEGER NOT NULL
                )
        """,
        """
        CREATE TABLE id_table (
                user_id SERIAL PRIMARY KEY,
                auth_id INTEGER REFERENCES auth,
                organizer_id INTEGER REFERENCES organizer
                )
        """,
        """
        CREATE TABLE payment (
                payment_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES app_user,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                event_id INTEGER REFERENCES event, 
                shipping_address TEXT DEFAULT NULL
               )
        """,
        """
        CREATE TABLE basket (
                basket_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES app_user,
                event_id INTEGER REFERENCES event, 
                price FLOAT8 NOT NULL,
                quantity TEXT NOT NULL
                )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()



if __name__ == '__main__':
    connect()