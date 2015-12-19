import hashlib
import socket
import re
import sqlite3
import os
import sys

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

if os.path.isfile("keys.pem") is True:
    print "keys.pem found"

else:   
    #generate key pair and an address
    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator)
    public_key = key.publickey()

    private_key_readable = str(key.exportKey())
    public_key_readable = str(key.publickey().exportKey())
    address = hashlib.sha224(public_key_readable).hexdigest() #hashed public key
    #generate key pair and an address

    print "Your address: "+ str(address)
    print "Your private key:\n "+ str(private_key_readable)
    print "Your public key:\n "+ str(public_key_readable)

    pem_file = open("keys.pem", 'a')
    pem_file.write(str(private_key_readable)+"\n"+str(public_key_readable) + "\n\n")
    pem_file.close()
    address_file = open ("address.txt", 'a')
    address_file.write(str(address)+"\n")
    address_file.close()


# import keys
key_file = open('keys.pem','r')
key = RSA.importKey(key_file.read())
public_key = key.publickey()
private_key_readable = str(key.exportKey())
public_key_readable = str(key.publickey().exportKey())
address = hashlib.sha224(public_key_readable).hexdigest()

print "Your address: "+ str(address)
print "Your private key:\n "+ str(private_key_readable)
print "Your public key:\n "+ str(public_key_readable)
# import keys

transaction = "1:genesis:"+address+":100000000"
signature = key.sign(transaction, '')
print "Signature: "+str(signature)

if os.path.isfile("thincoin.db") is True:
    print "You are beyond genesis"
else:
    #transaction processing
    con = None
    try:
        conn = sqlite3.connect('thincoin.db')
        c = conn.cursor()
        c.execute("CREATE TABLE transactions (block_height, address, to_address, amount, signature, public_key)")
        c.execute("INSERT INTO transactions VALUES ('1','genesis','"+address+"','100000000','"+str(signature)+"','"+public_key_readable+"')") # Insert a row of data                    
               
        conn.commit() # Save (commit) the changes
        #todo: broadcast
        print "Genesis created, don't forget to hardcode your genesis address"
    except sqlite3.Error, e:                      
        print "Error %s:" % e.args[0]
        sys.exit(1)                        
    finally:                        
        if conn:
            conn.close()
    #transaction processing