from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.authorizers import AuthenticationFailed
import requests

autorizer = None

class MyHandler(FTPHandler):
    def on_disconnect(self):
        #remove user on disconect as token may no longer be valid
        if authorizer.has_user(self.username):
            print("removing user: "+self.username)
            authorizer.remove_user(self.username)


class MyAuthorizer(DummyAuthorizer):
    def validate_authentication(self, username, password, handler):
        #check if the token is valid with the authentication server
        x = requests.get("http://auth_container:5000/login?username=" + username + "&password=" + password)
        if x.text == "true":
            valid = True
        # if valid
        if valid:
            #create a new user with the token as the username and blanck password
            self.add_user(username, ".", ".", perm='elradfmwM')
        else:
            raise AuthenticationFailed("Invalid Token")
            return False
        

authorizer = MyAuthorizer()

handler = MyHandler
handler.authorizer = authorizer
print(authorizer)
address = ("0.0.0.0", 21)  # listen on every IP on my machine on port 21
server = servers.FTPServer(address, handler)
server.serve_forever()

