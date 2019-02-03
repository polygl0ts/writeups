from pwn import *
import numpy as np
import scipy.ndimage as ndim
import scipy.misc
from matplotlib.image import imread, imsave

# image to grayscale, (change dimension from (x,y,3) to (x,y))
def to_grayscale(im, weights = np.c_[0.333, 0.334, 0.333]):
    tile = np.tile(weights, reps=(im.shape[0],im.shape[1],1))
    return np.sum(tile * im, axis=2)


imagename = 'image.png'

# load all the mapping images into the symbolImage array
alphabet = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
symbolImage = []
for i in alphabet:
	symbolImage.append(to_grayscale(imread("mapping/"+i+".png")[:,:,:3]))

#rotation over image
def rotate(img,angle):
	return ndim.rotate(img,angle,reshape=False,mode="nearest")

#add padding and resize to "scale" the image. (this output an image with the same size)
def resize(img,factor):
	if factor != 0:
		img = np.pad(img, pad_width=factor, mode = "edge")
		return scipy.misc.imresize(img,(27,30))*1.0/255
	return img

#for one image, find the best matching with our alphabet images inside the mapping
def findTextImg(image, verbose=False):
	currentImage = image
	minVal = 1000000
	minElem = ""
	# loop symbol
	for i, elem in enumerate(alphabet):
		# loop rotation angle
		for k in range(-15,15):
			# loop rescaling
			for l in range(0,5):
				angle = k*3
				crop = l*2
				# the symbol image is rotated and rescaled
				symbol = rotate(resize(symbolImage[i],crop),angle)
				#compute the absolute difference between the 2 images
				absolute = np.absolute(np.subtract(currentImage,symbol))
				val = np.sum(absolute)

				if verbose:
					print(elem, crop, angle, val)

				# keep the smallest value and corresponding symbol
				if val < minVal:
					minVal = val
					minElem = elem
	return minElem

# code to interact with the netcat
correct = False
correctNbr = 0
conn = remote("miscc.ctf.nullcon.net",6002)
print(conn.recvuntil("--- press Enter to continue ---"))
conn.sendline("")
conn.recvline()
# loop for each captcha (need 120 corrects over 200)
for i in range(200):
	#received the image in hex format
	hexval = conn.recvline().replace("\n","")

	print(conn.recvuntil("--- Type Answer to provided captcha"))
	print(conn.recvuntil("---"))
	print(conn.recvline())

	# create the image using the hex data
	data = hexval.decode("hex")
	with open(imagename, 'wb') as file:
		file.write(data)

	# convert to grayscale and find the best symbol in each of the 4 parts.
	img = to_grayscale(imread(imagename))
	char1 = findTextImg(img[:,0:30],verbose=False)
	char2 = findTextImg(img[:,30:60])
	char3 = findTextImg(img[:,60:90])
	char4 = findTextImg(img[:,90:120])

	#send the 4 guessed chars 
	textinput = char1+char2+char3+char4
	print("Guessing: "+ textinput)
	conn.sendline(textinput)
	result = conn.recvline()
	print(result)

	#different routine depending if we guessed right or not
	
	if "Wrong!" in result:
		print(conn.recvline())
	else:
		print("#########CORRECT########")
		correctNbr = correctNbr + 1
		print(correctNbr,"correctly guessed")

		# we have 120 corrects answer
		if correctNbr == 120:
			# flag comming
			print(conn.recvline())
			break

		print(conn.recvuntil("--- press Enter to continue ---"))
		conn.sendline("")
		conn.recvline()