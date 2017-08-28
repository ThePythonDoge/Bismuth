#this file takes optional arguments, arg1 = amount to spend, arg2 = recipient address, arg3 = keep forever (0/1), arg4=OpenField data
#args3+4 are not prompted if ran without args

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

import base64
import time
import sqlite3
import keys
import sys 


key, private_key_readable, public_key_readable, public_key_hashed, address = keys.read()

print('Number of arguments: %d arguments.' % len(sys.argv))
print('Argument List: %s' % ', '.join(sys.argv))

# get balance

mempool = sqlite3.connect('mempool.db')
mempool.text_factory = str
m = mempool.cursor()
m.execute("SELECT sum(amount) FROM transactions WHERE address = ?;", (address,))
debit_mempool = m.fetchone()[0]
mempool.close()

if debit_mempool is None:
    debit_mempool = 0

conn = sqlite3.connect('static/ledger.db')
conn.text_factory = str
c = conn.cursor()
c.execute("SELECT sum(amount) FROM transactions WHERE recipient = ?;", (address,))
credit = c.fetchone()[0]
c.execute("SELECT sum(amount) FROM transactions WHERE address = ?;", (address,))
debit = c.fetchone()[0]
c.execute("SELECT sum(fee) FROM transactions WHERE address = ?;", (address,))
fees = c.fetchone()[0]
c.execute("SELECT sum(reward) FROM transactions WHERE address = ?;", (address,))
rewards = c.fetchone()[0]
c.execute("SELECT MAX(block_height) FROM transactions")
bl_height = c.fetchone()[0]

debit = 0 if debit is None ele debit
fees = 0 if fees is None else fees
rewards = 0 if rewards is None else rewards
credit = 0 if credit is None else credit

balance = credit - debit - fees + rewards - debit_mempool
print("Transction address: %s" % address)
print("Transction address balance: %s" % balance)

#get balance

try:
    amount_input = sys.argv[1]
except IndexError:
    amount_input = input("Amount: ")

try:
    recipient_input = sys.argv[2]
except IndexError:
    recipient_input = input("Recipient: ")

try:
    keep_input = sys.argv[3]
except IndexError:
    keep_input = 0

try:
    openfield_input = sys.argv[4]
except IndexError:
    openfield_input = ''


# hardfork fee display
fee = '%.8f' % float(0.01 + (float(amount_input) * 0.001) + (float(len(openfield_input)) / 100000) + (float(keep_input) / 10))  # 0.1% + 0.01 dust
print("Fee: %s" % fee)

confirm = input("Confirm (y/n): ")

if confirm != 'y':
    print ("Transaction cancelled, user confirmation failed")
    exit(1)

# hardfork fee display
try:
    float(amount_input)
    is_float = 1
except ValueError:
    is_float = 0
    exit(1)

if len(str(recipient_input)) != 56:
    print("Wrong address length")
else:
    timestamp = '%.2f' % time.time()
    transaction = (str(timestamp), str(address), str(recipient_input), '%.8f' % float(amount_input), str(keep_input), str(openfield_input)) #this is signed
    #print transaction

    h = SHA.new(str(transaction).encode("utf-8"))
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    signature_enc = base64.b64encode(signature)
    
    print("Encoded Signature: %s" % signature_enc.decode("utf-8"))
    verifier = PKCS1_v1_5.new(key)
    
    if verifier.verify(h, signature):
        if float(amount_input) < 0:
            print("Signature OK, but cannot use negative amounts")

        elif float(amount_input) > float(balance):
            print("Mempool: Sending more than owned")

        else:
            print("The signature is valid, proceeding to save transaction to mempool")
            mempool = sqlite3.connect('mempool.db')
            mempool.text_factory = str
            m = mempool.cursor()
            m.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)",(str(timestamp), str(address), str(recipient_input), '%.8f' % float(amount_input),str(signature_enc.decode("utf-8")), str(public_key_hashed), str(keep_input), str(openfield_input)))
            mempool.commit()  # Save (commit) the changes
            mempool.close()
            print("Mempool updated with a received transaction")
            #refresh() experimentally disabled
    else:
        print("Invalid signature")
    #enter transaction end
