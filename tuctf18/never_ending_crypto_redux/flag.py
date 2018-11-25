from pwn import *
import string

morseAlphabet = {
    "A" : ".-",
    "B" : "-...",
    "C" : "-.-.",
    "D" : "-..",
    "E" : ".",
    "F" : "..-.",
    "G" : "--.",
    "H" : "....",
    "I" : "..",
    "J" : ".---",
    "K" : "-.-",
    "L" : ".-..",
    "M" : "--",
    "N" : "-.",
    "O" : "---",
    "P" : ".--.",
    "Q" : "--.-",
    "R" : ".-.",
    "S" : "...",
    "T" : "-",
    "U" : "..-",
    "V" : "...-",
    "W" : ".--",
    "X" : "-..-",
    "Y" : "-.--",
    "Z" : "--..",
    " " : "/",
    "1" : ".----",
    "2" : "..---",
    "3" : "...--",
    "4" : "....-",
    "5" : ".....",
    "6" : "-....",
    "7" : "--...",
    "8" : "---..",
    "9" : "----.",
    "0" : "-----",
    "." : ".-.-.-",
    "," : "--..--",
    ":" : "---...",
    "?" : "..--..",
    "'" : ".----.",
    "-" : "-....-",
    "/" : "-..-.",
    "@" : ".--.-.",
    "=" : "-...-"
}

morse_dict = dict((v,k) for (k,v) in morseAlphabet.items())

conn = remote('18.223.156.26', 12345)

def to_list(ciphertext):
    return ciphertext.strip().split(' ')

def morse(ciphertext):
    plaintext = ''
    for c in ciphertext:
        plaintext += morse_dict[c]

    return plaintext

def rot13(ciphertext):
    plaintext = ''
    for c in ciphertext:
        plaintext += chr(((ord(c) - 65 - 13) % 26) + 65)

    return plaintext

def flip(ciphertext):
    ciphertext = ciphertext.replace('.', 'x')
    ciphertext = ciphertext.replace('-', '.')
    ciphertext = ciphertext.replace('x', '-')

    return ciphertext

def mix(ciphertext):
    d = len(ciphertext) / 3
    mod = len(ciphertext) % 3

    ia = d if mod == 0 else (d + 1)
    mod = max(0, mod - 1)

    ib = d if mod == 0 else (d + 1)
    ib += ia
    mod = max(0, mod - 1)

    ic = d + ib

    a = ciphertext[: ia]
    b = ciphertext[ia : ib]
    c = ciphertext[ib : ic]

    plaintext = ''
    for i in range(d):
        plaintext += a[i]
        plaintext += b[i]
        plaintext += c[i]

    plaintext += a[d:] + b[d:]

    return plaintext

def xor_key(key, ciphertext):
    plaintext = ''
    for i, c in enumerate(ciphertext):
        plaintext += chr(((ord(c) - 65 - ord(key[i % len(key)])) % 26) + 65)

    return plaintext

def flag():
    text = ''.join(string.uppercase)

    # Level 0: morse
    conn.recvuntil(':')
    conn.sendline(text)
    for i in range(50):
        r = conn.recvuntil('Decrypt')
        if i == 0:
            print(r)
        r = conn.recvline()
        conn.sendline(morse(to_list(r)))

    # Level 1: morse + rot13
    conn.sendline(text)
    for i in range(50):
        r = conn.recvuntil('Decrypt')
        if i == 0:
            print(r)
        r = conn.recvline()
        conn.sendline(rot13(morse(to_list(r))))

    # Level 2: flip + morse
    conn.sendline(text)
    for i in range(50):
        r = conn.recvuntil('Decrypt')
        if i == 0:
            print(r)
        r = conn.recvline()
        conn.sendline(morse(to_list(flip(r))))

    # Level 3: morse + mix
    conn.sendline(text)
    for i in range(50):
        r = conn.recvuntil('Decrypt')
        if i == 0:
            print(r)
        r = conn.recvline()
        conn.sendline(mix(morse(to_list(r))))

    # Level 4: morse + mix + rot13
    conn.sendline(text)
    for i in range(50):
        r = conn.recvuntil('Decrypt')
        if i == 0:
            print(r)
        r = conn.recvline()
        conn.sendline(rot13(mix(morse(to_list(r)))))

    # Level 5: flip + morse + mix + rot13
    conn.sendline(text)
    for i in range(50):
        r = conn.recvuntil('Decrypt')
        if i == 0:
            print(r)
        r = conn.recvline()
        conn.sendline(rot13(mix(morse(to_list(flip(r))))))

    # Level 6: morse + key TUCTF + rot13
    conn.sendline(text)
    # conn.sendline('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    for i in range(50):
        r = conn.recvuntil('Decrypt')
        if i == 0:
            print(r)
        r = conn.recvline()
        conn.sendline(rot13(xor_key('TUCTF', morse(to_list(r)))))

    # Level 7: flip + morse + mix + key HAVEFUN + rot13
    conn.sendline(text)
    # conn.sendline('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
    for i in range(50):
        r = conn.recvuntil('Decrypt')
        if i == 0:
            print(r)
        r = conn.recvline()
        conn.sendline(rot13(xor_key('HAVEFUN', mix(morse(to_list(flip(r)))))))

    # GET FLAG!!!
    print(conn.recvall())

if __name__ == '__main__':
    flag()
