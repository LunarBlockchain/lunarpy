import socketutils
import transaction
import txblock
import pickle

head_blocks = [None]
wallet_list = [('localhost', 5006)]
miner_list = [('localhost', 5005)]
break_now = False

def stop_all():
    global break_now
    break_now = True
def wallet_server(my_addr):
    global head_blocks
    try:
        head_blocks = txblock.load_blocks('wallet_blocks.dat')
    except:
        print('WS: no previous blocks found. starting fresh.')
        head_blocks = [None]
    server = socketutils.new_server_connection('localhost', 5006)
    while not break_now:
        new_block = socketutils.rcv_obj(server)
        if isinstance(new_block, txblock.TxBlock):
            print('received block')
            for b in head_blocks:
                if b == None:
                    if new_block.previous_hash == None:
                        new_block.previous_block = b
                        if not new_block.is_valid():
                            print('error. new block is not valid')
                        else:
                            head_blocks.remove(b)
                            head_blocks.append(new_block)
                            print('added to head blocks')
                elif new_block.previous_hash == b.compute_hash():
                    new_block.previous_block = b
                    if not new_block.is_valid():
                        print('error. new block is not valid')
                    else:
                        head_blocks.remove(b)
                        head_blocks.append(new_block)
                        print('added to head blocks')
    txblock.save_blocks(head_blocks, 'wallet_blocks.dat')
    server.close()
    return True

def get_balance(pu_key):
    long_chain = txblock.find_longest_chain(head_blocks)
    this_block = long_chain
    bal = 0.0
    while this_block != None:
        for tx in this_block.data:
            for addr, amt in tx.inputs:
                if addr == pu_key:
                    bal = bal - amt
            for addr, amt in tx.outputs:
                if addr == pu_key:
                    bal = bal + amt
        this_block = this_block.previous_block
    return bal
def send_coins(pu_send, amt_send, pr_send, pu_recv, amt_recv, miner_list):
    new_tx = transaction.Tx()
    new_tx.add_input(pu_send, amt_send)
    new_tx.add_output(pu_recv, amt_recv)
    new_tx.sign(pr_send)
    socketutils.send_obj('localhost', new_tx)
    return True

def load_keys(pr_file, pu_file):
    return signatures.load_private(pr_file), signatures.load_public(pu_file)

if __name__ == '__main__':

    import threading
    import time
    import miner
    import signatures

    miner_pr, miner_pu = signatures.generate_keys()
    t1 = threading.Thread(target = miner.miner_server, args = (('localhost', 5005),))
    t2 = threading.Thread(target=miner.nonce_finder, args=(wallet_list, miner_pu))
    t3 = threading.Thread(target=wallet_server, args=(('localhost', 5006),))

    t1.start()
    t2.start()
    t3.start()

    pr1,pu1 = load_keys('private.key', 'public.key')
    pr2, pu2 = signatures.generate_keys()
    pr3, pu3 = signatures.generate_keys()

    #query balances
    bal_1 = get_balance(pu1)
    print('balance 1: ' + str(bal_1))
    bal_2 = get_balance(pu2)
    bal_3 = get_balance(pu3)

    #send coins
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)
    send_coins(pu1, 0.1, pr1, pu2, 0.1, miner_list)

    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)
    send_coins(pu1, 0.1, pr1, pu3, 0.03, miner_list)


    time.sleep(30)

    #save and load all blocks
    txblock.save_blocks(head_blocks, 'all_blocks.dat')
    head_blocks = txblock.load_blocks('all_blocks.dat')
    #query balances
    new_1 = get_balance(pu1)
    print('new balance1: ' + str(new_1))
    new_2 = get_balance(pu2)
    new_3 = get_balance(pu3)

    #verify balance
    if abs(new_1 - bal_1 + 2.0) > 0.00000001:
        print('error. wrong balance for pu1')
    else:
        print('success. good balance for pu1')

    if abs(new_2 - bal_2 - 1.0) > 0.00000001:
        print('error. wrong balance for pu1')
    else:
        print('success. good balance for pu1')

    if abs(new_3 - bal_3 - 0.3) > 0.00000001:
        print('error. wrong balance for pu1')
    else:
        print('success. good balance for pu1')

    miner.stop_all()
    stop_all()

    t1.join()
    t2.join()
    t3.join()

    print('done')