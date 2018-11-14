import base64
import re
import string
import tempfile

# Interact with the challenge
import requests
from bs4 import BeautifulSoup

# Image processing
from PIL import Image, ImageDraw, ImageFont
import numpy as np

CHARSET = string.digits + '()x+-'
URL = 'https://hidden-island-93990.squarectf.com/ea6c95c6d0ff24545cad'
FONT_REGEX = r';base64,([A-Za-z0-9\+/=]+)\''
FLAG_REGEX = r'flag-[0-9a-f]{8,32}'
CHAR_SIZE = (50, 80)


# Compute the MSE between two images of the same size
def img_mse(im1, im2):
    return  np.sum(np.square(np.array(im2, dtype=np.int32) - np.array(im1, dtype=np.int32)))


def solve(char_db):
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    expr = soup.p.string
    expr_chars = set(expr)

    # Load the challenge font
    with tempfile.NamedTemporaryFile() as f:
        f.write(base64.b64decode(re.search(FONT_REGEX, soup.style.string).group(1)))
        f.flush()
        font = ImageFont.truetype(f.name, CHAR_SIZE[1])

    token = next(e['value'] for e in soup.find_all('input') if e['name'] == 'token')

    charmap = {}

    # Translate the equation to 'regular ASCII'
    for c in expr_chars:
        # Space is always space
        if c == ' ':
            charmap[' '] = ' '
            continue

        # Render the character using the challenge font
        txt = Image.new('RGB', CHAR_SIZE, (255,255,255))
        d = ImageDraw.Draw(txt)
        d.text((0, 0), c, font=font, fill=(0,0,0))

        min_mse = None
        real_char = None

        # Find the most similar entry in the database
        for x, img in char_db:
            mse = img_mse(img, txt)
            if not min_mse or mse < min_mse:
                min_mse = mse
                real_char = x

        charmap[c] = real_char

    rec_expr = ''.join([charmap[c] for c in expr]).replace('x', '*')

    # Eval the expression
    res = eval(rec_expr)

    # Get the flag
    r = requests.post(URL, data={'answer': res, 'token': token})
    print re.search(FLAG_REGEX, r.text).group(0)



def main():
    # Load character database
    char_db = [
        (c, Image.open('chars_rec/{}.webp'.format(c))) for c in CHARSET
    ]

    solve(char_db)


if __name__ == '__main__':
    main()
