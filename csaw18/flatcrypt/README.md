CSAW CTF 2018: flatcrypt
========================

## Description 

no logos or branding for this bug

Take your pick `nc crypto.chal.csaw.io 8040` `nc crypto.chal.csaw.io 8041` `nc crypto.chal.csaw.io 8042` `nc crypto.chal.csaw.io 8043`

flag is not in flag format. flag is PROBLEM_KEY

serv-distribute.py:

```py

import zlib
import os

from Crypto.Cipher import AES
from Crypto.Util import Counter

ENCRYPT_KEY = bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000')
# Determine this key.
# Character set: lowercase letters and underscore
PROBLEM_KEY = 'not_the_flag'

def encrypt(data, ctr):
    return AES.new(ENCRYPT_KEY, AES.MODE_CTR, counter=ctr).encrypt(zlib.compress(data))

while True:
    f = input("Encrypting service\n")
    if len(f) < 20:
        continue
    enc = encrypt(bytes((PROBLEM_KEY + f).encode('utf-8')), Counter.new(64, prefix=os.urandom(8)))
    print("%s%s" %(enc, chr(len(enc))))
```

## Solution

The server reads some input from the attacker and concatenates it with the flag.
It then sends the result to us after first compressing it with zlib and then
encrypting it with AES in CTR mode with an unknown key.

The weakness is that the input to the compression function contains both the
secret and data chosen by the attacker. This is exploitable because the output
of the compression function is shorter if the input contains repeated strings.
Thus when our input contains part of the flag the output will be shorter than
when it doesn't.

This is similar to the CRIME attack and we can adapt [this POC
code](https://github.com/mpgn/CRIME-poc/blob/master/CRIME-rc4-poc.py) to solve
the challenge.

Flag: `crime_doesnt_have_a_logo`
