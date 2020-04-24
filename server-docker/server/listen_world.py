import UA_pb2
import world_amazon_pb2 
import threading
from utils import my_recv, my_send, parse_list_to_str
from to_world import recv_world, ack_back_world, world_pack
from to_ups import au_pickup, au_deliver
from exec_db import q_pkg_by_item, update_pkg_status, q_pkg_id


buyseq_shipid = dict()
shipid = 0

def listen_world(world_socket, ups_socket, db, world_acks, world_seqs, ups_acks, ups_seqs):
    global buyseq_shipid 

    print("========== Start to listen the world ==========\n")
    while True:
        try:
            response = recv_world(world_socket)
        except Exception as e:
            print("-------------- World Recv Failure ------------\n")
            break
        if response is not None: 
            print("---------------- Message from world ----------")
            print(response)
            print("-----------------------------------------------")
            if response.finished:
                print("End world.")
            
            for _ in response.acks:
                world_acks.add(_)
                print(world_acks)

            for come_error in response.error:
                print("come_error")

            for come_arrived in response.arrived: # repeated APurchaseMore arrived = 1;
                # ack back to world
                ack_back_world(world_socket, come_arrived.seqnum)
                # avoid handle same message
                if come_arrived.seqnum in world_seqs:
                    continue
                world_seqs.add(come_arrived.seqnum)
                print("Receive arrived")
                '''
                1. Update pkg status to PURCHASING
                    1.1 q_pkg_by_item
                '''
                pkg_id = q_pkg_by_item(db, parse_list_to_str(come_arrived.things))
                update_pkg_status(db, 2, (pkg_id,))
                '''
                2. Send world APack
                3. Update status to PACKING
                '''
                threading.Thread(target=world_pack, args=(db, world_socket, world_acks, come_arrived.whnum, come_arrived.things, pkg_id)).start()
                update_pkg_status(db, 3, (pkg_id,))
            
            for come_ready in response.ready: # repeated APacked ready = 2;
                ack_back_world(world_socket, come_ready.seqnum)
                if come_ready.seqnum in world_seqs:
                    continue
                world_seqs.add(come_ready.seqnum)
                # If pkg is cancelled, dont send pick up.
                if q_pkg_id(db, come_ready.shipid)[5] == 9:
                    continue
                # update status to packed
                update_pkg_status(db, 4, (come_ready.shipid,))
                # tell ups to pickup
                print("tell ups to pickup")
                threading.Thread(target=au_pickup, args=(db, ups_socket, come_ready.shipid, ups_acks)).start()
                # au_pickup(db, ups_socket, come_ready.shipid, ups_acks)

            
            for come_loaded in response.loaded: # repeated ALoaded loaded = 3;
                ack_back_world(world_socket, come_loaded.seqnum)
                if come_loaded.seqnum in world_seqs:
                    continue
                world_seqs.add(come_loaded.seqnum)
                # update status to loaded
                update_pkg_status(db, 6, (come_loaded.shipid,))
                # tell ups to deliver
                print("tell ups to deliver")
                threading.Thread(target=au_deliver, args=(db, ups_socket, come_loaded, ups_acks)).start()
                
                


            '''
            Maybe unnecessay
            '''
            for come_packagestatus in response.packagestatus:
                ack_back_world(world_socket, come_packagestatus.seqnum)
                # tell world query
                packageid = come_packagestatus.packageid
                status = come_packagestatus.status
                # abstract and send back to front-end

