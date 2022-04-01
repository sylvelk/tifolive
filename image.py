from PIL import Image
import numpy


def somefunction():
    im = Image.open("frames/maxresdefault.jpg")

    print(im.format, im.size, im.mode)

    im = im.resize((39, 12))

    print(im.format, im.size, im.mode)

    pixels_dec = list(im.getdata())
    width, height = im.size

    pixels_hex = []

    for pixel in pixels_dec:
        p = "#"
        for v in pixel:
            if v < 16:
                p += "0"
            p += str(hex(v).split('x')[1])
        pixels_hex.append(p)

    pixels_hex = numpy.array(pixels_hex).reshape(height, width)

    return pixels_hex.tolist()
