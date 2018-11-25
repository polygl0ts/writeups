from pwn import *

def rec(conn):
    r = conn.recvline()
    print(r)
    if 'in it."' in r:
        return False
    elif "executable!" in r:
        return True
    else:
        return rec(conn)

def iterate_files(cmd, conn):
    with open('ls.txt', 'r') as f:
        files = f.readlines()
        
    for file in files:
        arg = cmd + ' ' + file
        conn.send(arg)
        print(arg)
        if rec(conn):
            return file

def print_flag(r):
    index = r.find('TUCTF{')
    flag = r[index:]
    index = flag.find('}')

    print(flag[:index+1])

def flag():
    conn = remote('18.216.100.42', 12345)

    print(conn.recvuntil('TRY AGAIN.'))
    conn.sendline('1')

    print(conn.recvuntil('please...'))
    conn.sendline('y')

    print(conn.recvuntil('here?"'))
    conn.sendline('ls')

    print(conn.recvuntil('in it."'))

    file = iterate_files('file', conn)

    arg = 'strings ' + file
    print(arg)
    conn.send(arg)
    r = conn.recvall()
    print_flag(r)

if __name__ == '__main__':
    flag()
