import hashlib
import socket
import re
import sqlite3
import os
import sys
import time
import base64

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random

if os.path.isfile("privkey.der") is True:
    print ("privkey.der found")
elif os.path.isfile("privkey_encrypted.der") is True:
    print("privkey_encrypted.der found")

else:
    # generate key pair and an address
    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator)
    public_key = key.publickey()

    private_key_readable = str(key.exportKey())
    public_key_readable = str(key.publickey().exportKey())
    address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()  # hashed public key
    # generate key pair and an address

    print ("Your address: " + str(address))
    print ("Your private key:\n " + str(private_key_readable))
    print ("Your public key:\n " + str(public_key_readable))

    pem_file = open("privkey.der", 'a')
    pem_file.write(str(private_key_readable))
    pem_file.close()

    pem_file = open("pubkey.der", 'a')
    pem_file.write(str(public_key_readable))
    pem_file.close()

    address_file = open("address.txt", 'a')
    address_file.write(str(address) + "\n")
    address_file.close()

# import keys
key = RSA.importKey(open('privkey.der').read())
public_key = key.publickey()
private_key_readable = str(key.exportKey())
public_key_readable = str(key.publickey().exportKey())
address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()

print ("Your address: " + str(address))
print ("Your private key:\n " + str(private_key_readable))
print ("Your public key:\n " + str(public_key_readable))
public_key_hashed = base64.b64encode(public_key_readable)
# import keys

timestamp = str(time.time())
print "Timestamp: " + timestamp
transaction = (timestamp, "genesis", address, str(float(100000000)), "genesis")
h = SHA.new(str(transaction))
signer = PKCS1_v1_5.new(key)
signature = signer.sign(h)
signature_enc = base64.b64encode(signature)
print "Encoded Signature: " + str(signature_enc)
block_hash = hashlib.sha224(str((timestamp, transaction)).encode("utf-8")).hexdigest()  # first hash is simplified
print ("Transaction Hash:" + block_hash)

if os.path.isfile("static/ledger.db") is True:
    print ("You are beyond genesis")
else:
    # transaction processing
    con = None
    try:
        conn = sqlite3.connect('static/ledger.db')
        c = conn.cursor()
        c.execute("CREATE TABLE transactions (block_height INTEGER, timestamp, address, recipient, amount, signature, public_key, block_hash, fee, reward, keep, openfield)")
        c.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", ("1", timestamp, 'genesis', address, '0', str(signature_enc), public_key_hashed, block_hash, 0, 1, 1, 'genesis'))  # Insert a row of data
        conn.commit()  # Save (commit) the changes

        mempool = sqlite3.connect('mempool.db')
        m = mempool.cursor()
        m.execute("CREATE TABLE transactions (timestamp, address, recipient, amount, signature, public_key, keep, openfield)")
        mempool.commit()
        mempool.close()

        print ("Genesis created, don't forget to change genesis address in the config file")
    except sqlite3.Error as e:
        print ("Error %s:" % e.args[0])
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            # transaction processing
