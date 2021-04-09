FROM ubuntu:latest

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

# Copiar esta o conteudo desta diretoria para o container
COPY appflask.py auth-service/

# Correr o Flask
RUN python3 auth-service/appflask.py

# Expor uma porta
EXPOSE 5000
