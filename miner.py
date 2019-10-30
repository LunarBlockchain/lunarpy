import socketutils
import transaction
import txblock
import pickle
import wallet

wallet_list = [('localhost',5006)]
tx_list = []
head_blocks = [None]
break_now = False

def stop_all():
    global break_now
    break_now = True

def miner_server(my_addr):
    global tx_list
    global break_now
    #global head_blocks
    try:
        tx_list = load_tx_list('txs.dat')
        print('loaded tx_list has ' + str(len(tx_list)) + ' txs')
    except:
        print('no previous txs. starting fresh')
        tx_list = []
    head_blocks = [None]
    my_ip, my_port = my_addr
    server = socketutils.new_server_connection(my_ip, my_port)
    #get txs from wallet
    while not break_now:
        new_tx = socketutils.rcv_obj(server)
        if isinstance(new_tx, transaction.Tx):
            tx_list.append(new_tx)
            print('received tx')
    print('saving ' + str(len(tx_list)) + " txs to txs.dat")
    save_tx_list(tx_list, 'txs.dat')
    return False

def nonce_finder(wallet_list, miner_public):
    global break_now
    #add txs to new block
    while not break_now:
        NewBlock = txblock.TxBlock(txblock.find_longest_chain(head_blocks))
        for tx in tx_list:
            NewBlock.add_tx(tx)

        #mining reward
        total_in, total_out = NewBlock.count_totals()
        mine_reward = transaction.Tx()
        mine_reward.add_output(miner_public, 25.0 + total_in - total_out)
        NewBlock.add_tx(mine_reward)

        #find nonce
        print('finding nonce...')
        NewBlock.find_nonce(10000)
        if NewBlock.good_nonce():
            print('good nonce found')
            head_blocks.remove(NewBlock.previous_block)
            head_blocks.append(NewBlock)
            #send new block
            save_prev = NewBlock.previous_block
            NewBlock.previous_block = None
            print(type(wallet_list))
            for addr,port in wallet_list:
                print('sending to ' + addr + ':' + str(port))
                socketutils.send_obj(addr, NewBlock, 5006)
            NewBlock.previous_block = save_prev
            #remove used txs from tx list
            for tx in NewBlock.data:
                if tx != mine_reward:
                    tx_list.remove(tx)
    txblock.save_blocks(head_blocks, 'all_blocks.dat')
    return True

def load_tx_list(filename):
    fin = open(filename, 'rb')
    ret = pickle.load(fin)
    fin.close()
    return ret

def save_tx_list(the_list, filename):
    fp = open(filename, 'wb')
    pickle.dump(the_list, fp)
    fp.close()
    return True

if __name__ == '__main__':

    import signatures
    import threading
    import time

    my_pr, my_pu = signatures.generate_keys()
    t1 = threading.Thread(target=miner_server, args=(('localhost', 5005),))
    t2 = threading.Thread(target=nonce_finder, args=(wallet_list, my_pu))

    server = socketutils.new_server_connection('localhost', 5006)

    t1.start()
    t2.start()

    pr1, pu1 = signatures.generate_keys()
    pr2, pu2 = signatures.generate_keys()
    pr3, pu3 = signatures.generate_keys()

    Tx1 = transaction.Tx()
    Tx2 = transaction.Tx()

    Tx1.add_input(pu1, 4.0)
    Tx1.add_input(pu2, 1.0)
    Tx1.add_output(pu3, 4.8)
    Tx2.add_input(pu3, 4.0)
    Tx2.add_output(pu2, 4.0)
    Tx2.add_required(pu1)

    Tx1.sign(pr1)
    Tx1.sign(pr2)
    Tx2.sign(pr3)
    Tx2.sign(pr1)

    new_tx_list = [Tx1, Tx2]
    save_tx_list(new_tx_list, 'txs.dat')
    new_new_tx_list = load_tx_list('txs.dat')

    for tx in new_new_tx_list:
        try:
            socketutils.send_obj('localhost', tx)
            print('sent tx1')
        except:
            print('error. connection unsuccessful')

    for i in range(30):
        NewBlock = socketutils.rcv_obj(server)
        if NewBlock:
            break

    if NewBlock.is_valid():
        print('success. block is valid')
    if NewBlock.good_nonce():
        print('success. nonce is valid')

    for tx in NewBlock.data:
        try:
            if tx.inputs[0][0] == pu1 and tx.inputs[0][1] == 4.0:
                print('tx1 is present')
        except:
            pass
        try:
            if tx.inputs[0][0] == pu3 and tx.inputs[0][1] == 4.0:
                print('tx2 is present')
        except:
            pass

    time.sleep(20)
    break_now = True
    time.sleep(2)

    t1.join()
    t2.join()

    server.close()

    print('done!')

