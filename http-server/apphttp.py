#!/usr/bin/python3
import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests
import os
import time
from os import path

PORT = 8001


class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):

    def redirect(self):
                    self.send_response(303)
                    self.send_header('Location','http://0.0.0.0:5001/login?Referer=http://0.0.0.0:'+str(PORT))
                    self.end_headers()
    def do_GET(self):

                usertoken = ""
                if path.exists("testfile.txt"):
                    with open("testfile.txt","rb") as file:  
                        usertoken = file.read()
                        x = requests.get("http://auth_container:5001/verify?token="+usertoken.decode())
                        if x.text == "true":
                            return super().do_GET()
                        else:
                             os.remove("testfile.txt")
                             return  self.redirect()
                else:
                    query_parameters = parse_qs(urlparse(self.path).query)
                    if('token' not in query_parameters):
                         return self.redirect()
                    else:
                        usertoken = query_parameters["token"][0]
                        #usertoken = bytes.fromhex(usertoken)
                        x = requests.get("http://auth_container:5001/verify?token="+usertoken)
                        if x.text == "true":
                            with open("testfile.txt","w") as file:
                                  file.write(usertoken)
                            return super().do_GET()
                        else:
                             #self.send_response(401)
                            #self.send_header("Content-type", "text/html")
                            #self.end_headers()
                            #html = f"<html><head></head><body><h1>No token available</h1></body></html>"
                            return self.redirect()

                 
            #if valid
           
            #if not valid
    

handler = HttpRequestHandler

with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
    print("Server started at 0.0.0.0:" + str(PORT))
    httpd.serve_forever()
