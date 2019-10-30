from blockchain import Block
from signatures import generate_keys, sign, verify
from transaction import Tx
import pickle
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import time
import random

reward = 25.0
leading_zeros = 2
next_char_limit = 255
head_blocks = [None]

class TxBlock (Block):
    global head_blocks
    head_blocks = [None]

    nonce = 'AAAAAA'

    def __init__(self, previous_block):
        super(TxBlock, self).__init__([], previous_block)

    def add_tx(self, tx_in):
        self.data.append(tx_in)

    def count_totals(self):
        total_in = 0
        total_out = 0
        for tx in self.data:
            for addr, amt in tx.inputs:
                total_in = total_in + amt

            for addr, amt in tx.outputs:
                total_out = total_out + amt

        return total_in, total_out

    def is_valid(self):
        if not super(TxBlock, self).is_valid():
            return False
        for tx in self.data:
            if not tx.is_valid():
                return False
        total_in, total_out = self.count_totals()
        if total_out - total_in - reward > 0.0000000001:
            return False
        return True

    def good_nonce(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf8'))
        digest.update(bytes(str(self.previous_hash), 'utf8'))
        digest.update(bytes(str(self.nonce), 'utf8'))
        this_hash = digest.finalize()

        if this_hash[:leading_zeros] != bytes(''.join([ '\x4f' for i in range(leading_zeros)]),'utf8'):
            return False
        return int(this_hash[leading_zeros]) < next_char_limit
    def find_nonce(self, n_tries=1000000):
        for i in range(n_tries):
            self.nonce = ''.join([
                chr(random.randint(0, 255)) for i in range(10*leading_zeros)])
            if self.good_nonce():
                return self.nonce
        return None

def find_longest_chain(head_blocks):
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

#testing
if __name__ == '__main__':
    pr1, pu1 = generate_keys()
    pr2, pu2 = generate_keys()
    pr3, pu3 = generate_keys()

    Tx1 = Tx()
    Tx1.add_input(pu1, 1)
    Tx1.add_output(pu2, 1)
    Tx1.sign(pr1)

    if Tx1.is_valid():
        print('sucess. tx is valid')
    else:
        print('error')

    savef = open('tx.dat', 'wb')
    pickle.dump(Tx1, savef)
    savef.close()

    loadf = open('tx.dat', 'rb')
    new_tx = pickle.load(loadf)

    if new_tx.is_valid():
        print('success. loaded tx is valid')
    loadf.close()

    root = TxBlock(None)
    root.add_tx(Tx1)

    Tx2 = Tx()
    Tx2.add_input(pu2, 1.1)
    Tx2.add_output(pu3, 1)
    Tx2.sign(pr2)
    root.add_tx(Tx2)

    B1 = TxBlock(root)
    Tx3 = Tx()
    Tx3.add_input(pu3, 1.1)
    Tx3.add_output(pu1, 1)
    Tx3.sign(pr3)
    B1.add_tx(Tx3)

    Tx4 = Tx()
    Tx4.add_input(pu1, 1)
    Tx4.add_output(pu2, 1)
    Tx4.add_required(pu3)
    Tx4.sign(pr1)
    Tx4.sign(pr3)
    B1.add_tx(Tx4)
    start = time.time()
    print(B1.find_nonce())
    elapsed = time.time() - start
    print('elapsed time: ' + str(elapsed) + ' sec')
    if elapsed < 60:
        print('error. mining too fast')
    if B1.good_nonce():
        print('success. good nonce')
    else:
        print('error. bad nonce')

    savef = open("block.dat", "wb")
    pickle.dump(B1, savef)
    savef.close()

    loadf = open("block.dat", "rb")
    load_B1 = pickle.load(loadf)

    for b in [root, B1, load_B1, load_B1.previous_block]:
        if b.is_valid():
            print('success. valid blocks')
        else:
            print('error. bad blocks')

    if B1.good_nonce():
        print('success. good nonce after save & load')
    else:
        print('error. bad nonce after save & load')

    B2 = TxBlock(B1)
    Tx5 = Tx()
    Tx5.add_input(pu3, 1)
    Tx5.add_output(pu1, 100)
    Tx5.sign(pr3)
    B2.add_tx(Tx5)

    #invalid blocks
    load_B1.previous_block.add_tx(Tx4)
    for b in [load_B1, B2]:
        if b.is_valid():
            print('error. bad block was verified')
        else:
            print('success. bad block detected')

    #test mining reward and tx fee
    pr4, pu4 = generate_keys()

    B3 = TxBlock(B2)
    B3.add_tx(Tx2)
    B3.add_tx(Tx3)
    B3.add_tx(Tx4)
    Tx6 = Tx()
    Tx6.add_output(pu4, 25)
    B3.add_tx(Tx6)

    if B3.is_valid():
        print('success. block reward succeed')
    else:
        print('error. block reward fail')

    B4 = TxBlock(B3)
    B4.add_tx(Tx2)
    B4.add_tx(Tx3)
    B4.add_tx(Tx4)
    Tx7 = Tx()
    Tx7.add_output(pu4, 25.2)
    B4.add_tx(Tx7)

    if B4.is_valid():
        print('success. tx fees succeed.')
    else:
        print('error. tx fees fail')

    #greedy miner
    B5 = TxBlock(B4)
    B5.add_tx(Tx2)
    B5.add_tx(Tx3)
    B5.add_tx(Tx4)
    Tx8 = Tx()
    Tx8.add_output(pu4, 26.2)
    B5.add_tx(Tx8)

    if not B5.is_valid():
        print('success. greed detected')
    else:
        print('error. greed not detected')