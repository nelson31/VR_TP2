import os, hashlib
import jwt
import datetime
from dotenv import load_dotenv
# importing Mongoclient from pymongo
from pymongo import MongoClient
import pprint


load_dotenv("./auth-service/variaveis.env")
NAME_DB = os.getenv('NAME_DB')
USERNAME_DB = os.getenv('USERNAME_DB')
PASSWORD_DB = os.getenv('PASSWORD_DB')
AUTHSECRET = os.getenv('AUTHSECRET')
HOST = "mongo_container"
PORTA = 27017

uri = "mongodb://%s:%s@%s:%d" % (
    USERNAME_DB, PASSWORD_DB, HOST, PORTA)

print(AUTHSECRET)

'''
Funcao usada para registar um novo utilizador
'''
def registaUser(username, password, email, role):

    try:
        # Verificar se o utilizador ja existe na base de dados 
        if verificaUser(username, password):
            return False
        else:
            myclient = MongoClient(uri)
            # Obter a base de dados
            db = myclient[NAME_DB]
            # Inserir os dados 
            post = {"username": username,
                "password": password,
                "email": email,
                "role": role,
                "token": None}
            # Obter a colecao users
            users = db.users
            post_id = users.insert_one(post).inserted_id
            # Listar as colecoes
            # db.list_collection_names()
            # Obter um unico documento
            # pprint.pprint(users.find_one())
            # pprint.pprint(users.find_one({"_id": post_id}))
            # pprint.pprint(users.find_one({"username": "Nelson"}))
        
    except Exception as error:

        print(error)
        return False

    return True


'''
Verifica um determinado utilizador
'''
def verificaUser(username, password):

    try:
        
        myclient = MongoClient(uri)
        # Obter a base de dados
        mydb = myclient[NAME_DB]
        # Obter a coluna a alterar
        mycol = mydb["users"]
        
        myquery = { "username": username, "password": password }
        newvalues = { "$set": { "token": encode_token(username) } }

        # Fazer o update
        result = mycol.update_one(myquery, newvalues)

        # Se o utilizador nao existir, retorna falso
        if result.matched_count == 0:
            return False

    except Exception as error:
        print(error)
        return False

    return True


'''
Fazer o encoding de um token
'''
def encode_token(username):
    
    payload = {
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': username
                 }
                 
    return jwt.encode(
                payload,
                AUTHSECRET,
                algorithm='HS256')


'''
Fazer o dencoding de um token
'''
def decode_token(enctoken):
    try:
        payload = jwt.decode(enctoken, AUTHSECRET)
        return True
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
    
