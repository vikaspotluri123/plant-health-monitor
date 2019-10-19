import os
os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)
import cv2
import numpy as np

## path to img folder to extract each image
path = r"C:\Users\clark\School\Ecen 403\Image Processing\venv\Scripts\img_list"
image_list = []
for indx, f in enumerate(os.listdir(path), start=1):
    image_list.append(cv2.imread(os.path.join('img_list', f)))

## read images using opencv library
## img_right/left used for disambiguity
img_right = cv2.imread("field_right.jpg")
img_left = cv2.imread("field_left.jpg")

## start sifting
sift = cv2.xfeatures2d.SIFT_create()

## find key points
key_right , des_right = sift.detectAndCompute(img_right, None)
key_left, des_left = sift.detectAndCompute(img_left, None)

## method for finding matching key points (to be used to identify overlapping region)
match = cv2.BFMatcher()
matches = match.knnMatch(des_right, des_left, k=2)
good = []
for m,n in matches:
    if m.distance < 0.1*n.distance: ## 0.2 may need to be increased ##
        good.append(m)

# parameters of lines
draw_params = dict(matchColor=(0,255,0), singlePointColor=None, flags=2)

## draw matches
## img_matches = cv2.drawMatches(img_right, key_right, img_left, key_left, good, None, **draw_params)

## find overlapping region using matches
MIN_MATCH_COUNT = 10
if len(good) > MIN_MATCH_COUNT:

    # query based off right key
    src_pts = np.float32([key_right[ m.queryIdx].pt for m in good]).reshape(-1,1,2)
    # train based off of left key
    dst_pts = np.float32([key_left[m.trainIdx].pt for m in good]).reshape(-1,1,2)

    # find similarities between right and left (src and dst)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # give the left image the pixels from the right image (src -> dst)
    h, w, c = img_right.shape
    pts = np.float32([ [0,0] , [0,h-1] , [w-1,h-1] , [w-1,0] ]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts, M)

    # shows user the overlapping region with a rectangle
    # img_left = cv2.polylines(img_left, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
else:
    print("NOT ENOUGH MATCHES AVAILABLE! -", (len(good)/MIN_MATCH_COUNT))

## try complete when MIN_MATCH_COUNT was met in above conditional
try:
    dst = cv2.warpPerspective(img_right, M, (img_left.shape[1] + img_right.shape[1], img_left.shape[0]))
    dst[0:img_left.shape[0], 0:img_left.shape[1]] = img_left

    # function to erase black regions (caused by residue of src image)
    def trim(frame):
        # crop top
        if not np.sum(frame[0]):
            return trim(frame[1:])
        # crop left
        if not np.sum(frame[-1]):
            return trim(frame[:-2])
        # crop right
        if not np.sum(frame[:,0]):
            return trim(frame[:,1:])
        # crop bottom
        if not np.sum(frame[:,-1]):
            return trim(frame[:,:-2])
        return frame

    trimmed =  trim(dst)
    cv2.imshow("hawaii_test_.jpeg", trimmed)

    ## command to save the composite
    ## cv2.imsave("hawaii_test_.jpeg", trimmed)
    cv2.waitKey(0)

except:
    print("IMAGE STITCH FAILED: NOT ENOUGH MATCHES WERE FOUND")
## idea: given more than 2 images, save each composite as the image to be stiched in the next iteration
