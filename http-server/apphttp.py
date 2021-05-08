#!/usr/bin/python3

import os
import requests
from werkzeug.utils import secure_filename
from flask import Flask, request, url_for, redirect, render_template, make_response, send_from_directory, current_app

PORT = 8888

# Files stored in
UPLOAD_FOLDER = "/http-server/upDirectory/"

# Allowed files extensions for upload
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'txt'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Check file has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def verifica_login(token):

    try:

        (username, role) = decode_token(token)

    except:
        return (False,'')

    return (True,role)


'''
Fazer o decoding de um token, retornando o nome do user e o seu papel
'''
def decode_token(enctoken):
    try:
        payload = jwt.decode(enctoken, AUTHSECRET)
        return (payload.user, payload.role)
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


@app.route('/', methods=['GET','POST'])
def home():

    try:
        token = request.cookies.get('vr_token')
        (user,role) = decode_token(token)

        if role == "user":
            return redirect(url_for('user'))
        elif role == "admin":
            return redirect(url_for('admin'))

    except Exception as e:
        return redirect('http://0.0.0.0:5000/login?Referer=http://0.0.0.0:' + str(PORT) + '/loginreturn')


@app.route('/loginreturn', methods=['GET'])
def loginreturn():

    token = request.args.get('token')
    if not token:
        return redirect(url_for('home'))
    else:
        resp = make_response(redirect(url_for('admin')))
        resp.set_cookie('vr_token', token)
        return resp


@app.route('/admin', methods=['GET','POST'])
def admin():

    try:
        token = request.cookies.get('vr_token')
        (user,role) = decode_token(token)

        # Se for um user, redirecionar para la
        if role == "user":
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

    token = request.cookies.get('vr_token')

    if(not verifica_login(token)):
        return redirect(url_for('home'))

    # Get Files in the directory and create list items to be displayed to the user
    file_list = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        # Create link html
        file_list.append(f)

    return render_template("user.html", files=file_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
