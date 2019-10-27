from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

class someClass:
    string = None
    num = 328965
    def __init__(self, string):
        self.string = string
    def __repr__(self):
        return self.string + '^^^' + str(self.num)
    
class Block:
    data = None
    previous_hash = None
    previous_block = None

    def __init__(self, data, previous_block):
        self.data = data
        self.previous_block = previous_block
        if previous_block != None:
            self.previous_hash = previous_block.compute_hash()

    def compute_hash(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf8'))
        digest.update(bytes(str(self.previous_hash), 'utf8'))
        return digest.finalize()

    def is_valid(self):
        if self.previous_block == None:
            return True
        return self.previous_block.compute_hash() == self.previous_hash

if __name__ == '__main__':
    root = Block('I am robot', None)
    B1 = Block('I am child.', root)
    B2 = Block('I am B1s brother.', root)
    B3 = Block(1234, B1)
    B4 = Block(someClass('Hi there'), B3)
    B5 = Block('block', B4)

    for b in [B1, B2, B3, B4, B5]:
        print(b.previous_block.compute_hash() == b.previous_hash)
