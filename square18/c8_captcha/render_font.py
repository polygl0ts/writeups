import base64
import os
import re
import string
import tempfile

# Interact with the challenge
import requests
from bs4 import BeautifulSoup

# Image processing
from PIL import Image, ImageDraw, ImageFont


CHARSET = string.digits + '()x+-'
URL = 'https://hidden-island-93990.squarectf.com/ea6c95c6d0ff24545cad'
FONT_REGEX = r';base64,([A-Za-z0-9\+/=]+)\''
OUT_DIR = 'chars_rec'
CHAR_SIZE = (50, 80)


def main():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    expr = soup.p.string
    expr_chars = set(expr)

    # Load the challenge font
    with tempfile.NamedTemporaryFile() as f:
        f.write(base64.b64decode(re.search(FONT_REGEX, soup.style.string).group(1)))
        f.flush()
        font = ImageFont.truetype(f.name, CHAR_SIZE[1])

    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)

    for c in expr_chars:
        txt = Image.new('RGB', CHAR_SIZE, (255,255,255))
        d = ImageDraw.Draw(txt)
        d.text((0, 0), c, font=font, fill=(0,0,0))

        txt.save('{}/{}.webp'.format(OUT_DIR, c), lossless=True)


if __name__ == '__main__':
    main()

