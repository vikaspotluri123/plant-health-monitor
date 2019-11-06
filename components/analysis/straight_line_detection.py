# Python program to illustrate HoughLine
# method for line detection
import cv2 as cv
import numpy as np
import math

# Reading the required image in
# which operations are to be done.
# Make sure that the image is in the same
# directory in which this python program is

def drawLines(img, file):

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, 50, 150, apertureSize=3)
    minLineLength = 100
    maxLineGap = 10
    lines = cv.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength, maxLineGap)
    for x1, y1, x2, y2 in lines[0]:
        cv.line(img, (x1, y1), (x2, y2), (0, 244, 32), 2)




    out_image_path = r'C:\Users\Jennifer\Downloads\own_test_0\testing'  + "\LINES" + file.split('\\')[-1]
    cv.imwrite(out_image_path, img, [int(cv.IMWRITE_JPEG_QUALITY), 100])
