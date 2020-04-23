import world_amazon_pb2 
import socket
import threading
import psycopg2
import time
import smtplib
from random import randint
from email.mime.text import MIMEText
from email.header import Header
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

from utils import my_send, my_recv
from exec_db import update_pkg_status

SIMSPEED = 30000 * 3000
RESEND_INTERVAL = 10

def infinite_sequence():
    num = 100
    while True:
        yield num
        num += 1
gen = infinite_sequence()

def send_world(world_socket, world_command, seqnum, world_acks):
    while not seqnum in world_acks:
        print("----------------- Send to World ---------------")
        time.sleep(RESEND_INTERVAL)
        my_send(world_socket, world_command)

# call when user check out from django
def world_buy(world_socket, whnum, purchase_list, world_acks):
    seqnum = next(gen)
    # repeated APurchaseMore buy = 1;
    world_command = world_amazon_pb2.ACommands() 
    go_buy = world_command.buy.add()
    go_buy.whnum = whnum
    go_buy.seqnum = seqnum
    for item in purchase_list:
        product_command = go_buy.things.add(
            id = item['item_id'], description = item['description'], count = item['count'])
    world_command.simspeed = SIMSPEED
    send_world(world_socket, world_command, seqnum, world_acks)
    


def world_pack(db, world_socket, world_acks, whnum, thing, shipid):

    seqnum = next(gen)
    # repeated APack topack = 2;
    world_command = world_amazon_pb2.ACommands() 
    go_pack = world_command.topack.add()
    go_pack.whnum = whnum
    go_pack.shipid = shipid
    go_pack.seqnum = seqnum
    for item in thing:
        go_pack.things.add(id=item.id, description=item.description,count=item.count)
    world_command.simspeed = SIMSPEED
    my_send(world_socket, world_command)
    send_world(world_socket, world_command, seqnum, world_acks)
    # updatre status to packing
    update_pkg_status(db, 3, (shipid,))

    


def world_load(db, world_socket, whnum, truckid, sid_list, world_acks):
    for sid in sid_list:
        world_command = world_amazon_pb2.ACommands()
        seqnum = next(gen)
    # repeated APutOnTruck load = 3;
        go_load = world_command.load.add()
        go_load.whnum = whnum
        go_load.truckid = truckid
        go_load.shipid = sid
        go_load.seqnum = seqnum
        send_world(world_socket, world_command, seqnum, world_acks)
        # update status to loading
        update_pkg_status(db, 5, (sid,))

def world_disconnect(world_socket):
    world_command = world_amazon_pb2.ACommands()
    world_command.finished = True
    my_send(world_socket, world_command)
    
# call when user check status from django
def world_query(world_socket, world_command, shipid):
    seqnum = next(gen)
    query = world_command.queries.add()
    query.packageid = shipid
    query.seqnum = seqnum


def ack_back_world(world_socket, seqNum):
    world_command = world_amazon_pb2.ACommands()
    world_command.acks.append(seqNum)
    print("---------------- ACK back to world ------------")
    my_send(world_socket, world_command)
    print(world_command)
    print("-----------------------------------------------")


### 2. AConnect & 3. AConnected - Connect to world
def connect_world(WORLD_HOST, WORLD_PORT):
    world_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    world_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        try:
            world_socket.connect((WORLD_HOST, WORLD_PORT))
            print('================ Conn to World ================\n')
            return world_socket
        except:
            print('============ Failed to connect to World ==========\n')
            continue    


def connect_world_id(socket, id, wh_info):
    worldConnection = world_amazon_pb2.AConnect()
    if id:
        worldConnection.worldid = int(id)
    worldConnection.isAmazon = True
    for wh in wh_info:
        worldConnection.initwh.add(id=wh['id'], x=wh['x'], y=wh['y'])
    print(worldConnection)
    my_send(socket, worldConnection)

    command = world_amazon_pb2.AConnected()
    command.ParseFromString(my_recv(socket))
    print(command)
    return command.result
    
# recv command from world.
def recv_world(socket):
    response = world_amazon_pb2.AResponses()
    response.ParseFromString(my_recv(socket))
    print("---------------- Recv from World --------------\n")
    print(response)
    print("-----------------------------------------------\n")
    return response 

# Process:
# // when to connect to database and to AInitWarehouse?
#   CONNECT: UPS - 1. UtoAConnect
#   CONNECT: World - 2. AConnect - 3. AConnected 
#   VALIDATE: UPS - 4. send UserValidationRequest - 5. recv UserValidationResponse 
#   BUY: World - 6. send APurchaseMore(buy) - 7. recv APurchaseMore(arrived)
#   PACK: World - send APack - recv APacked
#   PICKUP: UPS - send AtoUPickupRequest - recv UtoALoadRequest
#   LOAD: World - send APutOnTruck - recv ALoaded
#   Deliver: UPS - recv Delivery


"""
# world handler
def to_world(world_socket, UPS_socket, whnum, purchase_list, shipid, truckid):
    global amazon_seq
    global world_seq
    global COMMAND
    # shipid: created by Amazon from package table
    # truckid: told by UPS when they arrive warehouse
    world_command = world_amazon_pb2.ACommands()
#   BUY: World - 6. send APurchaseMore(buy) - 7. recv APurchaseMore(arrived) 买
    world_buy(world_socket, world_command, whnum, purchase_list, world_seq)
#   PACK: World - send APack - recv APacked 打包
    world_pack_res = world_pack(world_socket, world_command, whnum, shipid, world_seq, purchase_list)
#   LOAD: World - send APutOnTruck - recv ALoaded 装车
    world_load_res = world_load(world_socket, world_command, whnum, truckid, shipid, world_seq)
#   send command to world
    my_send(world_socket, world_command)
#   recv response from world
    world_response = recv_world(world_socket)
"""