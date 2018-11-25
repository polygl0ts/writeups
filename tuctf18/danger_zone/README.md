# TU CTF 2018 - Danger Zone

## Description
Difficulty: easy
Legend says, this program was written by Kenny Loggins himself.

## Given files
- [dangerzone.pyc](./dangerzone.pyc)

## Solution
The `.pyc` extension indicates python compiled code. So let's decompile it using [uncompyle6](https://github.com/rocky/python-uncompyle6).

```
import base64

def reverse(s):
    return s[::-1]


def b32decode(s):
    return base64.b32decode(s)


def reversePigLatin(s):
    return s[-1] + s[:-1]


def rot13(s):
    return s.decode('rot13')


def main():
    print 'Something Something Danger Zone'
    return '=YR2XYRGQJ6KWZENQZXGTQFGZ3XCXZUM33UOEIBJ'


if __name__ == '__main__':
    s = main()
    print s
```

The string returned by the `main` function seems to be a reverse base64 string.

Looking at the decompiled code, the first function in the file is `reverse`, the second one `b32decode`. First we conclude that it's actually base32 and not base64. But, more importantly, it seems that applying the functions in the same order as they appear on the file will decode the string.

Let's give it a try and run: `rot13(reversePigLatin(b32decode(reverse('=YR2XYRGQJ6KWZENQZXGTQFGZ3XCXZUM33UOEIBJ'))))
`

This holds the flag!

```
    TUCTF{r3d_l1n3_0v3rl04d}
```

## Code
[danger_zone.py](./danger_zone.py)
