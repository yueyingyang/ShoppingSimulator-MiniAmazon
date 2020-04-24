import socket
from to_world import world_buy
from to_ups import au_validate
from utils import getListfromStr, send_email
from exec_db import q_pkg_id, add_wh_info, find_near_wh, update_pkg_status, q_email_by_sid


def listen_django(D_HOST, D_PORT, world_socket, ups_socket, db, world_acks, ups_acks, email_socket, email_sender):
            
    ########## Just for testing: Insert a new package
    # cursor = db.cursor()
    # cursor.execute('INSERT INTO "frontEndServer_package" (item_str, addr_x, addr_y, status) VALUES (%s, %s, %s, %s) RETURNING id', ("1,Apple,2;2,Banana,3;3,Milk,4", 4, 2, 0))
    # pkg_id = cursor.fetchone()[0]
    # db.commit()
    # print("pkg_id: ")
    # print(pkg_id)
    # pkg_info = q_pkg_id(db, pkg_id)
    # if pkg_info[7] is not None:
    #     au_validate(ups_socket, pkg_info[7])
    #     return
    # item_str = pkg_info[4]
    # whnum = find_near_wh(db, pkg_info[2], pkg_info[3])
    # add_wh_info(db, pkg_id, whnum)
    # purchase_list = getListfromStr(item_str)
    # update_pkg_status(db, 1, (pkg_id,))
    # world_buy(world_socket, whnum, purchase_list, world_acks)
    
    ##########
    
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Setting this socket option avoids the error: Address already in use
    # https://realpython.com/python-sockets/
    listen_socket.bind((D_HOST, D_PORT))
    listen_socket.listen()
    print("============ Start to listen Django ===========")
    while True:
        django_s, addr = listen_socket.accept()
        print("================ Accept Django ================")

        '''
        1. Recieve pkg_id
        2. Select * from t where pkg_id (execTable)
            2.1 Check status == Created
            2.2 Get item_str
        '''
        data = django_s.recv(65535)
        d1 = data.decode('utf-8')
        print("---------------- Message from Django ----------")
        print(d1)
        print("-----------------------------------------------")
        pkg_id = int(d1)
        receiver = q_email_by_sid(db, pkg_id)
        pkg_status = 'CREATED.'
        send_email(receiver, pkg_id, pkg_status, email_socket, email_sender)
        pkg_info = q_pkg_id(db, pkg_id)
        # IF pkg is related to ups account, then turn to validate
        if pkg_info[6] is not None:
            au_validate(ups_socket, ups_acks, pkg_info[6], pkg_info[0])
            continue
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


