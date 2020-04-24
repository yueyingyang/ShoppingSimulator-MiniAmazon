import socket
import psycopg2



def init_ups_socket(UPS_HOST, UPS_PORT):
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Setting this socket option avoids the error: Address already in use
    # https://realpython.com/python-sockets/
    listen_socket.bind((UPS_HOST, UPS_PORT))
    listen_socket.listen()
    ups_socket, addr = listen_socket.accept()
    print('Connected by', addr)
    
    return ups_socket

def connect_db():
    db = psycopg2.connect(
        database="amazon",
        user="postgres",
        password="abc123",
        host="127.0.0.1",
        port="5432",
    )
    print("================ Connected to DB ==============\n")
    return db