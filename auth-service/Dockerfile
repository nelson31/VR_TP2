FROM ubuntu:20.04

# Atualizar os pacotes
RUN apt-get update &&\
 apt-get install -y software-properties-common &&\
 add-apt-repository universe &&\
 apt-get install -y php-apcu

# Instalar as dependencias necessarias
RUN apt-get install -y python3.7
RUN apt-get install -y python3-pip
RUN pip3 install Flask
RUN pip3 install pyjwt
RUN pip3 install python-dotenv
RUN pip3 install Flask-PyMongo

# Pacotes adicionais
RUN apt-get install -y iputils-ping
RUN apt-get install -y net-tools

# Copiar esta o conteudo desta diretoria para o container
COPY . auth-service/

# Adicionar um administrador inicial
CMD [ "python3", "auth-service/addAdmin.py" ]
# Correr o Flask
CMD [ "python3", "auth-service/appauth.py" ]

# Expor uma porta
EXPOSE 5000
