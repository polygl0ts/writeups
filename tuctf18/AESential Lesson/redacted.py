#!/usr/bin/env python2

from Crypto.Cipher import AES

from select import select

import sys

INTRO = """
Lol. You think you can steal my flag?
I\'ll even encrypt your input for you,
but you can\'t get my secrets!

"""

flag = "REDACTED" # TODO Redact this

key = "REDACTED" # TODO Redact this


if __name__ == '__main__':

	padc = 'REDACTED' #TODO Redact this

	assert (len(flag) == 32) and (len(key) == 32)

	cipher = AES.new(key, AES.MODE_ECB)

	sys.stdout.write(INTRO)
	sys.stdout.flush()

	while True:
		try:
			sys.stdout.write('Enter your text here: ')
			sys.stdout.flush()

			rlist, _, _ = select([sys.stdin], [], [])

			inp = ''
			if rlist:
				inp = sys.stdin.readline().rstrip('\n')

			plaintext = inp + flag
			l = len(plaintext)

			padl = (l // 32 + 1)*32 if l % 32 != 0 else 0

			plaintext = plaintext.ljust(padl, padc)

			sys.stdout.write('Here\'s your encrypted text:\n{}\n\n'.format((cipher.encrypt(plaintext)).encode('hex')))
		except KeyboardInterrupt:
			exit(0)
