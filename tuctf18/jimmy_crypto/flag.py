#!/usr/bin/env python2

import string

def do_xor(p, k):
	out = ''
	for i in xrange(len(p)):
		out += chr(ord(p[i]) ^ ord(k[i]))
	return out

def get_x():
	with open('flag', 'rb') as f1:
		p1 = ''.join(f1.readlines())

	with open('secret', 'rb') as f2:
		p2 = ''.join(f2.readlines())

	return do_xor(p1, p2)

def check(s, dic):
	for c in s:
		if c not in dic:
			return False
	return True

def get_indexes(s, x, dic):
	l = len(s)
	for i in range(42, len(x)-l):
		res = do_xor(s, x[i : i + l])
		if check(res, dic):
			print(str(i) + ' -> ' + res)

def xor_and_check(a, b, dic):
	res = do_xor(a, b)
	if check(res, dic):
		print(res)
	else:
		print('NOPE')


def flag():
	flag_chars = string.uppercase + string.digits + string.punctuation
	secret_chars = string.printable
	x = get_x()

	# print('___________________________________________________________')
	# print('Indexes: TUCTF{')
	# get_indexes('TUCTF{', x, secret_chars)

	print('___________________________________________________________')
	flag = '~TUCTF{D0NT_US3_TH3_S4M3_K3Y_F0R_TH3_S4M3_M3SS4G3}~'
	print('Flag: ' + flag)
	xor_and_check(flag, x[41:], secret_chars)

	print('___________________________________________________________	')
	secret = 'steal my secrets. If you are looking at this file, '
	print('Secret: ' + secret)
	xor_and_check(secret, x[41:], flag_chars)

if __name__ == '__main__':
    flag()
