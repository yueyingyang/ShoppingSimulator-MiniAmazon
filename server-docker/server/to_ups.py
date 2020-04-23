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
from utils import my_recv, my_send, getListfromStr
from to_world import world_load, world_buy
from exec_db import q_pkg_id, update_pkg_status, find_near_wh, add_wh_info

RESEND_INTERVAL = 10
shiptruck_dict = dict()

def infinite_sequence():
    num = 100
    while True:
        yield num
        num += 1
gen = infinite_sequence()

def send_ups(ups_socket, au_command, seqnum, ups_acks):
    while seqnum not in ups_acks:
        print("------------------ Send to UPS ----------------")
        my_send(ups_socket, au_command)
        time.sleep(RESEND_INTERVAL)

def ack_back_ups(ups_socket, seqnum):
    ack_command = UA_pb2.AtoUCommand()
    ack_command.ack.append(seqnum)
    print("---------------- ACK back to UPS --------------")
    my_send(ups_socket, ack_command)
    

def ua_connect(ups_socket):
    response = my_recv(ups_socket)
    command = UA_pb2.UtoACommand()
    command.ParseFromString(response)
    for conn in command.connection:
        ack_back_ups(ups_socket, conn.seqNum)
        print(conn)
        recv_world_id = conn.worldId
        return recv_world_id


def au_validate(ups_socket, ups_acks, ups_acc, sid):
    seqnum = next(gen)
    val_user = UA_pb2.AtoUCommand()
    val_user.usrVlid.add(seqNum=seqnum, UPSaccount=ups_acc, shipId=sid)
    send_ups(ups_socket, val_user, seqnum, ups_acks)


def ua_validated(db, world_socket, user, ups_acks, world_acks):
    # Check if result
    # If True, purchase
    pkg_id = user.shipId
    if user.result:
        pkg_info = q_pkg_id(db, pkg_id)
        # IF pkg is related to ups account, then turn to validate
        item_str = pkg_info[4]
        whnum = find_near_wh(db, pkg_info[2], pkg_info[3])
        add_wh_info(db, pkg_id, whnum)
        # update_pkg_whinfo()
        '''
        1. Split item_str into purchase list (utils)
        2. Assign warehouse info
        3. Send world_buy
        '''
        purchase_list = getListfromStr(item_str)
        update_pkg_status(db, 1, (pkg_id,))
        world_buy(world_socket, whnum, purchase_list, world_acks)       
    else:
        # If False, update status to cancel
        update_pkg_status(db, 9, (user.shipId,))
    
    


def au_pickup(db, ups_socket, shipId, ups_acks):
    seqnum = next(gen)
    au_command = UA_pb2.AtoUCommand()  
    # find wh/x/y/buystr from db
    pickup = au_command.pikReq.add()
    pkg = q_pkg_id(db, shipId)
    print(pkg)
    pickup.seqNum = seqnum
    pickup.warehouseId = pkg[8]
    newship = pickup.shipment.add()
    newship.shipId = shipId
    if pkg[6] is not None:
        newship.UPSaccount = pkg[6]
    # parse purchase_list
    buy = getListfromStr(pkg[4])
    for item in buy:
        newship.products.add(description = item['description'], count = item['count'])
    newship.destination_x = pkg[2]
    newship.destination_y = pkg[3]
    # send to ups
    send_ups(ups_socket, au_command, seqnum, ups_acks)


def au_deliver(db, ups_socket, loaded, ups_acks):
    ship_list = [loaded.shipid]
    # shipinfo
    for sid in ship_list:
        deliver = UA_pb2.AtoUCommand()
        seqnum = next(gen)
        deliver.loadReq.add(seqNum=seqnum, shipId=ship_list, truckId=q_pkg_id(db, sid)[1])   
        send_ups(ups_socket, deliver, seqnum, ups_acks)
    # update status to delivering 
    update_pkg_status(db, 7, (loaded.shipid,))
        
