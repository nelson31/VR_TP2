#!/usr/bin/python3

import os, hashlib
import comunicadb
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
from flask import Flask, request, flash, session, render_template, redirect


app = Flask(__name__)


@app.route('/login', methods=('GET', 'POST'))
def login():

    # Caso seja um pedido de post 
    if(request.form.get("loginbutton")):
      
        username = str(request.form.get("username"))
        # Hash da password
        password = hashlib.sha256(request.form.get("password").encode()).hexdigest()
        # Se os tammanhos nao forem maiores que 0
        if len(username) == 0 or len(password) == 0:
        	flash("Introduce a valid username and password")
        	return render_template("login.html")
        # Verifica o utilizador, adicionando-lhe o respetivo token
        verificaUser = comunicadb.verificaUser(username, password)
        # Obter o token
        token = comunicadb.encode_token(username)
        # Caso o utilizador seja valido, conceder acesso
        if verificaUser == True:

            query_parameters = parse_qs(urlparse(request.referrer).query)
            if('Referer' not in query_parameters):
                return token
            else:
                referer = query_parameters['Referer'][0]
                return redirect(str(referer) + '?token=' + token,302)
    
        else:
            flash("Wrong password or username")
            return render_template("login.html")

    # Caso seja um pedido de get
    if(request.args.get('username')):

        username = str(request.args.get('username'))
        password = hashlib.sha256(request.args.get('password').encode()).hexdigest()
        verificaUser = comunicadb.verificaUser(username,password)
         
        if verificaUser == True:
            return json.dumps(True)
        else:
            return json.dumps(False)

    # Se o utilizador clicou no botao regista, entao redirecionar para la!!
    if(request.form.get("registerbutton")):

        return redirect("/registaUser")

    return render_template("login.html")


@app.route("/verificaToken", methods=["GET"])
def verificaToken():

    # verify the token 
    if(request.args.get('token')):
        validtoken = comunicadb.decode_token(request.args.get('token'))
        if(validtoken == True):
            return json.dumps(True)
        else:
            return validtoken

    else:
        return "No Token in there"


@app.route('/registaUser', methods=['GET','POST'])
def registaUser():

    referrer = request.headers.get("Referer")
    print("Aparece  " + str(referrer))
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
    app.run(host="0.0.0.0", port=5000,debug=True)
