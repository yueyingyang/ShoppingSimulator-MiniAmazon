import socket
import psycopg2
import smtplib,ssl
from socket import gaierror
from getpass import getpass



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
    # db = psycopg2.connect(
    #     database="amazon",
    #     user="postgres",
    #     password="abc123",
    #     host="127.0.0.1",
    #     port="5432",
    # )
    db = psycopg2.connect(
        database="fslryadt",
        user="fslryadt",
        password="buIwYtkXY2Anx2m0uo1HlRZUgTD51B1k",
        host="drona.db.elephantsql.com",
        port="5432",
    )
    print("================ Connected to DB ==============\n")
    return db

def setup_email():
    try:
        context=ssl.create_default_context()
        sender = 'yueyingyang22@gmail.com'
        s = smtplib.SMTP(host = 'smtp.gmail.com', port = 587, timeout=7200)
        s.starttls(context=context)
        s.login(sender, '12345678xiaomila')
        return s, sender  
    except smtplib.SMTPException as e:
        print(e)
        print("smtplib.SMTPException")
        pass
    except smtplib.socket.error as e:
        print("smtplib.socket.error")
        pass 
