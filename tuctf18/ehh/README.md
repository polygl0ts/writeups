TUCTF 2018: Ehh
===============

## Description

Difficulty: easy

Whatever... I dunno

`nc 18.222.213.102 12345`

## Solution

The target asks us for a string, then use it as the format string for `printf`.
After the call to `printf` it will check that the global variable `val` is 0x18
and give us the flag if that check succeeds.

This is a straightforward example of a format string vulnerability: we can
use the `%n` format specifier to overwrite arbitrary memory, in this case `val`.
The binary is position-independent, but conveniently the first thing it does
is send us the address of `val` so we don't have to search for an infoleak.

The first step in exploiting the binary is finding out what is the first
argument to `printf` that we can control. The easiest way to do this is using
`%s`, then `%xs`, then `%x%x%s` and so on as format string until the target
crashes.

In this case the program starts crashing at `%x%x%x%x%x%s` so the we control the
arguments starting from the 6th. We can use pwntools's format string helper to
generate a payload instead of writing it by hand.


```
$ python2 exploit.py
[+] Opening connection to 18.222.213.102 on port 12345: Done
[+] Receiving all data: Done (73B)
[*] Closed connection to 18.222.213.102 port 12345
TUCTF{pr1n7f_15_pr377y_c00l_huh}
```
