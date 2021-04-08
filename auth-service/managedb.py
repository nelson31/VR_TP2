import psycopg2
import hashlib
import os
import jwt
import datetime
from dotenv import load_dotenv


load_dotenv("varia.env")
DBNAME = os.getenv('DBNAME')
DBUSER = os.getenv('DBUSER')
DBPASSWORD = os.getenv("DBPASSWORD")
AUTHSECRET = os.getenv("AUTHSECRET")
HOST = "postgres_container"
#AUTHSECRET = os.getenv("AUTHSECRET")

def RegisterUser(username, password,email, isAdmin):
    conn = None
    query = "insert into clients (\"username\", \"password\",\"email\", \"IsAdmin\") values(%s,%s,%s,%s)"

    try:
        
        conn = psycopg2.connect("dbname=" + DBNAME + " user=" + DBUSER + " host=" + HOST  + " password=" +DBPASSWORD)
        cur = conn.cursor()
        cur.execute(query, (username,password,email,isAdmin))
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

def VerifyUser(username,password):
    conn = None
    query = "select * from clients where \"username\"='" + username + "' and \"password\"='" + password + "'"
    insertoken = """Update clients set token= %s where username= %s"""
    try:
        conn = psycopg2.connect("dbname=" + DBNAME + " user=" + DBUSER + " host=" + HOST  + " password=" +DBPASSWORD)
        cur = conn.cursor()
        cur.execute(query)
        
        if cur.rowcount == 1:
            
            #cur.execute(insertoken,(encode_token(username),username))
            #conn.commit()
            return True
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



def encode_token(userid):
    
    payload = {
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=20, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': userid
                 }
                 
    return jwt.encode(
                payload,
                AUTHSECRET,
                algorithm='HS256')

def decode_token(enctoken):
    try:
        payload = jwt.decode(enctoken, AUTHSECRET)
        return True
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
    
