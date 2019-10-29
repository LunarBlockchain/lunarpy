import socketutils
import transaction
import txblock
import signatures

wallet_list = ['localhost']
tx_list = []
head_blocks = [None]

def find_longest_chain():
    longest = -1
    long_head = None
    for b in head_blocks:
        current = b
        this_len = 0
        while current != None:
            this_len = this_len + 1
            current = current.previous_block
        if this_len > longest:
            long_head = b
            longest = this_len
    return long_head

def miner_server(my_ip, wallet_list, my_public):
    server = socketutils.new_server_connection(my_ip)
    #get 2 txs from wallet
    for i in range(10):
        new_tx = socketutils.rcv_obj(server)
        if isinstance(new_tx, transaction.Tx):
            tx_list.append(new_tx)
            print('received tx')
        if len(tx_list) >= 2:
            break

    #add txs to new block
    NewBlock = txblock.TxBlock(find_longest_chain())
    NewBlock.add_tx(tx_list[0])
    NewBlock.add_tx(tx_list[1])

    #mining reward
    total_in, total_out = NewBlock.count_totals()
    mine_reward = transaction.Tx()
    mine_reward.add_output(my_public, 25.0 + total_in - total_out)
    NewBlock.add_tx(mine_reward)

    #find nonce
    for i in range(10):
        print('finding nonce...')
        NewBlock.find_nonce()
        if NewBlock.good_nonce():
            print('good nonce found')
            break
    if not NewBlock.good_nonce():
        print('error. coundt find nonce')
        return False

    #send new block
    for ip_addr in wallet_list:
        print('sending to ' + ip_addr)
        socketutils.send_obj(ip_addr, NewBlock, 5006)
    head_blocks.remove(NewBlock.previous_block)
    head_blocks.append(NewBlock)
    return False

my_pr, my_pu = signatures.generate_keys()
miner_server('localhost', wallet_list, my_pu)