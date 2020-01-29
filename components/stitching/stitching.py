import os
import sys
os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)
import cv2
import numpy as np
import time
import shutil
from pathlib import Path

PATH_SEP = os.path.sep

def loopstitch(path):
    for indx, f in enumerate(os.listdir(path), start=0):
        j = path[len(path) - 1]
        if (len(os.listdir(path))-1>indx):
            img_left = os.path.join(path, os.listdir(path)[indx])
            img_right = os.path.join(path, os.listdir(path)[indx + 1])
            comp = stitch(img_left, img_right)
            print("write to " + os.listdir(path)[indx + 1])
            ## command to save the composite
            cv2.imwrite(os.path.join(path, os.listdir(path)[indx + 1]), comp)
        else:
            print("loop complete")

    comp_rotate = rotate_img(comp, 90)
    cv2.imwrite("output0/test"+ str(j) + ".jpg", comp_rotate)
    print("comp_rotate written")
    return comp_rotate

def stitch(init_left, init_right):
    print("beginnging of stitch")
    ## read images using opencv library
    ## img_right/left used for disambiguity
    img_left = cv2.imread(init_left)
    img_right = cv2.imread(init_right)

    ## start sifting
    sift = cv2.xfeatures2d.SIFT_create()

    ## find key points
    key_right, des_right = sift.detectAndCompute(img_right, None)
    key_left, des_left = sift.detectAndCompute(img_left, None)

    ## method for finding matching key points (to be used to identify overlapping region)
    match = cv2.BFMatcher()
    matches = match.knnMatch(des_right, des_left, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.5 *  n.distance:
            good.append(m)

    ## find overlapping region using matches
    MIN_MATCH_COUNT = 5
    if len(good) > MIN_MATCH_COUNT:

        # query based off right key
        src_pts = np.float32([key_right[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        # train based off of left key
        dst_pts = np.float32([key_left[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # find similarities between right and left (src and dst)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # give the left image the pixels from the right image (src -> dst)
        h, w, c = img_right.shape ## add "c" in with h and w if color pics are used
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        # shows user the overlapping region with a rectangle
        # img_left = cv2.polylines(img_left, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
    else:
        print("NOT ENOUGH MATCHES AVAILABLE! -", (len(good) / MIN_MATCH_COUNT))

    dst = cv2.warpPerspective(img_right, M, (img_left.shape[1] + img_right.shape[1], img_left.shape[0]))
    dst[0:img_left.shape[0], 0:img_left.shape[1]] = img_left
    stitched_img = trim(dst)

    ## return the trimmed composite after stitching the inputs
    return stitched_img

# function to erase black regions (caused by residue of src image)
def trim(frame):
    # crop top
    if not np.sum(frame[0]):
        return trim(frame[1:])
    # crop left
    if not np.sum(frame[-1]):
        return trim(frame[:-2])
    # crop right
    if not np.sum(frame[:, 0]):
        return trim(frame[:, 1:])
    # crop bottom
    if not np.sum(frame[:, -1]):
        return trim(frame[:, :-2])
    return frame

def rotate_img(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))

def finalize_img(image):
    return rotate_img(image,180)

def loopstitch_wrapper(path):
    comp = loopstitch(path)
    cv2.imshow("composite image", comp)
    return comp

def stitching_main(inputDir, outFilename, numRows, numCols):
    # to hold all input paths
    paths = []

    # create a directory for each row
    for i in range(0, numRows):
        i = str(i)
        file = inputDir + PATH_SEP + "input" + i

        if os.path.exists(file):
            shutil.rmtree(file)

        os.makedirs(file)
        paths.append(file)

    # rotate images -90 degrees (might not be necessary in final product)
    # for img in os.listdir(inputDir):
    #     rotate_img(img, -90)

    # move images into their respective directories
    for i in range(0, numRows):
        i = str(i)
        for j in range(0, numCols):
            # @NOTE: we always use the first file since the previous file was moved!
            shutil.move(inputDir + PATH_SEP + os.listdir(inputDir)[0], inputDir + PATH_SEP + "input" + i)

    for i in paths:
        loopstitch_wrapper(i)

    output_comp = loopstitch_wrapper(outFilename)

    final = finalize_img(output_comp)

    cv2.imwrite(outFilename, final)
    # cv2.imshow("final.jpg", final)
    cv2.waitKey(0)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: argv[0] inputDir outFilename, numRows, numCols")
        exit(1)

    stitching_main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
