#!/bin/bash
cd auth-service
sudo docker build . -t auth-service
cd ..
cd db_auth-service
sudo docker build . -t db-service
cd ..
cd ftp-server
sudo docker build . -t ftp-service
cd ..
cd http-server
sudo docker build . -t http-service 
cd ..

sudo docker-compose up -d
