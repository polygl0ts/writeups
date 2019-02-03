nullcon HackIM 2019: Captcha Forest
=============================

## Description

A baby captcha just for you.

`nc misc.ctf.nullcon.net 6001`


The server sent us a `png` image in hexadecimal. We have to solve the captcha and output 4 corresponding characters.

This challenge need to be solved 200 times to output the flag.

The image is a concatenation of 4 characters from the Bill Cipher (a code in Gravity Fall).

#### Example of characters

![A](mapping/A.png)
![B](mapping/B.png)
![C](mapping/C.png)
![D](mapping/D.png)

## Solution

Using Google, we found a table with similar character for the Bill Cipher.

![Bill Cipher](gravityfallsdecode.png)

The mapping works if we answer manually to the server, so that's great.

Right now we would like to automate it. The quality of the image seems not enough to do a good enough matching. 
So with more google search I found the [exact images](https://www.dcode.fr/gravity-falls-bill-cipher) used in the challenge!

From there we just split the catpcha in 4, pick the symbol with the least absolute difference for each of the 4 images.

It's then the trivial to communicate with the server and get the flag.

## Code

The code is written [here](script.py)

The image mapping is stored [here](mapping)

## Flag

`hackim19{Since_you_are_not_a_robot_I_will_give_you_the_flag}`