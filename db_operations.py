# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 11:10:45 2020

@author: bkorkmaz
"""

import psycopg2
from db import *
from passlib.context import CryptContext
from config import config

params = config(filename='CONFIG_FILE',section='encryption')

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)

def hash_password(password):
    return pwd_context.encrypt(password)
    
def verify_password(password,hashed_password):
    return pwd_context.verify(password, hashed_password)

def register_to_db(email,password,city,theaterFan,cinemaFan,music,isadmin):
    connection = connect()
    cursor = connection.cursor()
    
    isOrganizer = False
    print('here')
    hashed_password = hash_password(password)
    postgres_insert_query = """ INSERT INTO auth (email_address, password, isorganizer,isadmin) VALUES (%s,%s,%s,%s)"""
    record_to_insert = (email,hashed_password,isOrganizer,isadmin)
    try:
        cursor.execute(postgres_insert_query, record_to_insert)
        
        connection.commit()
        auth_id_query = """SELECT MAX(auth_id) from auth"""
        cursor.execute(auth_id_query)
        auth_id = cursor.fetchone()[0]
    
    except:
        print('unf here')
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
        organizer_id = "0"

    postgres_insert_query = """ INSERT INTO id_table (user_id, auth_id, organizer_id) VALUES (%s,%s,%s)"""
    record_to_insert = (str(user_id),str(auth_id),organizer_id)
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
    
    sql_select_query = """SELECT password from auth WHERE email_address = %s"""
    cursor.execute(sql_select_query, (email,))
    record = cursor.fetchone()
    
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
    
    if(record != None):
        if(verify_password(password,record[0])):
            return True
    
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
    

def get_userinfo_from_db(email):
    connection = connect()
    cursor = connection.cursor()  
    
    try:
        
        sql_select_query = """SELECT city,istheaterfan,iscinemafan,favourite_music_type FROM app_user INNER JOIN id_table 
        ON id_table.user_id = app_user.user_id 
        INNER JOIN auth 
        ON id_table.auth_id = auth.auth_id WHERE email_address=%s"""
        cursor.execute(sql_select_query,(email,))
        r = cursor.fetchone()
      
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        
        return r
    except:    
        return 'Could not found'
    
def add_basket(event_id,ticket_amount,email):
    connection = connect()
    cursor = connection.cursor()
    
    user_id = get_userid_from_db(email)
    price = get_price_from_db(event_id)
    error = 'Could not found'
    if(price == error or user_id == error):
        return error
    
    else:
        postgres_insert_query = """ INSERT INTO basket (user_id, event_id, price,quantity) VALUES (%s,%s,%s,%s)"""
        record_to_insert = (user_id,event_id,price, ticket_amount)
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

def get_userid_from_db(email):
    
    connection = connect()
    cursor = connection.cursor()
    
    sql_select_query = """SELECT app_user.user_id FROM app_user INNER JOIN id_table 
        ON id_table.user_id = app_user.user_id 
        INNER JOIN auth 
        ON id_table.auth_id = auth.auth_id WHERE email_address=%s"""
    
    try:
        cursor.execute(sql_select_query,(email,))
        r = cursor.fetchone()[0]
        return str(r)
    except:
        error = 'Could not found'
        return error

def get_price_from_db(event_id):
    connection = connect()
    cursor = connection.cursor()
    
    sql_select_query = """SELECT price FROM event WHERE event_id=%s"""
    
    try:
        cursor.execute(sql_select_query,(event_id,))
        r = cursor.fetchone()[0]
        return str(r)
    except:
        error = 'Could not found'
        return error

def get_current_basket_amount(email):
    
    user_id = get_userid_from_db(email)
    connection = connect()
    cursor = connection.cursor()
    sql_select_query = """SELECT COUNT(basket_id) FROM basket WHERE user_id=%s"""
    
    try:
        cursor.execute(sql_select_query,(user_id,))
        r = cursor.fetchone()[0]
        return str(r)
    except:
        error = 'Could not found'
        return error

def get_basket_list_from_db(email):
    
    user_id = get_userid_from_db(email)
    connection = connect()
    cursor = connection.cursor()
    sql_select_query = """SELECT event.title,basket.price,basket.quantity,basket.basket_id FROM basket INNER JOIN event 
        ON event.event_id = basket.event_id WHERE user_id=%s """
    
    try:
        cursor.execute(sql_select_query,(user_id,))
        r = cursor.fetchall()
        
        baskets = []
        for row in r:
            name = row[0]
            price = row[1]
            quantity = row[2]
            idx = row[3]
            total = price * int(float(quantity))
            baskets.append([name,price,quantity,total,idx])
        
        return baskets
    except:
        error = 'Could not found'
        return error
    
def delete_basket(basket_id):
    
    connection = connect()
    cursor = connection.cursor()
    sql_delete_query = """DELETE FROM basket WHERE basket_id=%s """
    
    try:
        cursor.execute(sql_delete_query,(basket_id,))
        connection.commit()
        
        return True
    except:
        error = 'Could not deleted'
        return error

def insert_session_token(token,email):
    
    user_id = get_userid_from_db(email)
    connection = connect()
    cursor = connection.cursor()
    sql_select_query = """ SELECT token FROM session_tokens WHERE user_id=%s"""
    try:
        cursor.execute(sql_select_query,(user_id,))
        r = cursor.fetchall()
        
        if(r != []):
            sql_update_query = """ UPDATE session_tokens SET token=%s WHERE user_id=%s"""
            cursor.execute(sql_update_query,(token,user_id,))
            connection.commit()
        else:
             postgres_insert_query = """ INSERT INTO session_tokens (user_id, token) VALUES (%s,%s)"""
             record_to_insert = (user_id,token)
             
             cursor.execute(postgres_insert_query, record_to_insert)
             connection.commit()
                    
             if(connection):
                 cursor.close()
                 connection.close()
                 print("PostgreSQL connection is closed")
          
    except:
        error = 'Could not insert'
        return error
        
    
def check_session_token(token):
    
    connection = connect()
    cursor = connection.cursor()
    sql_select_query = """ SELECT * FROM session_tokens WHERE token=%s"""
    error = 'Could not find'
    try:
        cursor.execute(sql_select_query,(token,))
        r = cursor.fetchall()
        if(r != []):
            return True
        else:
            return False
    except:
        
        return error
    
    