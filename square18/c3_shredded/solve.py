from itertools import permutations
import os
import sys
from tempfile import NamedTemporaryFile

from PIL import Image
from qrtools import QR


# Combine a list of images
def combine(image_list, f):
    images = map(Image.open, image_list)
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]

        new_im.save(f)


# Check if a QR code is valid
def check_qr(file):
    qr = QR()
    if qr.decode(file):
        print qr.data
        return True

    return False


def main():
    img_folder = 'shredded'

    left_edge = [0, 12, 17]
    right_edge = [11, 13, 9]

    left_squares_left = 5
    left_squares_mid = [6, 15]
    left_squares_center = [2, 16, 25]
    left_squares_right = 26

    spacing_1 = 3

    center_white = [10, 19]
    center_black = [4, 20, 21]

    spacing_2 = 7

    right_square_edge = [8, 14]
    right_square_mid = [1, 18]
    right_squares_center = [22, 23, 24]

    # Perform an exhaustive search on the reduced set of codes
    for left_squares_mid_p in permutations(left_squares_mid):
        for left_squares_center_p in permutations(left_squares_center):
            for center_white_p in permutations(center_white):
                for center_black_p in permutations(center_black):
                    for right_square_edge_p in permutations(right_square_edge):
                        for right_square_mid_p in permutations(right_square_mid):
                            for right_squares_center_p in permutations(right_squares_center):
                                indices = [
                                    left_edge[0], left_edge[1], left_edge[2],

                                    left_squares_left,
                                    left_squares_mid_p[0],
                                    left_squares_center_p[0],
                                    left_squares_center_p[1],
                                    left_squares_center_p[2],
                                    left_squares_mid_p[1],
                                    left_squares_right,

                                    spacing_1,

                                    center_black_p[0], center_white_p[0],
                                    center_black_p[1], center_white_p[1],
                                    center_black_p[2],

                                    spacing_2,

                                    right_square_edge_p[0],
                                    right_square_mid_p[0],
                                    right_squares_center_p[0],
                                    right_squares_center_p[1],
                                    right_squares_center_p[2],
                                    right_square_mid_p[1],
                                    right_square_edge_p[1],

                                    right_edge[0], right_edge[1], right_edge[2],
                                ]

                                # QRTools can only read from a file...
                                with NamedTemporaryFile(suffix='.png') as f:
                                    image_list = list(map(lambda x: os.path.join(img_folder, '{}.png'.format(x)), indices))
                                    combine(image_list, f.name)

                                    if check_qr(f.name):
                                        exit()


if __name__ == '__main__':
    main()
