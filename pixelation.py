import os, glob
import cv2
import numpy as np
from PIL import Image 
from math import sqrt
import PIL.ImageOps    


def nearest_color(pixel, rgb_palette):
    """
    - Helper to find nearest color to pixel from given palette using distance formula with 3-d

    :param str pixel = RGB tuple 
    :param dict rgb_palette = dictionary with location and rgb tuple for each color in palette
    :return location of nearest palette RGB color
    :rtype int 
    """

    # Distance formula on each item in palette 
    r, g, b = pixel
    color_diffs = []
    for location, color in rgb_palette.items():
        cr, cg, cb = color
        color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        color_diffs.append((color_diff, color, location))

    # Return location of nearest pixel value 
    return min(color_diffs)[2]


def pixelation(filename, width, height, palette):
    """
    Part 1: Image Pixelation
    - Pixelate input image using given parameters

    :param str filename = path to an image file (ex. "taylor.png")
    :param int width = final width of resultant image (ex. 200)
    :param int height = final height of resultant image (ex. 200)
    :param list palette = list of hex triplet RGB values (ex. ["#FFFFFF", "#C0C0C0", "#808080", "#000000"])
    :return conversion of input image set to numerical values corresponding to the palette 
    :rtype 2D list 
    """

    # Convert color palette from hex values to RGB tuples dictionary
    rgb_dict = {}
    for j in range(len(palette)): 
        tmp = palette[j].lstrip("#")
        rgb_dict[j] = tuple(int(str(tmp[i:i+2]), 16) for i in (0, 2, 4))

    # Read and resize input image
    image = cv2.imread(filename)

    # print(len(image))
    # print(len(image[0]))
    
    resized = cv2.resize(image, dsize=(width, height), interpolation=cv2.INTER_CUBIC)

    # Find location of nearest colors in color palette
    loc_img = []
    count = 0
    for i in range (height):
        curr = []
        for j in range(width):
            # Find nearest palette color to current pixel color 
            curr.append(nearest_color(tuple(resized[i][j]), rgb_dict))
            print(f"{count} out of {height * width}")
            count += 1
        loc_img.append(curr)
    
    # Return hex_img with locations of palette colors
    print("Done!")
    return loc_img


def save_image(loc_img, width, height, palette):
    """
    - Helper to save image file for testing purposes 

    :param 2D list loc_img = image in terms of palette indices
    :param int width = final width of resultant image (ex. 200)
    :param int height = final height of resultant image (ex. 200)
    :param list palette = list of hex triplet RGB values (ex. ["#FFFFFF", "#C0C0C0", "#808080", "#000000"])
    :return None
    :rtype None
    """
    # Convert color palette from hex values to RGB tuples dictionary
    rgb_dict = {}
    for j in range(len(palette)): 
        tmp = palette[j].lstrip("#")
        rgb_dict[j] = tuple(int(str(tmp[i:i+2]), 16) for i in (0, 2, 4))

    # Avoid writing the same file twice (for testing use)
    for filename in glob.glob("./version*"):
        os.remove("resized_image.jpeg")

    # Convert loc_img back into rgb values for testing 
    test = []
    for i in range(height):
        curr = []
        for j in range(width):
            curr.append(rgb_dict[loc_img[i][j]])
        test.append(curr)

    cv2.imwrite('resized_image.jpeg', np.float32(test))
    



# img = pixelation("images/swiper.jpeg", 200, 200, ["#cc00cc", "#0066ff", "#00ff00", "#ff3300", "#ffffff", "#000000", "#2676d8", "#ee63Bd", "#f96f29", "#ffb40d", "#4445ff", "#FFEE75"])
# save_image(img, 200, 200, ["#cc00cc", "#0066ff", "#00ff00", "#ff3300", "#ffffff", "#000000", "#2676d8", "#ee63Bd", "#f96f29", "#ffb40d", "#4445ff", "#FFEE75"])