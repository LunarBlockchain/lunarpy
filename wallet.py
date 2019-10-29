import socketutils
import transaction
import signatures

head_blocks = [None]

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

Tx2.sign(pr1)
Tx2.sign(pr2)
Tx2.sign(pr3)
Tx2.sign(pr1)

print(Tx1.is_valid())
print(Tx2.is_valid())

try:
    socketutils.send_obj('localhost', Tx1)
    socketutils.send_obj('localhost', Tx2)
except:
    print('error. connection unsuccessful')

server = socketutils.new_server_connection('localhost', 5006)
for i in range(30):
    new_block = socketutils.rcv_obj(server)
    if new_block:
        break
server.close()

if new_block.is_valid():
    print('success. block is valid')
if new_block.good_nonce():
    print('success. nonce is valid')

for tx in new_block.data:
    try:
        if tx.inputs[0][0] == pu1 and tx.inputs[0][1] == 4.0:
            print('tx1 is present')
    try:
        if tx.inputs[1][0] == pu3 and tx.inputs[0][1] == 4.0:
            print('tx2 is present')

for b in head_blocks:
    if NewBlock.previous_hash == b.compute_hash():
        NewBlock.previous_block = b
        head_blocks.remove(b)
        head_blocks.append(NewBlock)