from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.authorizers import AuthenticationFailed
import sys, requests


# Path para a pasta de uploads
UPDIRECTORY = "/usr/src/ftp/"


class MyAuthorizer(DummyAuthorizer):

    def validate_authentication(self, username, password, handler):

        #Testa se o user é valido com o auth server
        #payload = {'username': username, 'password': password}
        # Verificar se existe
        #x = requests.post('http://auth_container:5000/login', data=json.dumps(payload))
        x = requests.get("http://auth_container:5000/login?username=" + username + "&password=" + password)
        if x.text == "true":
            valid = True
        # Se for valido
        if valid:
            #create a new user with the token as the username and blanck password (perm é usado para permissoes)
            self.add_user(username, ".", UPDIRECTORY, perm='elradfmwM')
        else:
            raise AuthenticationFailed("Invalid Token")
            return False


class MyHandler(FTPHandler):

    def on_disconnect(self):

        #remove user on disconect as token may no longer be valid
        if authorizer.has_user(self.username):
            print("removing user: "+self.username)
            authorizer.remove_user(self.username)


def config():

	# Objeto responsavel pela autenticação dos utilizadores e suas respectivas permissoes
	authorizer = MyAuthorizer()
	print("Local de acesso do servidor : \n  " + UPDIRECTORY + '\n')

	# objeto que manipula os comandos enviados pelo cliente FTP
	handler = MyHandler
	# Responsavel pela autenticacao do servidor
	handler.authorizer = authorizer

	return handler


def main(arg):
	
	handler = config()
	porta = 21 # porta padrão do servidor
	if len(arg) == 1:
		ip = "172.20.0.1" # ip padrão do servidor
	else:
		ip = arg[1]
	
	# servidor
	server = FTPServer((ip,porta),handler)
	#inicia o servidor
	server.serve_forever()



if __name__ == '__main__':
	main(sys.argv)

