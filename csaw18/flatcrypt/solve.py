# Based on https://github.com/mpgn/CRIME-poc/blob/master/CRIME-rc4-poc.py

from pwn import *

import string
import sys

CHARSET = list(string.ascii_lowercase) + ['_']

def oracle(s, data):
    s.sendline(data)
    s.recvline()
    line = s.recvline()
    ret = ord(line[-2])
    return ret


def two_tries_recursive(s, found, p):
    tmp = []
    for i in CHARSET:
        payload1 = '=asdf' + '~#:/@$&@$&[|/0' + i + ''.join(found) + '=asdf'
        payload2 = '=asdf' + i + '~#:/@$&@$&[|/0' + ''.join(found) + '=asdf'

        assert len(payload1) >= 20 and len(payload2) >= 20

        len1 = oracle(s, payload1)
        len2 = oracle(s, payload2)
        if len1 < len2:
            tmp.append(i)

    for a in tmp:
        t = list(found)
        t.insert(0, a)
        print '[+] flag={}'.format(''.join(t))
        p = two_tries_recursive(s, t, p)

    if len(tmp) == 0:
        p += 1
        print("")
    return p


def main():
    s = remote('crypto.chal.csaw.io', 8042)
    found = ['']
    p = two_tries_recursive(s, found, 0)
    print "\nFound", str(p), "possibilities of secret flag"


if __name__ == '__main__':
    main()
