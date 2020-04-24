from random import random, randint

def update_truck_id(db, tid, sid_list):
    cursor = db.cursor()
    cursor.execute('UPDATE "frontEndServer_package" SET "truck_id" = %s WHERE "id" = %s', (tid, sid_list))
    db.commit()   
    print('[INFO][UPDATE PACKAGE][TRUCK_ID] %s TO [%s]', sid_list, tid)

def select_dist(e):
    return e['dist']

def find_near_wh(db, x, y):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM "frontEndServer_warehouse"')
    wh_list = cursor.fetchall()
    dist_list = []
    for wh in wh_list:
        dist = {}
        dist['whnum'] = wh[0]
        dist['dist'] = ((wh[1] - x) ** 2) + ((wh[2] - y) ** 2)
        dist_list.append(dist)
    dist_list.sort(key=select_dist)
    return dist_list[0]['whnum']

def update_pkg_status(db, status, pkg_id_list):
    cursor = db.cursor()
    cursor.execute('UPDATE "frontEndServer_package" SET "status" = %s WHERE "id" = %s', (status, pkg_id_list))
    db.commit()
    print('[INFO][UPDATE PACKAGE] %s TO [%s]', pkg_id_list, status)

def q_pkg_by_item(db, item_str):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM "frontEndServer_package" WHERE item_str = %s AND status = %s', ((item_str,), (1,)))
    result = cursor.fetchall()
    # Check status == Purchasing
    assert(result[0][5] == 1)
    return result[0][0]

def add_wh_info(db, pkg_id, whnum):
    cursor = db.cursor()
    cursor.execute('UPDATE "frontEndServer_package" SET "wh_id" = %s WHERE "id" = %s', (whnum, (pkg_id,)))
    db.commit()

def q_pkg_id(db, pkg_id):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM "frontEndServer_package" WHERE id = %s', (pkg_id,))
    result = cursor.fetchall()
    print(result[0])
    return result[0]

def init_wh(db, NUM_WH):
    clear_wh(db)
    wh_list = []
    for _ in range(NUM_WH):
        wh_list.append({})
        wh_list[_]['x'] = randint(0, 100)
        wh_list[_]['y'] = randint(0, 100)
        wh_list[_]['id'] = insert_wh(db, wh_list[_]['x'], wh_list[_]['y'])
    return wh_list  

def clear_wh(db):
    cursor = db.cursor()
    cursor.execute('TRUNCATE "frontEndServer_warehouse" CASCADE')
    db.commit()

def insert_wh(db, x, y):
    cursor = db.cursor()
    cursor.execute('INSERT INTO "frontEndServer_warehouse" (x, y) VALUES (%s, %s) RETURNING id', (x, y))
    whnum = cursor.fetchone()[0]
    db.commit()
    return whnum


def q_prime_by_sid(db, sid):
    user = q_pkg_id(db, sid)[7]
    cursor = db.cursor()
    cursor.execute('SELECT * FROM "frontEndServer_my_user" WHERE id = %s', (user,))
    result = cursor.fetchall()
    # X is the index of prime
    print(result[0][11])
    return result[0][11]  