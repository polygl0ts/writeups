# Challenge "-.-"
## Description
To 1337-H4X0R:

Our coworker Bob loves a good classical cipher. Unfortunately, he also loves to send everything encrypted with these ciphers. Can you go ahead and decrypt this for me?

Comment : This was given with the file flag.txt

## Solution
The text represents morse code, in a pronouncable way. A morse code of 

### Parsing the text
The text was parsed with "dit" or "di" being taken as a dot. And "dah" or "da" being taken as a dash. Spaces will be mark the words.
The script `toMorse.py` parses the file. And then we used a online morse interpreter to get the solution.
This gave us some data in hex format, which, when parsed in `utf-8` will yield the flag.
So using `test.py` we get the flag.

### Note :
The script `toMorse.py` should run on both versions of python, but was used with Python 3 while `test.py` was used with Python 2.7.

### Flag
Flag was : `gigem{C1icK_cl1CK-y0u_h4v3_m4I1}`

