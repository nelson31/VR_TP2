#!/usr/bin/python3

from flask import Flask, request,flash, session, render_template, redirect
import hashlib
import managebd
import os
from urllib.parse import urlparse
from urllib.parse import parse_qs
import json

app = Flask(__name__)



@app.route('/login', methods=('GET', 'POST'))
def login():

    if(request.form.get("loginbutton")):
      
        username =  request.form.get("username")
        userpassword = hashlib.sha256(request.form.get("password").encode()).hexdigest()
        verifyuser = managebd.VerifyUser(username,userpassword) 
        token = managebd.encode_token(username)
        if verifyuser == True:
            query_parameters = parse_qs(urlparse(request.referrer).query)
            if('Referer' not in query_parameters):
                return token
            else:
                referer = query_parameters['Referer'][0]
                return redirect(str(referer)+ '?token=' +token.decode(),302)
    
        elif verifyuser == False:
            flash("Wrong password or username")

    if(request.form.get("registerbutton")):
        return redirect("/register")
        
    if(request.args.get('username')):
        print("a tua prima")
        username = request.args.get('username')
        password = hashlib.sha256(request.args.get('password').encode()).hexdigest()
        verifyuser = managebd.VerifyUser(username,password)
         
        if verifyuser == True:
            return json.dumps(True)
        else:
            return json.dumps(False)
    
    
    return render_template('login.html')

@app.route("/verify", methods=["GET"])
def verify():
    # verify the token 
    if(request.args.get('token')):
        validtoken = managebd.decode_token(request.args.get('token'))
        if(validtoken == True):
            return json.dumps(True)
        else:
            return validtoken

    else:
        return "No Token in there"



@app.route('/register', methods=['GET','POST'])
def register():
    referrer = request.headers.get("Referer")
    print("Aparece  " + str(referrer))
    if request.method == 'POST':

        if(request.form.get("registerbutton")):

            username =  request.form.get("username")
            userpassword = hashlib.sha256(request.form.get("password").encode()).hexdigest()
            email = request.form.get("email")
            isAdmin = False
            managebd.RegisterUser(username,userpassword,email,isAdmin)

            return redirect("/login")

        if(request.form.get("loginbutton")):
            return redirect("/login")

    return render_template("register.html")

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port=5001,debug=True)
