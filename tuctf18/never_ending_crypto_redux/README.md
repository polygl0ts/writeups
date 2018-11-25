# TU CTF 2018 - Never Ending Crypto Redux

## Description
The challenge is back and stronger than ever!
IT WILL NEVER END!!

Good luck. You're gonna need it.

nc 18.223.156.26 12345

## Solution
This challenge consists in a series of levels (from 0 to 7). For each level we can do one query, obtaining the ciphertext corresponding to our plaintext. Then we are given 50 ciphertext in sequence and we have to decode all of them in order to reach the next level.

### Level 0
Just morse code.

### Level 1
Morse code and [rot13](https://en.wikipedia.org/wiki/ROT13).

### Level 2
This time the ciphertext is not valid morse code. Hopefully seeing it next to the ciphertext of `Level 0` pointed me in the correct direction: we had to replace `.` with `-` and vice versa (from now this I'll call this operation "flip"). Doing that we obtain the morse code

### Level 3
This was probably the trickiest level. Our plaintext is divide in three buffers based on modulo 3 of the character index. In other words, the indexes will be divided as below.

```
a = 0, 3, 6, ...
b = 1, 4, 7, ...
c = 2, 5, 8, ...
```

Then the three buffers are concatenated `a + b + c`.

Let's call this operation "mix". To win this level we decode the morse and mix.

### Level 4
We add rot13, i.e. morse, mix and rot13.

### Level 5
Again a combination of the previous levels: flip, morse, mix and rot13.

### Level 6
Here some letters were encoded in the same one, which made me think the message was xor-ed with a key. Sending a bunch of `A` as plaintext gave me `TUCTFTUCTFTUCTF...` confirming my opinion: `TUCTF` is the key.

Nevertheless, once decoded with the key we also have to apply rot13.

### Level 7
First of all we notice that this should be last level:

`You're good! But are you good enough
to beat this FINAL CHALLENGE?!!!!`

After a few trials it turns out this was a combination of all the previous challenges: flip, morse, mix, xor with `HAVEFUN`, rot13.

```
    Congratulations on ending what was never ending!

    Here's your flag:
    TUCTF{CRYPT0_D03$NT_R34LLY_3V3R_3ND}
```

## Code
[flag.py](./flag.py)
