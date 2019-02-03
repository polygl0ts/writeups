from pwn import *
import numpy as np
from matplotlib.image import imread

def to_grayscale(im, weights = np.c_[0.333, 0.334, 0.333]):
    tile = np.tile(weights, reps=(im.shape[0],im.shape[1],1))
    return np.sum(tile * im, axis=2)

imagename = 'image.png'

#load the 26 symbol images
alphabet = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
symbolImage = []
for i in alphabet:
	symbolImage.append(to_grayscale(imread("mapping/"+i+".png")[:,:,:3]))


# function that output the best symbol compared with the image input
def findTextImg(image):
	currentImage = image
	minVal = 1000
	minElem = ""
	# check every symbol of the alphabet
	for i, elem in enumerate(alphabet):
		symbol = symbolImage[i]
		# do the absolute difference with the image
		val = np.sum(np.absolute(np.subtract(currentImage,symbol)))
		# choose the best symbol
		if val < minVal:
			minVal = val
			minElem = elem
	return minElem


# communication with the server
conn = remote("misc.ctf.nullcon.net",6001)

# need to solve 200 captcha
for i in range(200):
	print(conn.recvuntil("--- press Enter to continue ---"))
	conn.sendline("")
	conn.recvline()

	# received the captcha in hex
	hexval = conn.recvline().replace("\n","")
	print(conn.recvuntil("--- Type Answer to provided captcha"))
	print(conn.recvuntil("---"))
	print(conn.recvline())

	# convert the hex to a png image
	data = hexval.decode("hex")
	with open(imagename, 'wb') as file:
		file.write(data)

	# load the image and split it into 4
	img = to_grayscale(imread(imagename))

	# for each part, find the best corresponding character
	char1 = findTextImg(img[:,0:30])
	char2 = findTextImg(img[:,30:60])
	char3 = findTextImg(img[:,60:90])
	char4 = findTextImg(img[:,90:120])

	# create and send the answer
	textinput = char1+char2+char3+char4
	print("Guessing: "+ textinput)
	conn.sendline(textinput)
	print(conn.recvline())

# the flag is coming

print(conn.recvline())
print(conn.sendline(""))
print(conn.recvline())
print(conn.recvline())
print(conn.recvline())