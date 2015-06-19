import sys
from PIL import Image


def desaturate(r, g, b):
    d = int(round((float(r) + float(g) + float(b))/3))
    return d, d, d


def increase(r, g, b):
    return (r + 100) % 256, (g + 100) % 256, (b + 100) / 256


im = Image.open('/Users/macellan/Pictures/export/DSC_0031.jpg')
# pixels = list(im.getdata())
width, height = im.size
output = Image.new('RGB', im.size)

for y in range(0, height):
    for x in range(0, width):
        sys.stdout.flush()
        sys.stdout.write('\r%s/%s' % (y, height))
        rgb = im.getpixel((x, y))
        output.putpixel((x, y), increase(*rgb))

output.save("/Users/macellan/Desktop/desaturate.jpg")
