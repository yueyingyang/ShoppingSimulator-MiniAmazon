import socket
from to_world import world_buy
from utils import getListfromStr
from exec_db import q_pkg_id, add_wh_info, find_near_wh, update_pkg_status

DJANGO_HOST, DJANGO_PORT = "vcm-12347.vm.duke.edu", 23333

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
