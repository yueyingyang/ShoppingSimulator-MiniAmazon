import UA_pb2
from utils import my_recv
from toUps import ua_validated, ua_toload, ua_delivered

# Global
ups_acks = set()
ups_seq = set()

def listen_ups(ups_socket, world_socket):
    print("=============== Start to listen UPS ===========\n")
    while True:
        response = my_recv(ups_socket)
        command = UA_pb2.UtoACommand()
        command.ParseFromString(response)
        if response is not None:
            print("---------------- Receive from UPS -------------\n")
            print(command)
            print("-----------------------------------------------\n")
            if command.connection:
                return command.connection
            for user in command.usrVlid:
                ua_validated(user)
            for to_load in command.loadReq:
                ua_toload(world_socket, to_load)
            for delivered in command.delivery:
                ua_delivered(delivered)
            for _ in command.ack:
                ups_acks.add(_)
    

    