'''
@author:    Matt Raymond
@about:     Created to act as a testing script to show that our coordinate
            rotation works properly
'''

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def rotateCoordinates90(x, y, x_max, y_max, times, dir):
    if dir == "r":
        times = -times%4
    elif dir == "l":
        times = times%4
    else:
        raise ValueError("\'dir\' must be either \'r\' or \'l\'")

    if times == 0:
        return x,y
    elif times == 1:
        return y, x_max-x
    elif times == 2:
        return x_max-x, y_max-y
    else:
        return y_max-y, x


x = 106
y = 52
dir = "l"

for i in range(0,4):
    x = 106
    y = 52
    img = np.array(Image.open("./ast_rot_test.jpg"))
    x_size = img.shape[1]
    y_size = img.shape[0]

    if dir == "r":
        _k = 4-i
    else:
        _k=i

    # rotates to the left
    img = np.rot90(img, k=_k)

    x,y = rotateCoordinates90(x, y, x_size, y_size, i, dir)
    img[y,x] = [255,0,0]

    plt.subplot(2, 2, i+1)
    plt.title("Rotate {} {} times".format(str.upper(dir), i))
    plt.imshow(img)

plt.tight_layout()
plt.show()
