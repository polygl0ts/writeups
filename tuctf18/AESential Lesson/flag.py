from pwn import *
#from Crypto.Cipher import AES

conn = remote("18.218.238.95",12345)
print(conn.recvuntil(":"))


#cipher = AES.new(key, AES.MODE_ECB)

#find the padding char
for i in range(64,256):
	char = chr(i)
	text = "}"+char * 31
	send_text = text+"a"
	conn.sendline(send_text)
	conn.recvline()
	code = conn.recvline()
	c1, c2, c3 = code[:64], code[64:128], code[128:192]
	if(c1 == c3):
		paddingChar = char
		break
	conn.recvline()
print("padding char is: "+paddingChar)

#find the flag char by char
flag = ""
for i in range(31):
	for j in range(32,127):
		char = chr(j)
		text = char + flag + paddingChar * (31-i)
		send_text = text+"a"+"a"*i
		conn.recvuntil(":")
		conn.sendline(send_text)
		conn.recvline()
		code = conn.recvline()
		c1, c2, c3 = code[:64], code[64:128], code[128:192]
		if(c1 == c3):
			flag = char + flag
			print(flag)
			break
		conn.recvline()

print("The flag is: " + flag)
flag = "TUCTF{A3S_3CB_1S_VULN3R4BL3!!!!}"
