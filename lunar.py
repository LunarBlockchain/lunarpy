import signatures
import pickle
import wallet
import miner
import threading
import time

wallet_list = []
miner_list = []
my_ip = 'localhost'
t_ms = None
t_nf = None

wallet_list.append((my_ip, 5006))
miner_list.append((my_ip, 5005))

def start_miner():
    global t_ms, t_nf
    try:
        my_pu = signatures.load_public("public.key")
    except:
        print('no public.key - need to generate')
    t_ms = threading.Thread(target=miner.miner_server, args=((my_ip,5005),))
    t_nf = threading.Thread(target=miner.nonce_finder, args=(wallet_list, my_pu))
    t_ms.start()
    t_nf.start()

    return True

def start_wallet():
    global t_ws
    wallet.my_private, wallet.my_public = signatures.load_keys("private.key", "public.key")
    t_ws = threading.Thread(target=wallet.wallet_server, args=((my_ip, 5006),))
    t_ws.start()
    return True

def stop_miner():
    global t_ms, t_nf
    miner.stop_all()
    if t_ms: t_ms.join()
    if t_nf: t_nf.join()
    t_ms = None
    t_nf = None
    return True

def stop_wallet():
    global t_ws
    wallet.stop_all()
    if t_ws:
        t_ws.join()
    t_ws = None
    return True

def get_balance(pu_key):
    if not t_ws:
        print('start the server by calling start wallet before checking balances')
        return 0.0
    return wallet.get_balance(pu_key)
def send_coins(pu_rcv, amt, tx_fee):
    wallet.send_coins(wallet.my_public, amt + tx_fee, wallet.my_private, pu_rcv,
                      amt, miner_list)
    return True

def make_new_keys():
    return None, None

if __name__ == '__main__':
    start_miner()
    start_wallet()
    other_public = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzXdhesONi//34lKdMNmM\naJR6suxxmGPSdqA0vDNfejhCQHojQJzN+U14DoxEsxu4C0Fd0v1/G09Hqfwk61Lm\nfpK7yryFVg5zGVgyqbBOE0PVUjqyIXenUOJYPIl1CLrWLf682SXiIwAzlGDHInTa\nbpHQXap2lxjf8BqppHSL72jK50lcvtPBRYDv+mMdVA8sGHXW5OQtdga/AtC0c8R5\nS8PBGGrKYcLsH+ZDDqAjWwD0ZLkvTpY5ddcCxyPzu+E3BrpakozMqPjqIylQphCe\nLnkbdJ+dfo8KDG4fIEQYAHyDlNCkblDl8objaxBW0KXjh4wqKMnehj82Nxk/z6Gw\nxwIDAQAB\n-----END PUBLICKEY-----\n'
    time.sleep(2)
    print(get_balance(wallet.my_public))
    send_coins(other_public, 1.0, 0.1)
    time.sleep(20)
    print(get_balance(other_public))
    print(get_balance(wallet.my_public))

    time.sleep(1)
    stop_wallet()
    stop_miner()