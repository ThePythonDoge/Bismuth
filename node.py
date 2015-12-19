import socket
import sys
import re
import ast
import sqlite3

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 2829)
print 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

#verify blockchain
con = None

conn = sqlite3.connect('thincoin.db')
c = conn.cursor()
#c.execute("CREATE TABLE IF NOT EXISTS transactions (block_height, address, to_address, amount, signature, public_key)")
c.execute("SELECT Count(*) FROM transactions")
db_rows = c.fetchone()[0]
print "Total steps: "+str(db_rows)

#verify genesis
c.execute("SELECT * FROM transactions ORDER BY block_height ASC LIMIT 1")
genesis = c.fetchone()[2]
print "Genesis: "+genesis
if str(genesis) != "b813b03700c22478d7480cd6810a85dd704acec9030f587c5d8ed0f6": #change this line to your genesis address if you want to clone
    print "Invalid genesis address"
    sys.exit(1)
#verify genesis

try:
    for row in c.execute('SELECT * FROM transactions ORDER BY block_height'):
        db_block_height = row[0]
        db_address = row[1]
        db_to_address = row[2]
        db_amount = row [3]
        db_signature = row[4]
        db_public_key = RSA.importKey(row[5])
        db_transaction = str(db_block_height) +":"+ str(db_address) +":"+ str(db_to_address) +":"+ str(db_amount)

        #print db_transaction

        db_signature_tuple = ast.literal_eval(db_signature) #converting to tuple
        
        if db_public_key.verify(db_transaction, db_signature_tuple) == True:
            print "Step "+str(db_block_height)+" is valid"
        else:
            print "Step "+str(db_block_height)+" is invalid"
            if db_block_height == str(1):
                print "Your genesis signature is invalid, someone meddled with the database"
                sys.exit(1)
        
except sqlite3.Error, e:                        
    print "Error %s:" % e.args[0]
    sys.exit(1)                        
finally:                        
    if conn:
        conn.close()
#verify blockchain

while True:
    # Wait for a connection
    print 'waiting for a connection'
    connection, client_address = sock.accept()
    
    try:
        print 'connection from', client_address

        # Receive and send data
        while True:
            hello = connection.recv(4096)
            print 'received '+ hello
            
            if hello:
                with open ("peers.txt", "r") as peer_list:
                    peers=peer_list.read()
                    print peers
                    connection.sendall(peers)
                    
            data = connection.recv(4096)
            if data:
                data_split = data.split(";")
                received_transaction = data_split[0]
                print "Received transaction: "+received_transaction
                #split message into values
                received_transaction_split = received_transaction.split(":")
                block_height = received_transaction_split[0]
                address = received_transaction_split[1]
                to_address = received_transaction_split[2]
                amount =received_transaction_split[3]
                #split message into values
                received_signature = data_split[1] #needs to be converted
                received_signature_tuple = ast.literal_eval(received_signature) #converting to tuple
                print "Received signature: "+received_signature
                received_public_key_readable = data_split[2]
                print "Received public key: "+received_public_key_readable

                #convert received strings
                received_public_key = RSA.importKey(received_public_key_readable)
                #convert received strings
                
                if received_public_key.verify(received_transaction, received_signature_tuple) == True:
                    print "The signature is valid"
                    #transaction processing
                    con = None
                    try:
                        conn = sqlite3.connect('thincoin.db')
                        c = conn.cursor()
                        #verify block
                        c.execute('''SELECT block_height FROM transactions ORDER BY block_height DESC LIMIT 1;''')
                        block_latest = c.fetchone()[0]
                        print "Latest block in db: "+str(block_latest)
                        if int(block_height) != int(block_latest)+1:
                            print "Block height invalid"
                            #verify block
                        else:                      
                            #verify balance and blockchain                           
                            print "Verifying balance"
                            print address
                            c.execute("SELECT sum(amount) FROM transactions WHERE to_address = '"+address+"'")
                            inputs = c.fetchone()[0]

                            c.execute("SELECT sum(amount) FROM transactions WHERE address = '"+address+"'")
                            outputs = c.fetchone()[0]
                            if outputs == None:
                                outputs = 0
                            print "Total inputs: "+str(inputs)                                
                            print "Total outputs: "+str(outputs)
                            balance = int(inputs) - int(outputs)
                            print "Your balance: "+str(balance) 

                            if  int(balance) - int(amount) < 0:
                                print "Your balance is too low for this transaction"
                            else:
                                print "Processing transaction"
                            #verify balance and blockchain                            
                                #execute transaction
                                c.execute("INSERT INTO transactions VALUES ('"+block_height+"','"+address+"','"+to_address+"','"+amount+"','"+received_signature+"','"+received_public_key_readable+"')") # Insert a row of data                    
                                #execute transaction                                
                            conn.commit() # Save (commit) the changes
                            #todo: broadcast
                            print "Saved"
                    except sqlite3.Error, e:                      
                        print "Error %s:" % e.args[0]
                        sys.exit(1)                        
                    finally:                        
                        if conn:
                            conn.close()    
                    #transaction processing
                else:
                    print "Signature invalid"

 
            else:
                print 'no more data from', client_address
                break
            
    finally:
        # Clean up the connection
        connection.close()