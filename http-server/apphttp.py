#!/usr/bin/python3

import os, sys, datetime
import requests
import jwt, json
from werkzeug.utils import secure_filename
from flask import Flask, request, url_for, redirect, render_template, make_response, send_from_directory, current_app
from dotenv import load_dotenv


# Files stored in
UPLOAD_FOLDER = "/http-server/upDirectory/"

# Allowed files extensions for upload
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'txt'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


'''
Fazer o decoding de um token, retornando o nome do user e o seu papel
'''
def decode_token(enctoken):

    payload = jwt.decode(enctoken, 
        options={"verify_signature": False},
        algorithms=["HS256"])
    return payload


@app.route('/', methods=['GET','POST'])
def home():

    try:
        token = request.cookies.get('token')
        token_dec = decode_token(token)

        if token_dec["role"] == "user":
            return redirect(url_for('user'))
        elif token_dec["role"] == "admin":
            return redirect(url_for('admin'))

    except Exception as e:
        return redirect('http://' + auth_ip + ':' + str(auth_port) + '/login')


@app.route('/loginreturn', methods=['GET'])
def loginreturn():

    token = request.args.get('token')
    # Set cookie policy for session cookie.
    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=30, seconds=0)
    if not token:
        return redirect(url_for('home'))
    else:
        res = make_response(redirect(url_for('admin')))
        res.set_cookie("token", token, expires=expires)
        return res


@app.route('/admin', methods=['GET','POST'])
def admin():

    try:
        token = request.cookies.get('token')
        token_dec = decode_token(token)
        print(token_dec, file=sys.stdout)

        # Se for um user, redirecionar para la
        if token_dec["role"] == "user":
            return redirect(url_for('user'))

    except Exception as e:
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


    # Get Files in the directory and create list items to be displayed to the user
    file_list = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        # Create link html
        file_list.append(f)

    return render_template("admin.html", files=file_list)


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):

    uploads = os.path.join(app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename)


@app.route('/user', methods=['GET'])
def user():

    token = request.cookies.get('token')
    token_dec = decode_token(token)

    # Se for um user, redirecionar para la
    if token_dec["role"] == "admin":
        return redirect(url_for('admin'))


    # Get Files in the directory and create list items to be displayed to the user
    file_list = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        # Create link html
        file_list.append(f)

    return render_template("user.html", files=file_list)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=http_port, debug=True)
