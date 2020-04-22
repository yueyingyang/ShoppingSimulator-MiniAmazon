# Import Library
import socket
import threading
import time
from random import randint
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

# Import other 
import UA_pb2
import world_amazon_pb2 
from utils import my_recv, my_send
from toWorld import world_load

RESEND_INTERVAL = 5
shiptruck_dict = dict()
debug_shipid = -1

def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1
gen = infinite_sequence()

    
def ack_back_ups(ups_socket, seqnum):
    ack_command = UA_pb2.AtoUCommand()
    ack_command.ack.append(seqnum)
    print(ack_command)
    my_send(ups_socket, ack_command)

    
def ua_connect(ups_socket):
    response = my_recv(ups_socket)
    command = UA_pb2.UtoACommand()
    command.ParseFromString(response)
    conns = command.connection
    for conn in conns:
        print(conn)
        # ack_back_ups(ups_socket, conn.seqNum)
        recv_world_id = conn.worldId
        return recv_world_id


def au_validate(ups_socket, ups_acc):
    seqnum = next(gen)
    val_user = UA_pb2.AtoUCommand()
    val_user.usrVlid.add(seqnum=seqnum, UPSaccount=ups_acc)
    my_send(ups_socket, val_user)

    # while seqnum not in acks:
    #     time.sleep(RESEND_INTERVAL)
    #     my_send(ups_socket, val_user)

def ua_validated(user):
    # ack_back_ups(user.seqnum)
    # todo: call world to pack
    print("send validate")


def au_pickup(ups_socket, shipId, ship_info):
    #todo: q_pkg_id
    global debug_shipid
    seqnum = next(gen)
    pickup = UA_pb2.AtoUCommand()
    ship_list = []
    prods_list = []
    # pickup.pikReq.shipment.products
    for prod in ship_info.things:
        item = UA_pb2.Product(description=prod.description, count=prod.count)
        prods_list.append(item)
    # pickup.pikReq.shipment.products 
    ship = UA_pb2.ShipInfo(shipId=shipId, products=prods_list, 
                                destination_x=1,destination_y=1)
    ship_list.append(ship) # pickup.pickReq.shipment
    pickup.pikReq.add(seqNum=seqnum, warehouseId=ship_info.whnum, shipment=ship_list)
    # pickup.pickReq
    my_send(ups_socket, pickup)    
    debug_shipid = shipId
    # while seqnum not in acks:
    #     time.sleep(RESEND_INTERVAL)
    #     my_send(ups_socket, pickup)


def ua_toload(world_socket, load):
    print("send to load")
    # ack_back_ups(load.seqnum)
    shiptruck_dict[debug_shipid] = load.truckId
    world_load(world_socket, load.warehouseId, load.truckId, debug_shipid)
    

def au_deliver(ups_socket, loaded, shipinfo):
    seqnum = next(gen)
    ship_list = [loaded.shipid]
    deliver = UA_pb2.AtoUCommand()
    deliver.loadReq.add(seqNum=seqnum, shipId=ship_list, truckId=shiptruck_dict[loaded.shipid])
    my_send(ups_socket, deliver)    

    # while seqnum not in acks:
    #     time.sleep(RESEND_INTERVAL)
    #     my_send(ups_socket, deliver)


def ua_delivered(delivered):
    # ack_back_ups(delivered.seqnum)
    # todo: update db
    print("send delivered")