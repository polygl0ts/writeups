# Pragyan CTF 2019 - EXORcism

## Description
>My friend Alex needs your help very fast. He has been possessed by a ghost and the only way to save him is if you tell the flag to the ghost. Hurry up, time is running out!

We are given the file [encoded.txt](./encoded.txt), which has 10000 lines, each line consists in a `0` or a `1`.

## Solution
The file starts with more than 1000 `1`s, then some `0` appears here and there. The first observation I did was that the number of subsequent `0`s seemed to always be even.

I thought it was an esoteric language (as often happens in CTFs), but it wasn't the case. My next idea was to rearrange the characters in a 100x100 square. The result looked promising but a bit confused, so I replaced all `1` with a white space. This gave a much more clearer output: a QR-code? I changed the `0` to be black squares and yes, it clearly gave me a QR-code!

This is the simple script I used.

```
f = open('./encoded.txt', 'r')

i = 0
s = ''
for line in f:
    if i % 100 == 0:
        print s.replace('1', ' ').replace('0', u"\u2588")
        s = ''
    s += line.strip()
    i += 1

f.close()
```

At this point I was a bit lazy: I printed the output directly on the terminal, took a screenshot and modified the height with GIMP (the image was elongated). Scanning the resulting [QR-code](./exorxism.png) gave me `160f15011d1b095339595138535f135613595e1a`.

Given the name of the challenge, my idea was to `xor` the above string (after hex-decoding it) with the flag prefix (i.e. `pctf{`), which gave me `flagf`. So let's try to `xor` it with `flag`:

`pctf{wh4_50_53r1u5?}`
