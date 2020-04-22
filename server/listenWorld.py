import UA_pb2
import world_amazon_pb2 
from utils import my_recv, my_send, parse_list_to_str
from toWorld import recv_world, ack_back_world, world_pack
from toUps import au_pickup, ua_toload, au_deliver
from execTable import q_pkg_by_item, update_pkg_status


buyseq_shipid = dict()
shipid = 0

def listen_world(socket, ups_socket, db, world_acks, world_seqs):
    global buyseq_shipid 

    print("================Start to listen the world======\n")
    while True:
        # world_command_updated = True
        response = recv_world(socket)
        world_command = world_amazon_pb2.ACommands()
        if response is not None: 
            if response.finished:
                print("End world.")
            
            for _ in response.acks:
                world_acks.add(_)

            for come_error in response.error:
                print("come_error")

            for come_arrived in response.arrived: # repeated APurchaseMore arrived = 1;
                # ack back to world
                ack_back_world(socket, come_arrived.seqnum)
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
                world_pack(socket, come_arrived.whnum, come_arrived.things, pkg_id)
                update_pkg_status(db, 3, (pkg_id,))
            
            for come_ready in response.ready: # repeated APacked ready = 2;
                ack_back_world(socket, come_ready.seqnum)
                # update status to packed
                update_pkg_status(db, 4, (come_ready.shipid,))
                # tell ups to pickup
                print("tell ups to pickup")
                au_pickup(ups_socket, come_ready.shipid)

            
            for come_loaded in response.loaded: # repeated ALoaded loaded = 3;
                ack_back_world(socket, come_loaded.seqnum)
                # update status to loaded
                update_pkg_status(db, 6, (come_loaded.shipid,))
                # tell ups to deliver
                print("tell ups to deliver")
                au_deliver(ups_socket, come_loaded, buyseq_shipid[come_loaded.shipid])
                # update status to delivering 
                '''
                wired
                '''
                update_pkg_status(db, 7, (come_loaded.shipid,))


            '''
            Maybe unnecessay
            '''
            for come_packagestatus in response.packagestatus:
                ack_back_world(socket, come_packagestatus.seqnum)
                # tell world query
                packageid = come_packagestatus.packageid
                status = come_packagestatus.status
                # abstract and send back to front-end

