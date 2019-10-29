import txblock
import transaction
import signatures
import pickle
import socket

TCP_PORT = 5005

def send_block(ip_addr, blk):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_addr, TCP_PORT))
    data = pickle.dumps(blk)
    s.send(data)
    s.close()
    return False


if __name__ == '__main__':
    pr1, pu1 = signatures.generate_keys()
    pr2, pu2 = signatures.generate_keys()
    pr3, pu3 = signatures.generate_keys()

    Tx1 = transaction.Tx()
    Tx1.add_input(pu1, 2.3)
    Tx1.add_output(pu2, 1.0)
    Tx1.add_output(pu3, 1.1)
    Tx1.sign(pr1)

    Tx2 = transaction.Tx()
    Tx2.add_input(pu3, 2.3)
    Tx2.add_input(pu2, 1.0)
    Tx2.add_output(pu1, 3.1)
    Tx2.sign(pr2)
    Tx2.sign(pr3)

    B1 = txblock.TxBlock(None)
    B1.add_tx(Tx1)
    B1.add_tx(Tx2)

    send_block('localhost', B1)
    send_block('localhost', Tx1)

