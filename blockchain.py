from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
digest.update(b"abc")
digest.update(b"123")
hash = digest.finalize()
print(hash)

class someClass:
    def __init__(self, string):
        self.string = string
    def __repr__(self):
        return self.string
    
class CBlock:
    data = None
    previousHash = None
    def __init__(self, data, previous_block):
        pass

    def compute_hash(self):
        return b'aaa'

if __name__ == '__main__':
    root = CBlock('I am robot', None)
    B1 = CBlock('I am child.', root)
    B2 = CBlock('I am B1s brother.', root)
    B3 = CBlock(1234, B1)
    B4 = CBlock(someClass('Hi there'))
