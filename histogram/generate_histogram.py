from PIL import Image
import matplotlib.pyplot as plt

image_name = 'img2.jpg'
im = Image.open(image_name)
pix = im.load()
flat = []
w, h = im.size

for x in range(0, w):
    for y in range(0, h):
        R, G, B = pix[x, y]
        brightness = sum([R, G, B])/3
        flat.append(brightness)

plt.hist(flat, 255, histtype='step', align='mid', color='g')
plt.title(f'Histogram of {image_name}')
plt.show()
