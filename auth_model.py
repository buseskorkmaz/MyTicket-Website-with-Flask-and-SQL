import os
import json

# pip install psycopg2
import psycopg2
from db import *

# pip install pyjwt
import jwt

from auth_payload import authPayload 
from auth_response import authResponse


def authenticate(clientId, clientSecret):

    conn = None
    query = "select * from clients where \"ClientId\"='" + clientId + "' and \"ClientSecret\"='" + clientSecret + "'"
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        isAdmin = False

        if cur.rowcount == 1:
            for row in rows:
                isAdmin = row[3]
                payload = authPayload(row[0],row[1], isAdmin)
                break

            encoded_jwt = jwt.encode(payload.__dict__, AUTHSECRET, algorithm='HS256')
            response = authResponse(encoded_jwt,EXPIRESSECONDS, isAdmin)
            
            return response.__dict__
        else:
            return False
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print(error)
        if conn is not None:
            cur.close()
            conn.close()

        return False
    finally:
        if conn is not None:
            cur.close()
            conn.close()

def verify(token):
    try:
        isBlacklisted = checkBlacklist(token)
        if isBlacklisted == True:
             return {"success": False}
        else:
            decoded = jwt.decode(token, AUTHSECRET, algorithms=['HS256'])
            return decoded
    except (Exception) as error:
        print(error)
        return {"success": False}

def create(email,password,city,theaterFan,cinemaFan,music,isadmin):

    success = register_to_db(email,password,city,theaterFan,cinemaFan,music,isadmin)

    return success

def blacklist(token):
    conn = None
    query = "insert into blacklist (\"token\") values(\'" + token +"\')"
    try:
        conn = connect()
        cur.execute(query)
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if conn is not None:
            cur.close()
            conn.close()

        return False
    finally:
        if conn is not None:
            cur.close()
            conn.close()

def checkBlacklist(token):
    conn = None
    query = "select count(*) from blacklist where token=\'" + token + "\'"
    print(query)
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
        if result[0] == 1:
            return True
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if conn is not None:
            cur.close()
            conn.close()

        return True
    finally:
        if conn is not None:
            cur.close()
            conn.close()