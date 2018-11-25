import base64

def reverse(s):
    return s[::-1]


def b32decode(s):
    return base64.b32decode(s)


def reversePigLatin(s):
    return s[-1] + s[:-1]


def rot13(s):
    return s.decode('rot13')


def main():
    print 'Something Something Danger Zone'
    # return '=YR2XYRGQJ6KWZENQZXGTQFGZ3XCXZUM33UOEIBJ'
    return rot13(reversePigLatin(b32decode(reverse('=YR2XYRGQJ6KWZENQZXGTQFGZ3XCXZUM33UOEIBJ'))))


if __name__ == '__main__':
    s = main()
    print s
