
def import_encoded_data():
    text_file = open("instructions.txt", "r")
    return text_file.readline().split('.')

def dashes_to_binary(dashes):
    indexes = []
    for d in dashes:
        indexes.append(len(d))

    indexes.sort()

    bs = ['0']*((max(indexes)/8)*8 + 8)
    for i in indexes:
        bs[i - 1] = '1'

    return bs

def get_flag():
    enc = import_encoded_data()
    bs = dashes_to_binary(enc)

    flag = ''
    for i in range(0, len(bs), 8):
        flag += chr(int(''.join(bs[i:i+8][::-1]), 2))

    print(flag[::-1])

if __name__ == '__main__':
    get_flag()
