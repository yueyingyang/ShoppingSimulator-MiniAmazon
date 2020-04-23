import UA_pb2
import threading
from utils import my_recv
from to_ups import ua_validated, ack_back_ups
from to_world import world_load, world_disconnect
from exec_db import update_truck_id, update_pkg_status

# Global
ups_acks = set()
ups_seq = set()

def listen_ups(ups_socket, world_socket, db, world_acks, world_seqs, ups_acks, ups_seqs):
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
            for user in command.usrVlid:
                # avoid repeated handle
                if user.seqNum in ups_seqs:
                    continue
                ups_seqs.add(user.seqNum)
                ack_back_ups(ups_socket, user.seqNum)
                ua_validated(user)
            
            for to_load in command.loadReq:
                # avoid repeated handle
                if to_load.seqNum in ups_seqs:
                    continue
                ups_seqs.add(to_load.seqNum)
                ack_back_ups(ups_socket, to_load.seqNum)
                threading.Thread(target=world_load, args=(db, world_socket, to_load.warehouseId, to_load.truckId, to_load.shipId, world_acks))  
                sid_plain_list = ()
                for sid in to_load.shipId:
                    sid_plain_list += (sid,) 
                update_truck_id(db, to_load.truckId, sid_plain_list)
            
            for delivered in command.delivery:
                # avoid repeated handle
                if delivered.seqNum in ups_seqs:
                    continue
                ups_seqs.add(delivered.seqNum)
                ack_back_ups(ups_socket, delivered.seqNum)
                update_pkg_status(db, 8, delivered.shipId)

            for _ in command.ack:
                ups_acks.add(_)

            if command.disconnection:
                world_disconnect(world_socket)
                break
                

    