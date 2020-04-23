import UA_pb2
from utils import my_recv
from toUps import ua_validated, ack_back_ups
from toWorld import world_load
from execTable import update_truck_id, update_pkg_status

# Global
ups_acks = set()
ups_seq = set()

def listen_ups(ups_socket, world_socket, db, world_acks, world_seqs, ups_acks, ups_seqs):
    print("=============== Start to listen UPS ===========\n")
    while True:
        response = my_recv(ups_socket)
        command = UA_pb2.UtoACommand()
        command.ParseFromString(response)
        if response is not None:
            print("---------------- Receive from UPS -------------\n")
            print(command)
            print("-----------------------------------------------\n")
            for user in command.usrVlid:
                # avoid repeated handle
                if user.seqnum in ups_seqs:
                    continue
                ups_seqs.add(user.seqnum)

                ack_back_ups(ups_socket, user.seqNum)
                ua_validated(user)
            for to_load in command.loadReq:
                # avoid repeated handle
                if to_load.seqnum in ups_seqs:
                    continue
                ups_seqs.add(to_load.seqnum)

                ack_back_ups(ups_socket, to_load.seqNum)
                world_load(db, world_socket, to_load.warehouseId, to_load.truckId, to_load.shipId, world_acks)
                
                update_truck_id(db, to_load.truckId, to_load.shipId)
            for delivered in command.delivery:
                # avoid repeated handle
                if delivered.seqnum in ups_seqs:
                    continue
                ups_seqs.add(delivered.seqnum)

                ack_back_ups(ups_socket, delivered.seqNum)
                update_pkg_status(db, 8, delivered.shipId)

            for _ in command.ack:
                ups_acks.add(_)
    

    