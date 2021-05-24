#!/usr/bin/python3

"""
Auxiliar da appauth.py para comunicacao com a MongoDB

Copyright (c) 2021 Universidade do Minho
Perfil GVR - Virtualizacao de Redes 2020/21
Desenvolvido por: Nelson Faria (a84727@alunos.uminho.pt)
"""

import os, hashlib
import jwt
import json
import datetime
from dotenv import load_dotenv
# importing Mongoclient from pymongo
from pymongo import MongoClient
import pprint


# Carregar algumas variaveis 
load_dotenv("./auth-service/variaveis.env")
NAME_DB = os.getenv('NAME_DB')
USERNAME_DB = os.getenv('USERNAME_DB')
PASSWORD_DB = os.getenv('PASSWORD_DB')
AUTHSECRET = os.getenv('AUTHSECRET')
HOST = "mongo_container"
PORTA = 27017

uri = "mongodb://%s:%s@%s:%d" % (
    USERNAME_DB, PASSWORD_DB, HOST, PORTA)


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
Faz update um determinado utilizador, retornando true se correr tudo bem e 
ainda o seu papel no sistema
'''
def updateUser(username, password):

    try:
        
        myclient = MongoClient(uri)
        # Obter a base de dados
        mydb = myclient[NAME_DB]
        # Obter a coluna a alterar
        mycol = mydb["users"]

        myquery = { "username": username, "password": password }

        # Encontrar um que faca match
        result = mycol.find_one(myquery)

        # Se o utilizador nao existir, retorna falso
        if len(result.items()) == 0:
            return (False, '')
        else:
            token = encode_token(username, result['role'])
            newvalues = { "$set": { "token": token } }

            # Fazer o update
            result1 = mycol.update_one(myquery, newvalues)

            return (True, token)

    except Exception as error:
        print(error)
        return (False, error)


'''
Usado para verificar se um determinado token existe para um determinado user
'''
def existToken(username, token):

    try:
        
        myclient = MongoClient(uri)
        # Obter a base de dados
        mydb = myclient[NAME_DB]
        # Obter a coluna a alterar
        mycol = mydb["users"]
        
        myquery = { "username": username, "token": token }

        # Encontrar um que faca match
        result = mycol.find_one(myquery)

        # Se o utilizador nao existir, retorna falso
        if result == None:
            return False
        else:
            return True

    except Exception as error:
        return False


'''
Usado para apagar o token de um dado utilizador
'''
def apagarToken(username, password):

    try:
        myclient = MongoClient(uri)
        # Obter a base de dados
        mydb = myclient[NAME_DB]
        # Obter a coluna a alterar
        mycol = mydb["users"]
        
        myquery = { "username": username, "password": password }
        # Encontrar um que faca match
        result = mycol.find_one(myquery)
        # Se o utilizador nao existir, retorna falso
        if result == None:
            return False
        else:
            newvalues = { "$set": { "token": None } }
            # Fazer o update
            result1 = mycol.update_one(myquery, newvalues)
            return True

    except Exception as error:
        print(error)
        return False


'''
Verifica um determinado utilizador, retornando tambem o seu papel no sistema
'''
def verificaUser(username, password):

    try:
        
        myclient = MongoClient(uri)
        # Obter a base de dados
        mydb = myclient[NAME_DB]
        # Obter a coluna a alterar
        mycol = mydb["users"]
        
        myquery = { "username": username, "password": password }

        # Encontrar um que fasca match
        result = mycol.find_one(myquery)

        # Se o utilizador nao existir, retorna falso
        if result == None:
            return (False, '')
        else:
            return (True, result['role'])

    except Exception as error:
        print(error)
        return (False, '')

    return (True, result['role'])


'''
Fazer o encoding de um token
'''
def encode_token(username, role):
    
    payload = {
                "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=30, seconds=0),
                "iat": datetime.datetime.utcnow(),
                "user": username,
                "role": role
                 }
                 
    return jwt.encode(
                payload,
                AUTHSECRET,
                algorithm="HS256")


'''
Fazer o decoding de um token
'''
def decode_token(enctoken):

    try:
        payload = jwt.decode(enctoken, 
            options={"verify_signature": False}, 
            algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
