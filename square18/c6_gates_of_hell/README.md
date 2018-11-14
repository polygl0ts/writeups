Square CTF 2018: C6 - gates of hell
===================================

## Description

C6 is a Linux based system. It was brought to Charvis by the very first
settlers. You found a USB drive with a copy of the executable.

Now, all you need to do is figure out the correct input to disable C6 through
its online interface.

## Solution

The only file provided with this challenge is a 32-bit Linux executable called
`gates_of_hell`. When run the executable doesn't seem to do anything. Running
the target under strace confirms this, as the only system call that the program
uses is `exit()`.

The online interface is located at `/cgi-bin/gates-of-hell.pl` on the server and
just displays

```
root@sqctf:~$ /bin/gates-of-hell
```

We figured out that if we add a query string to the URL it will be passed to the
program as a sequence of command line arguments. For example
`cgi-bin/gates-of-hell.pl?hello world` displays

```
root@sqctf:~$ /bin/gates-of-hell hello world
```

It looks like we will have to reverse the program and find a sequence of command
line arguments that will make it print the flag.

The target is very small (only 4 functions) and towards the end of the main
function we can see that it checks if ebx == 666. If the check succeeds, it will
print `flag is here on server\n-- Alok` and then exit, otherwise it will just
exit.

After some reversing we came up with the following pseudocode for the program:

```c
unsigned char table[256] = { ... };

int main(int argc, char *argv[])
{
	if (argc < 16)
		exit();

	unsigned int ebx = 37;

	for (int i = 0; i < 16; i++) {
		unsigned int x = atob(argv[i]);

		if (!check_arg(x))
			ebx = 0;

		ebx *= table[x];

		for (int j = 0; j < 256; j++) {
			if (table[j] > 0)
				table[j]--;
		}
	}

	if (ebx == 666)
		write(1, flag, sizeof(flag));
}
```

where check_arg is a sequence of two x86 instructions,

```
aam 0x12
aad 0xf6
```

which set the sign flag if `x` meets certain conditions, and `atob` just
converts a string to an 8-bit unsigned integer.

To find the correct input we need to find the indices of 16 numbers in the table
whose product is 18 (= 666 / 37) while keeping in mind that every non-zero entry
in the table gets decremented by 1 at every iteration. These indices must also
pass `check_arg` otherwise ebx will be zeroed and we will not get the flag.

All we have to do now is dump the initial value of `table` and write a small
Python script to solve the challenge.

```
root@sqctf:~$ /bin/gates-of-hell 15 2 0 2 0 16 13 11 1 253 5 12 9 7 3 6
flag-526f64696e0000666
```
