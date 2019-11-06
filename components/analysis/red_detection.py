# import the necessary packages
import numpy as np
import argparse
import cv2

def findRed(image, file):
    boundaries = [([38, 0, 165], [97, 174, 251])]
    for (lower, upper) in boundaries:
        # create NumPy arrays from the boundaries
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(image, lower, upper)
        image[mask>0] = (179, 179, 179)

        out_image_path = r'C:\Users\Jennifer\Downloads\own_test_0\testing' + "\Red" + file.split('\\')[-1]
        cv2.imwrite(out_image_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
