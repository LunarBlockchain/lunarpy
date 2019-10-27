from blockchain import Block
from signatures import generate_keys, sign, verify
from transaction import Tx
import pickle
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class TxBlock (Block):
    def __init__(self, previous_block):
        super(TxBlock, self).__init__([], previous_block)

    def add_tx(self, tx_in):
        self.data.append(tx_in)

    def is_valid(self):
        if not super(TxBlock, self).is_valid():
            return False
        for tx in self.data:
            if not tx.is_valid():
                return False
        return True

#testing
if __name__ == '__main__':
    pr1, pu1 = generate_keys()
    pr2, pu2 = generate_keys()
    pr3, pu3 = generate_keys()

    Tx1 = Tx()
    Tx1.add_input(pu1, 1)
    Tx1.add_output(pu2, 1)
    Tx1.sign(pr1)

    print(Tx1.is_valid())

    savef = open('tx.dat', 'wb')
    pickle.dump(Tx1, savef)
    savef.close()

    loadf = open('tx.dat', 'rb')
    new_tx = pickle.load(loadf)

    print(new_tx.is_valid())
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

    savef = open("block.dat", "wb")
    pickle.dump(B1, savef)
    savef.close()

    loadf = open("block.dat", "rb")
    load_B1 = pickle.load(loadf)

    for b in [root, B1, load_B1, load_B1.previous_block]:
        print(b.is_valid())

    B2 = TxBlock(B1)
    Tx5 = Tx()
    Tx5.add_input(pu3, 1)
    Tx5.add_output(pu1, 100)
    Tx5.sign(pr3)
    B2.add_tx(Tx5)

    #invalid blocks
    load_B1.previous_block.add_tx(Tx4)
    for b in [load_B1, B2]:
        print(b.is_valid())