TUCTF 2018: Shella Easy
=======================

## Description

Difficulty: easy-ish

Want to be a drive-thru attendant?
Well, no one does... But! the best employee receives their very own flag!
whatdya say?

`nc 52.15.182.55 12345`

## Solution

The target uses `gets` to read into a stack buffer which is a straightforward
example of a stack buffer overflow. The target also has an executable stack,
which means that we can simply write our shellcode in the buffer, then jump to
it by overwriting the saved return address. The binary even prints the address
of the stack buffer we will overflow before asking us for input so this is
pretty much as simple as it gets in terms of exploitation.

The only thing that stands between us and a shell is an additional check that
the target is doing. During initialization one of the stack variables is set
to 0xcafebabe but before returning from `main` the target checks if the same
variable is 0xdeadbeef. If this check fails, the target calls `exit`, thus never
returning (and never executing our shellcode). To make it succeed, we can just
overwrite the variable with the correct value when smashing the stack.

```
$ python2 exploit.py
[+] Opening connection to 52.15.182.55 on port 12345: Done
[*] Switching to interactive mode
$ ls
chal
flag
$ cat flag
TUCTF{1_607_4_fl46_bu7_n0_fr135}
$
[*] Closed connection to 52.15.182.55 port 12345
```
