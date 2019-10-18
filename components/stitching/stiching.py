import cv2
import numpy as np

## read images using opencv library
## img_left/right used for disambiguity
img_left = cv2.imread("field_right.jpg")
img_right = cv2.imread("field_left.jpg")

## start sifting
sift = cv2.xfeatures2d.SIFT_create()

## find key points
key_left , des_left = sift.detectAndCompute(img_left, None)
key_right, des_right = sift.detectAndCompute(img_right, None)

## shows user key points in images
## cv2.imshow("hawaii_left_keypoints.jpeg",cv2.drawKeypoints(img_left,key_left,None))
## cv2.imshow("hawaii_right_keypoints.jpeg",cv2.drawKeypoints(img_right,key_right,None))
## cv2.waitKey(0)

## method for finding matching key points (to be used to identify overlapping region)
match = cv2.BFMatcher()
matches = match.knnMatch(des_left, des_right, k=2)
good = []
for m,n in matches:
    if m.distance < 0.01*n.distance: ## 0.2 may need to be increased ##
        good.append(m)

# parameters of lines
draw_params = dict(matchColor=(0,255,0), singlePointColor=None, flags=2)

## draw matches
img_final = cv2.drawMatches(img_left, key_left, img_right, key_right, good, None, **draw_params)

## display matches
## cv2.imshow("hawaii_final.jpeg", img_final)
## cv2.waitKey(0)

## find overlapping region using matches
MIN_MATCH_COUNT = 10
if len(good) > MIN_MATCH_COUNT:

    src_pts = np.float32([key_left[ m.queryIdx].pt for m in good]).reshape(-1,1,2)
    dst_pts = np.float32([key_right[m.trainIdx].pt for m in good]).reshape(-1,1,2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    h, w, c = img_left.shape
    pts = np.float32([ [0,0] , [0,h-1] , [w-1,h-1] , [w-1,0] ]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts, M)

    # shows user the overlapping region with a rectangle
    # img_right = cv2.polylines(img_right, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
else:
    print("NOT ENOUGH MATCHES AVAILABLE! -", (len(good)/MIN_MATCH_COUNT))

dst = cv2.warpPerspective(img_left, M, (img_right.shape[1] + img_left.shape[1], img_right.shape[0]))
dst[0:img_right.shape[0], 0:img_right.shape[1]] = img_right

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

cv2.imshow("hawaii_test_.jpeg", trim(dst))

## cv2.imsave("hawaii_test_.jpeg", trim(dst))
cv2.waitKey(0)

## idea: given more than 2 images, save each composite as the image to be stiched in the next iteration