import txblock
import socket
import pickle

TCP_PORT = 5005
BUFFER_SIZE = 1024

def new_conn(ip_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_addr, TCP_PORT))
    s.listen()
    return s

def rcv_obj(socket):
    new_sock, addr = socket.accept()
    all_data = b''
    while True:
        data = new_sock.recv(BUFFER_SIZE)
        if not data:
            break
        all_data = all_data + data
    return pickle.loads(all_data)

if __name__ == '__main__':
    s = new_conn('localhost')
    new_b = rcv_obj(s)
    print(new_b.data[0])
    print(new_b.data[1])
    if new_b.is_valid():
        print('success. tx is valid')
    else:
        print('error. tx invalid')

    if new_b.data[0].inputs[0][1] == 2.3:
        print('success. input value match')
    else:
        print('error. wrong input value for block 1, tx 1')

    if new_b.data[1].inputs[0][1] == 2.3:
        print('success. input value match')
    else:
        print('error. wrong input value for block 1, tx 1')

    if new_b.data[1].inputs[1][1] == 1.0:
        print('success. input value match')
    else:
        print('error. wrong input value for block 1, tx 1')

    new_tx = rcv_obj(s)
    print(new_tx)

