# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 11:10:45 2020

@author: bkorkmaz
"""

import psycopg2
from db import *

def register_to_db(email,password,city,theaterFan,cinemaFan,music):
    connection = connect()
    cursor = connection.cursor()
    
    isOrganizer = False
    
    postgres_insert_query = """ INSERT INTO auth (email_address, password, isorganizer) VALUES (%s,%s,%s)"""
    record_to_insert = (email,password,isOrganizer)
    try:
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        auth_id_query = """SELECT MAX(auth_id) from auth"""
        cursor.execute(auth_id_query)
        auth_id = cursor.fetchone()[0]
    
    except:
        error = 'Could not insert'
        return error
        
    postgres_insert_query = """ INSERT INTO app_user (city, favourite_music_type, istheaterfan, iscinemafan) VALUES (%s,%s,%s,%s)"""
    record_to_insert = (city,music,theaterFan, cinemaFan)
    try:
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()

        user_id_query = """SELECT MAX(user_id) from app_user"""
        cursor.execute(user_id_query)
        user_id = cursor.fetchone()[0]
    
    except:
        error = 'Could not insert'
        return error
    
    if(isOrganizer == False):
        organizer_id = 0

    postgres_insert_query = """ INSERT INTO id_table (user_id, auth_id, organizer_id) VALUES (%s,%s,%s)"""
    record_to_insert = (user_id,auth_id,organizer_id)
    try:
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()
    except:
        error = 'Could not insert'
        return error
    
    
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
    
    return True

def check_auth_db(email,password):
    connection = connect()
    cursor = connection.cursor()  
    
    try:
        sql_select_query = """SELECT auth_id from auth WHERE email_address = %s and password = %s"""
        cursor.execute(sql_select_query, (email,password))
        record = cursor.fetchone()[0]
        
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            
        return True
    except:    
        return 'Could not found'
    
def get_events_from_db():
    connection = connect()
    cursor = connection.cursor()  
    
    try:
        sql_select_query = """SELECT * FROM event """
        cursor.execute(sql_select_query)
        record = cursor.fetchall()
        events = []
        for r in record:
            sql_select_query = """SELECT place,city_id FROM place WHERE place_id = %s"""
            place_id = r[5]
            cursor.execute(sql_select_query,(str(place_id)))
            places = cursor.fetchone()
            
            place = places[0]
            city_id = places[1]
            
            sql_select_query = """SELECT city,country FROM city WHERE city_id = %s"""
            cursor.execute(sql_select_query,(str(city_id)))
            city_records = cursor.fetchone()
            city = city_records[0]
            country = city_records[1]
            
            event = [r[1], r[3], r[4], place, city, country, r[6],r[0]]
            events.append(event)
        
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
      
        
        return events
    except:    
        return 'Could not found'
    
def get_event_from_db(event_id):
    
    connection = connect()
    cursor = connection.cursor()  
    
    try:
        sql_select_query = """SELECT * FROM event WHERE event_id=%s"""
        cursor.execute(sql_select_query,(event_id,))
        r = cursor.fetchone()

        sql_select_query = """SELECT place,city_id FROM place WHERE place_id = %s"""
        place_id = r[5]
        cursor.execute(sql_select_query,(str(place_id)))
        places = cursor.fetchone()
        
        place = places[0]
        city_id = places[1]
            
        sql_select_query = """SELECT city,country FROM city WHERE city_id = %s"""
        cursor.execute(sql_select_query,(str(city_id)))
        city_records = cursor.fetchone()
        city = city_records[0]
        country = city_records[1]
        location = city + "/" + country
        
        event = [r[1],r[8] ,r[3], r[6], place, location, r[4], "80"]
        
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
      
        
        return event
    except:    
        return 'Could not found'
