#!/usr/bin/env python2

import random

def do_xor(p, k):
	out = ''
	for i in xrange(len(p)):
		out += chr(ord(p[i]) ^ ord(k[i]))
	return out


with open('flag_plaintext', 'rb') as f1:
	p1 = ''.join(f1.readlines())

with open('secret_plaintext', 'rb') as f2:
	p2 = ''.join(f2.readlines())

l = max(len(p1), len(p2))

key = ''.join([chr(random.randint(0, 256)) for i in xrange(l)])

c1 = do_xor(p1, key)
c2 = do_xor(p2, key)

with open('flag', 'wb') as f1:
	f1.write(c1)

with open('secret', 'wb') as f2:
	f2.write(c2)
