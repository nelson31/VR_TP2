#!/usr/bin/python3

import os, hashlib
import comunicadb
import json, datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs
from flask import Flask, request, flash, session, render_template, redirect, make_response


app = Flask(__name__)

# IP do servidor de autenticacao
auth_ip = "172.20.0.3"
# IP do servidor de HTTP
http_ip = "172.20.0.2"
# Porta do servidor autenticacao
auth_port = 5000
# Porta do servidor HTTP
http_port = 8888


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /login
'''
@app.route('/login', methods=('GET', 'POST'))
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

    # Caso seja um pedido de get
    if(request.args.get('username')):

        username = str(request.args.get('username'))
        password = hashlib.sha256(request.args.get('password').encode()).hexdigest()
        (updateUser,token) = comunicadb.updateUser(username,password)
         
        if updateUser == True:
            return json.dumps(True)
        else:
            return json.dumps(False)

    # Se o utilizador clicou no botao regista, entao redirecionar para la!!
    if(request.form.get("registerbutton")):

        return redirect("/registaUser")

    return render_template("login.html")


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /verificaToken
'''
@app.route("/verificaToken", methods=["GET"])
def verificaToken():

    # verificar o token 
    if(request.args.get('token')):
        validtoken = comunicadb.decode_token(request.args.get('token'))
        if(validtoken == True):
            return json.dumps(True)
        else:
            return validtoken

    else:
        return "No Token in there"


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /registaUser
'''
@app.route('/registaUser', methods=['GET','POST'])
def registaUser():

	# Quando o pedido for efetuado
    if request.method == 'POST':
        if(request.form.get("registerbutton")):

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

        if(request.form.get("loginbutton")):
            return redirect("/login")

    return render_template("register.html")


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port=auth_port,debug=True)
