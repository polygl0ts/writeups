input = open("flag.txt").read()
words = input.split(" ") # Splitting the words
morse_words = [] #Storing the words
for w in words:
    chars = w.split("-")
    reconstructed = ""
    for v in chars:
        if v == "dit" or v == "di":
            reconstructed += "."
        elif v == "dah" or v == "da":
            reconstructed += "-"
        else:
            raise Exception("Doesn't exists !")
    morse_words.append(reconstructed)
morse_phrase = ""
for w in morse_words:
        morse_phrase += w + " "
print(morse_phrase)
