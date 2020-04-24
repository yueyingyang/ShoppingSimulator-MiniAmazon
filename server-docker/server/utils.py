import world_amazon_pb2 
from email.mime.text import MIMEText
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

# recv message
def my_recv(socket):
    buffer = []
    while True:
        buf = socket.recv(1)
        buffer += buf
        size, pos = _DecodeVarint32(buffer, 0) 
        if pos != 0:
            break
    message = socket.recv(size)
    return message

# send message
def my_send(s, message):
    print("------------------ Send Message ---------------")
    print(message)
    hdr = []
    _EncodeVarint(hdr.append, len(message.SerializeToString()), None)
    s.sendall(b"".join(hdr))
    s.sendall(message.SerializeToString())
    print("-----------------------------------------------")


# send ack to world
def ack_world(world_socket, seqnum):
    world_command = world_amazon_pb2.ACommands()
    world_command.acks.append(seqnum)
    my_send(world_socket, world_command)

# Parse message AProduct
def parse_list_to_str(things):
    item_list = []
    for item in things:
        item_str = ','.join([str(item.id), item.description, str(item.count)])
        item_list.append(item_str)
    print(';'.join(item_list))
    return ';'.join(item_list)


# Split item_str into purchase list 
def getListfromStr(item_str):
    item_list = item_str.split(';')
    purchase_list = []
    for item_info in item_list:
        item_detail = item_info.split(',')
        item = dict()
        item['item_id'] = int(item_detail[0])
        item['description'] = item_detail[1]
        item['count'] = int(item_detail[2])
        purchase_list.append(item)
    return purchase_list
    '''
    Sample purchase list
    purchase_list = [{
        'item_id':1,
        'description':'Apple',
        'count':2
    },{
        'item_id':2,
        'description':'Banana',
        'count':3
    },{
        'item_id':3,
        'description':'Milk',
        'count':4
    }]
    '''

def send_email(receiver, id, status, socket, sender):
    email_socket = socket
    email_sender = sender
    content = """Thank you for choosing Yi & Yueying \'s Amazon.
                Best regards"""
    msg = MIMEText(content)
    msg['From'] = email_sender
    msg['To'] = receiver
    msg['Subject'] = 'Your pakage #' + str(id) + ' is ' + status
    email_socket.sendmail(email_sender, receiver, msg.as_string())
