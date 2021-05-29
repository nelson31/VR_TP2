#!/usr/bin/python3

"""
addAdmin.py serve so para adicionar um administrador no inicio (para ser mais facil)

Copyright (c) 2021 Universidade do Minho
Perfil GVR - Virtualizacao de Redes 2020/21
Desenvolvido por: Nelson Faria (a84727@alunos.uminho.pt)
"""

import os, hashlib
import comunicadb


def main():

	username = "admin"
	password = "admin"
	email = "admin@uminho.pt"
	role = "admin"
	hpassword = hashlib.sha256(password.encode()).hexdigest()
	res = comunicadb.registaUser(username, hpassword, email, role)


if __name__ == '__main__':
    main()


