import UA_pb2
import threading
from utils import my_recv, send_email
from to_ups import ua_validated, ack_back_ups
from to_world import world_load, world_disconnect
from exec_db import update_truck_id, update_pkg_status, q_email_by_sid

# Global
ups_acks = set()
ups_seq = set()

def listen_ups(ups_socket, world_socket, db, world_acks, world_seqs, ups_acks, ups_seqs, email_socket, email_sender):
    print("=============== Start to listen UPS ===========\n")
    while True:
        try:
            response = my_recv(ups_socket)
        except Exception as e:
            print("---------------- UPS Recv Failure -------------\n")
            break
        
        if response is not None:
            command = UA_pb2.UtoACommand()
            command.ParseFromString(response)
            print("---------------- Receive from UPS -------------\n")
            print(command)
            print("-----------------------------------------------\n")
            for _ in command.ack:
                ups_acks.add(_)
                
            for user in command.usrVlid:
                # avoid repeated handle
                ack_back_ups(ups_socket, user.seqNum)
                if user.seqNum in ups_seqs:
                    continue
                ups_seqs.add(user.seqNum)
                ua_validated(db, world_socket, user, ups_acks, world_acks, email_socket, email_sender)
            
            for to_load in command.loadReq:
                # avoid repeated handle
                ack_back_ups(ups_socket, to_load.seqNum)
                if to_load.seqNum in ups_seqs:
                    continue
                ups_seqs.add(to_load.seqNum)
                threading.Thread(target=world_load, args=(db, world_socket, to_load.warehouseId, to_load.truckId, to_load.shipId, world_acks)).start() 
                sid_plain_list = ()
                for sid in to_load.shipId:
                    sid_plain_list += (sid,) 
                update_truck_id(db, to_load.truckId, sid_plain_list)
            
            for delivered in command.delivery:
                # avoid repeated handle
                ack_back_ups(ups_socket, delivered.seqNum)
                if delivered.seqNum in ups_seqs:
                    continue
                ups_seqs.add(delivered.seqNum)
                update_pkg_status(db, 8, delivered.shipId)
                receiver = q_email_by_sid(db, delivered.shipId)
                pkg_status = 'DELIVERED.'
                send_email(receiver, delivered.shipId, pkg_status, email_socket, email_sender)


            if command.disconnection:
                world_disconnect(world_socket)
                break
                

    