## Prerequisites
```
cd erss-final-yy252-ym154/server-docker/server
pip3 install protobuf
sudo apt install protobuf-compiler
protoc -I=. --python_out=. ./world_amazon.proto
protoc -I=. --python_out=. ./UA.proto
```

## Run
1. Frontend Server
- Modify `/frontEndServer/views.py` AMAZON_HOST to your hostname
- Run Frontend Server with 
    ```
    cd erss-final-yy252-ym154/frontend-docker/
    sudo docker-compose up
    ```
2. Amazon Server
- Modify `/server-docker/server/run_server.py` WORLD_HOST to world hostname
- Run Amazon Server with 
    ```
    cd erss-final-yy252-ym154/server-docker/server
    python3 run_server.py
    ```

## Debug helper
1. The programmer running this project can log into [ElephantSQL](https://customer.elephantsql.com/login) with the following account to debug:
- Email: yueyingyang22@gmail.com
- Password: 12345678xiaomila
2. The above gmail account is also the default Email sender account. The programmer can log into gmail to check the Email sending situation.
