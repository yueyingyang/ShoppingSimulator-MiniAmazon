import socket
from to_world import world_buy
from utils import getListfromStr
from exec_db import q_pkg_id, add_wh_info, find_near_wh, update_pkg_status

# The first step is always the same: import all necessary components:
import smtplib,ssl
from socket import gaierror
from getpass import getpass
from email.mime.text import MIMEText

import psycopg2
from config import config

DJANGO_HOST, DJANGO_PORT = "vcm-12347.vm.duke.edu", 23333

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE vendors (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE parts (
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE part_drawings (
                part_id INTEGER PRIMARY KEY,
                file_extension VARCHAR(5) NOT NULL,
                drawing_data BYTEA NOT NULL,
                FOREIGN KEY (part_id)
                REFERENCES parts (part_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE vendor_parts (
                vendor_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                PRIMARY KEY (vendor_id , part_id),
                FOREIGN KEY (vendor_id)
                    REFERENCES vendors (vendor_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (part_id)
                    REFERENCES parts (part_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__": 
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Setting this socket option avoids the error: Address already in use
    # https://realpython.com/python-sockets/
    listen_socket.bind((DJANGO_HOST, DJANGO_PORT))
    listen_socket.listen()
    print("============ Start to listen Django ===========")
    while True:
        django_s, addr = listen_socket.accept()
        print("================ Accept Django ================")
        data = django_s.recv(65535)
        d1 = data.decode('utf-8')
        print("---------------- Message from Django ----------")
        print(d1)
        print(type(d1))
        print(int(d1))
        print(type(int(d1)))
        #print(d2)
        #print(d3)
        print("-----------------------------------------------")

    # sender = 'yueyingyang22@gmail.com'
    # receiver = 'sif1900@outlook.com'
    # content = """From Amazon.
    #             Best regards"""
    # msg = MIMEText(content)
    # msg['From'] = sender
    # msg['To'] = receiver
    # msg['Subject'] = 'Amazon Status'

    # context=ssl.create_default_context()
    # s = smtplib.SMTP('smtp.gmail.com', 587)
    # s.starttls(context=context)
    # s.login('yueyingyang22@gmail.com', '12345678xiaomila')
    # s.sendmail(sender, receiver, msg.as_string())
    # s.quit()

