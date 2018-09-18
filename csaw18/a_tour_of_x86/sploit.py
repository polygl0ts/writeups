from pwn import *
import binascii

conn = remote('rev.chal.csaw.io', 9004)
print conn.recvline()

binary = binascii.hexlify(open('sploit.bin', 'r').read())
# print(binary)
conn.send(binary + '\n')
while True:
    print conn.recvline()
