import random


message, key = None, None
with open("flag.txt") as f:
	message, key = f.readline().split()
	random.seed(int(key))


perms = "😀 😁 😂 🤣 😃 😄 😅 😆 😉 😊 😋 😎 😍 😘 🥰 😗 😙 😚 🙂 🤗 🤩 🤔 🤨 😐 😑 😶 🙄 😏 😣 😥 😮 🤐 😯 😪 😫 😴 😌 😛 😜 😝 🤤 😒 😓 😔 😕 🙃 🤑 😲 🙁 😖 😞 😟 😤 😢 😭 😦 😧 😨 😩 🤯 😬 😰 😱 🥵 🥶 😳 🤪 😵 😡 😠 🤬 😷 🤒 🤕 🤢 🤮 🤧 😇 🤠 🤡 🥳 🥴 🥺 🤥 🤫 🤭 🧐 🤓 😈 👿 👹 👺 💀 👻 👽 🤖 💩 😺 😸 😹 😻 😼 😽 🙀 😿 😾"
perms = perms.replace(" ","")[:100]
perms = ''.join(random.sample(perms,len(perms)))


def int2Emoji(i):
	return perms[i%100]

def bigInt2Emoji(i):
	output = ""
	s = str(i)
	for i in range(0, len(s), 2):
		output +=  int2Emoji(int(s[i:i+2]))
	return output


for i in random.sample(range(100),100):
	print(int2Emoji(i),int2Emoji(i**2),int2Emoji(i**3),int2Emoji(i**4),int2Emoji(i**5), int2Emoji((i-1)*i))

intMsg = int.from_bytes(message.encode('utf-8'), byteorder='big')

a, b, c = 0, 0, 0

while a + b + c >= intMsg or a == 0:
	a = random.randint(intMsg>>3, intMsg)	
	b = random.randint(intMsg>>3, intMsg)	
	c = random.randint(intMsg>>3, intMsg)
	d = intMsg-a-b-c

print()
print(bigInt2Emoji(a))
print(bigInt2Emoji(b))
print(bigInt2Emoji(c))
print(bigInt2Emoji(d))
