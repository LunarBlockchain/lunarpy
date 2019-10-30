import socket
import pickle
import select

TCP_PORT = 5005
BUFFER_SIZE = 1024

def new_server_connection(ip_addr, port=TCP_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_addr, port))
    s.listen()
    return s

def rcv_obj(socket):
   # inputs, outputs, errors = select.select([socket], [], [socket], 6)
    #if socket in inputs:
    #    new_sock, addr = socket.accept()
     #   all_data = b''
     #   while True:
      #      data = new_sock.recv(BUFFER_SIZE)
       #     if not data:
      #          break
      #      all_data = all_data + data
      #  return pickle.loads(all_data)
   # return None
    new_sock,addr = socket.accept()
    all_data = b''
    while True:
        data = new_sock.recv(BUFFER_SIZE)
        if not data: break
        all_data = all_data + data
    return pickle.loads(all_data)

def send_obj(ip_addr, in_obj, port=TCP_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_addr, port))
    data = pickle.dumps(in_obj)
    s.send(data)
    s.close()
    return False

if __name__ == '__main__':
    server = new_server_connection('localhost')
    o = rcv_obj(server)
    print('success.') #if returns after time, then successful
    print(o)
    server.close()
