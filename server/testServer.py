import UA_pb2
import world_amazon_pb2 
import threading
import socket
from random import random, randint
from init import connect_db, init_ups_socket
from execTable import init_wh
from toWorld import connect_world, connect_world_id
from toUps import ua_connect, au_validate
from listenWorld import listen_world
from listenUps import listen_ups
from listenDjango import listen_django

UPS_HOST, UPS_PORT = "vcm-12347.vm.duke.edu", 5555
WORLD_HOST, WORLD_PORT = "vcm-12347.vm.duke.edu", 23456
DJANGO_HOST, DJANGO_PORT = "vcm-12347.vm.duke.edu", 23333


NUM_WH = 3

if __name__ == "__main__":

    # Global variable
    global wh_info
    global ups_socket
    global world_socket
    global db
    global world_acks
    global world_seqs
    world_acks = set()
    world_seqs = set()
    ups_acks = set()
    ups_seqs = set()

    # Connect to database
    db = connect_db()

    # Connect to ups and receive world id.
    ups_socket = init_ups_socket(UPS_HOST, UPS_PORT)
    world_id = ua_connect(ups_socket)

    # Connect to world
    world_socket = connect_world(WORLD_HOST, WORLD_PORT)
    wh_info = init_wh(db, NUM_WH)
    connect_world_id(world_socket, world_id, wh_info)

    # Start listen
    with ups_socket, world_socket, db:
        # todo: How to select wh.

        # record the shipid with APurchase:buy command as a dict

        # Listen 2 socket.
        listenWorld = threading.Thread(target=listen_world, args=(world_socket, ups_socket, db, world_acks, world_seqs, ups_acks, ups_seqs))
        listenWorld.start()
        listenUps = threading.Thread(target=listen_ups, args=(ups_socket, world_socket, db, world_acks, world_seqs, ups_acks, ups_seqs))
        listenUps.start()
        listenDjango = threading.Thread(target=listen_django, args=(DJANGO_HOST, DJANGO_PORT, world_socket, ups_socket, db, world_acks,))
        listenDjango.start()

        while True:
            pass
