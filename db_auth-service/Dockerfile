FROM mongo:4.4.5

# Atualizar os pacotes
RUN apt-get update &&\
 apt-get install -y software-properties-common &&\
 add-apt-repository universe &&\
 apt-get install -y php-apcu

# Definicao das variaveis de ambiente de autenticacao e criacao da base de dados
ENV MONGO_INITDB_ROOT_USERNAME=root
ENV MONGO_INITDB_ROOT_PASSWORD=pass12345
ENV MONGO_INITDB_DATABASE=authdb
ENV MONGODB_DATA_DIR=/data/db
ENV MONDODB_LOG_DIR=/var/log/mongodb

# Comandos adicionais a correr
RUN apt-get install -y iputils-ping
RUN apt-get install -y net-tools

# Correr o mongo unicamente com autenticacao
#RUN chown mongodb /var/log
#RUN mongod --auth --fork --logpath /var/log/mongod.log
CMD [ "mongod", "--auth"]

