#!/usr/bin/python3

"""
Aplicacao que simula um servidor de autenticacao em Python que sera usado como 
um microservico em containers Docker

Copyright (c) 2021 Universidade do Minho
Perfil GVR - Virtualizacao de Redes 2020/21
Desenvolvido por: Nelson Faria (a84727@alunos.uminho.pt)
"""

import os, hashlib, socket
import comunicadb
import json, datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.error import HTTPError
from flask import Flask, request, abort, flash, session, render_template, redirect, make_response


app = Flask(__name__)

# IP do servidor de autenticacao
auth_ip = socket.gethostbyname("auth_container")
# IP do servidor de HTTP
http_ip = socket.gethostbyname("http_container")
# Porta do servidor autenticacao
auth_port = 5000
# Porta do servidor HTTP
http_port = 8888


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /login
'''
@app.route('/login', methods=['GET','POST'])
def login():

    # Caso tenha clicado no botao de login
    if(request.form.get("loginbutton")):
      
        username = str(request.form.get("username"))
        # Hash da password
        password = hashlib.sha256(request.form.get("password").encode()).hexdigest()
        # Se os tammanhos nao forem maiores que 0
        if len(username) == 0 or len(password) == 0:
        	flash("Introduce a valid username and password")
        	return render_template("login.html")

        # Update do utilizador, adicionando-lhe o respetivo token
        (updateUser, token) = comunicadb.updateUser(username, password)
        # Set cookie policy for session cookie.
        #expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=30, seconds=0)

        # Caso o utilizador seja valido, conceder acesso
        if updateUser == True:

            res = make_response(redirect('http://' + http_ip + ':' + str(http_port) + '/validaLogin' + '?token=' + token))
            return res

        else:
            flash("Username ou password errados!!")
            return render_template("login.html")

    # Se o utilizador clicou no botao regista, entao redirecionar para la!!
    if(request.form.get("registerbutton")):

        return redirect("/registaUser")

    return render_template("login.html")


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /loginFTP
(Este login so e usado no ambito do servidor ftp)
'''
@app.route('/loginFTP', methods=['POST'])
def loginFTP():

	data = request.get_json(force=True)
	username = data['username']
	password = hashlib.sha256(data['password'].encode()).hexdigest()
	# Update do utilizador, adicionando-lhe o respetivo token
	(updateUser,token) = comunicadb.updateUser(username,password)
	if updateUser == True:
		# Retorna ok
		return make_response(token, 200)
	else:
		# Retorna erro
		return make_response("erro", 404)


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /verificaToken
'''
@app.route("/verificaToken", methods=['POST'])
def verificaToken():

	data = request.get_json(force=True)
	username = data['username']
	token = data['token']
	#f = open("logs.txt", "w")
	#f.write(username)
	#f.write("\n")
	#f.write(token)
	#f.close()
	# verificar o token se existe na db
	res = comunicadb.existToken(username, token)
	if res == True:
		# Retorna ok
		return make_response("ok", 200)
	else:
		# Retorna erro
		return make_response("erro", 404)


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /registaUser
'''
@app.route('/registaUser', methods=['GET','POST'])
def registaUser():

	# Quando o pedido for efetuado
    if request.method == 'POST':
        if request.form.get("registerbutton"):

            username = str(request.form.get("username"))
            password = hashlib.sha256(request.form.get("password").encode()).hexdigest()
            email = request.form.get("email")
            if len(username) == 0 or len(email) == 0 or len(password) == 0:
            	flash("Introduce a valid username, email and password")
            	return render_template("register.html")
            role = "user"
            res = comunicadb.registaUser(username, password, email, role)
            if res == False:
            	flash("You're already registed!")
            	return render_template("register.html")

            return redirect("/login")

        if request.form.get("loginbutton"):
            return redirect("/login")

    return render_template("register.html")


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port=auth_port,debug=True)
