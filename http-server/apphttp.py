#!/usr/bin/python3

import os, sys, datetime
import requests
import jwt, json
from werkzeug.utils import secure_filename
from flask import Flask, request, url_for, redirect, render_template, make_response, send_from_directory, current_app
from dotenv import load_dotenv


app = Flask(__name__)

# LOcalizacao dos ficheiros relativos a aplicacao
UPDIRECTORY = "/http-server/upDirectory/"

# Extensoes permitidas para o download de ficheiros 
EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg'])

app.config['UPDIRECTORY'] = UPDIRECTORY

# IP do servidor de autenticacao
auth_ip = "172.20.0.3"
# IP do servidor de HTTP
http_ip = "172.20.0.2"
# Porta do servidor autenticacao
auth_port = 5000
# Porta do servidor HTTP
http_port = 8888


# Check file has an allowed extension
def allowed_file(filename):

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in EXTENSIONS


'''
Fazer o decoding de um token, retornando o nome do user e o seu papel
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


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /download/<path:filename>
(Usado aquando de um download de um ficheiro)
'''
@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):

    uploads = os.path.join(app.config['UPDIRECTORY'])
    return send_from_directory(directory=uploads, filename=filename)


'''
Funcao usada para validar os resultados que advem do login
'''
@app.route('/validaLogin', methods=['GET'])
def validaLogin():

    token = request.args.get('token')
    # Set cookie policy for session cookie.
    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=30, seconds=0)
    # Se o token nao for valido, redirecionar para a home
    if not token:
        return redirect(url_for('home'))
    else:
        # Redirecionar para o admin de modo a verificar se e administrador
        res = make_response(redirect(url_for('admin')))
        res.set_cookie("token", token, expires=expires)
        return res


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /
'''
@app.route('/', methods=['GET','POST'])
def home():

    try:
        token = request.cookies.get('token')
        token_dec = decode_token(token)
        # Verificar se estamos perante um user ou um admin, 
        # senao houver token ira ser redirecionado para o login na autenticacao
        if token_dec["role"] == "user":
            return redirect(url_for('user'))
        elif token_dec["role"] == "admin":
            return redirect(url_for('admin'))

    except Exception as error:
        return redirect('http://' + auth_ip + ':' + str(auth_port) + '/login')


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /admin
'''
@app.route('/admin', methods=['GET','POST'])
def admin():

    try:
        token = request.cookies.get('token')
        token_dec = decode_token(token)
        # Se for um user, redirecionar para la
        if token_dec["role"] == "user":
            return redirect(url_for('user'))

    except Exception as error:
        # Redirecionado para a home caso nao tenha token
        return redirect(url_for('home'))

    # If a post method then handle file upload
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect('/')
        file = request.files['file']

        if file.filename == '':
            return redirect('/')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPDIRECTORY'], filename))

    # Get Files in the directory and create list items to be displayed to the user
    file_list = []
    for f in os.listdir(app.config['UPDIRECTORY']):
        # Create link html
        file_list.append(f)

    return render_template("admin.html", files=file_list)


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /user
'''
@app.route('/user', methods=['GET'])
def user():

    try:
        token = request.cookies.get('token')
        token_dec = decode_token(token)
        # Se for um user, redirecionar para la
        if token_dec["role"] == "admin":
            return redirect(url_for('admin'))
    except Exception as error:
        return redirect('http://' + auth_ip + ':' + str(auth_port) + '/login')
    # Get Files in the directory and create list items to be displayed to the user
    file_list = []
    for f in os.listdir(app.config['UPDIRECTORY']):
        # Create link html
        file_list.append(f)

    return render_template("user.html", files=file_list)


'''
Funcao usada para proceder ao tratamento das operacoes relativas ao path /
'''
@app.route('/logout', methods=['POST'])
def logout():

    try:
        res = make_response(redirect(url_for('home')))
        # Apagar o token
        res.set_cookie('token', '', expires=0)
        return res

    except Exception as error:
        return redirect('http://' + auth_ip + ':' + str(auth_port) + '/login')


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=http_port, debug=True)
