import random
from collections import defaultdict


alphabet = "😀 😁 😂 🤣 😃 😄 😅 😆 😉 😊 😋 😎 😍 😘 🥰 😗 😙 😚 🙂 🤗 🤩 🤔 🤨 😐 😑 😶 🙄 😏 😣 😥 😮 🤐 😯 😪 😫 😴 😌 😛 😜 😝 🤤 😒 😓 😔 😕 🙃 🤑 😲 🙁 😖 😞 😟 😤 😢 😭 😦 😧 😨 😩 🤯 😬 😰 😱 🥵 🥶 😳 🤪 😵 😡 😠 🤬 😷 🤒 🤕 🤢 🤮 🤧 😇 🤠 🤡 🥳 🥴 🥺 🤥 🤫 🤭 🧐 🤓 😈 👿 👹 👺 💀 👻 👽 🤖 💩 😺 😸 😹 😻 😼 😽 🙀 😿 😾"
alphabet = alphabet.replace(" ","")[:100]
perms = list(alphabet)


# functions defined by the chall program
def int2Emoji(i):
	return perms[i%100]

def bigInt2Emoji(i):
	output = ""
	s = str(i)
	for i in range(0, len(s), 2):
		output +=  int2Emoji(int(s[i:i+2]))
	return output


def emoji2Int(e):
    '''inverse of int2Emoji'''
    return perms.index(e)

for i in range(100):
    assert emoji2Int(int2Emoji(i)) == i

def emoji2BigInt(es):
    '''inverse of bigInt2Emoji'''
    return int(''.join(format(emoji2Int(e), '02') for e in es))

# parse the chall output
with open('output.txt') as f:
    # first paragraph: the sample
    sample = []
    for line in f:
        line = line.rstrip()
        if not line:
            break  # end of paragraph
        sample.append(line)

    # second paragraph: the digest
    digest = []
    for line in f:
        line = line.rstrip()
        digest.append(line)

# comcatenate the sample
emoji_sample = []
for line in sample:
    emoji_sample.extend([e for e in line.split()])
# the sample is built from a permutation of range(100)
true_sample = []
for i in range(100):
    true_sample.extend([i, i**2 % 100, i**3 % 100, i**4 % 100, i**5 % 100, (i-1)*i % 100])

# by comparing frequencies, we can partially figure out the permutation
def classify(sample):
    freqs = defaultdict(lambda: 0)
    for k in sample:
        freqs[k] += 1
    classes = defaultdict(lambda: [])
    for k, i in freqs.items():
        classes[i].append(k)
    return classes

code = {}
classified_emoji_sample = classify(emoji_sample)
classified_true_sample = classify(true_sample)
print(" ---- Frequency analysis ----")
for k in classified_emoji_sample:
    if len(classified_emoji_sample[k]) == 1:
        print(classified_emoji_sample[k][0], "->", classified_true_sample[k][0])
        code[classified_emoji_sample[k][0]] = classified_true_sample[k][0]
print(f"{len(code)}/100 found")

# collect (i, i**2 % 100) pairs
emoji_squares = []
for i in range(0,len(emoji_sample),6):
    emoji_squares.append((emoji_sample[i], emoji_sample[i+1]))
    emoji_squares.append((emoji_sample[i+1], emoji_sample[i+3]))

# collect (i, i**3 % 100) pairs
emoji_cubes = []
for i in range(0,len(emoji_sample),6):
    emoji_cubes.append((emoji_sample[i], emoji_sample[i+2]))

# collect (i, i**4 % 100) pairs
emoji_power4 = []
for i in range(0,len(emoji_sample),6):
    emoji_power4.append((emoji_sample[i], emoji_sample[i+3]))

# collect (i, i**5 % 100) pairs
emoji_power5 = []
for i in range(0,len(emoji_sample),6):
    emoji_power5.append((emoji_sample[i], emoji_sample[i+4]))

# collect (i, i**(i-1) % 100) pairs
emoji_triangle = []
for i in range(0,len(emoji_sample),6):
    emoji_triangle.append((emoji_sample[i], emoji_sample[i+5]))

print(" ---- Manual overrides ----")
code['😢'] = 10
code['😛'] = 30
print(f"{len(code)}/100 found")

print(" ---- Forward inference ----")
for i in range(3):
    for e, ee in emoji_squares:
        if e in code:
            if ee in code:
                assert code[ee] == code[e]**2 % 100
            code[ee] = code[e]**2 % 100
    for e, ee in emoji_cubes:
        if e in code:
            if ee in code:
                assert code[ee] == code[e]**3 % 100
            code[ee] = code[e]**3 % 100
    for e, ee in emoji_power4:
        if e in code:
            if ee in code:
                assert code[ee] == code[e]**4 % 100
            code[ee] = code[e]**4 % 100
    for e, ee in emoji_power5:
        if e in code:
            if ee in code:
                assert code[ee] == code[e]**5 % 100
            code[ee] = code[e]**5 % 100
    for e, ee in emoji_triangle:
        if e in code:
            if ee in code:
                assert code[ee] == code[e]*(code[e]-1) % 100
            code[ee] = code[e]*(code[e]-1) % 100
    print(f"{len(code)}/100 found")

square_roots = defaultdict(set)
for i in range(100):
    square_roots[i**2 % 100].add(i)

cube_roots = defaultdict(set)
for i in range(100):
    cube_roots[i**3 % 100].add(i)

power4_roots = defaultdict(set)
for i in range(100):
    power4_roots[i**4 % 100].add(i)

power5_roots = defaultdict(set)
for i in range(100):
    power5_roots[i**5 % 100].add(i)

triangle_roots = defaultdict(set)
for i in range(100):
    triangle_roots[i*(i-1) % 100].add(i)

print(" ---- Backward inference ----")
for i in range(2):
    candidates = defaultdict(lambda: set(range(100)))
    for e,ee in emoji_squares:
        if ee in code and e not in code:
            candidates[e] &= square_roots[code[ee]]
    for e,ee in emoji_cubes:
        if ee in code and e not in code:
            candidates[e] &= cube_roots[code[ee]]
    for e,ee in emoji_power4:
        if ee in code and e not in code:
            candidates[e] &= power4_roots[code[ee]]
    for e,ee in emoji_power5:
        if ee in code and e not in code:
            candidates[e] &= power5_roots[code[ee]]
    for e,ee in emoji_triangle:
        if ee in code and e not in code:
            candidates[e] &= triangle_roots[code[ee]]

    for e in candidates:
        candidates[e] -= set(code.values())
        if len(candidates[e]) == 1:
            code[e] = list(candidates[e])[0]
    print(f"{len(code)}/100 found")

# finally build back perms
for e,i in code.items():
    perms[i] = e

a,b,c,d = [emoji2BigInt(e) for e in digest]

# d == intMsg-a-b-c per chall program
intMsg = a+b+c+d

print(intMsg.to_bytes(512, byteorder='big').decode('utf-8'))
