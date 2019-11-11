import os
os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)
import cv2
import numpy as np

def loopstitch(path):
    for indx, f in enumerate(os.listdir(path), start=0):
        if (len(os.listdir(path))-1>indx):
            img_left = os.path.join('input', os.listdir(path)[indx])
            img_right = os.path.join('input', os.listdir(path)[indx + 1])
            comp = stitch(img_left, img_right)
            print("write to " + os.listdir(path)[indx + 1])
            ## command to save the composite
            cv2.imwrite(os.path.join('input', os.listdir(path)[indx + 1]), comp)
        else:
            print("loop complete")

    cv2.imwrite("output", comp)

def stitch(init_left, init_right):
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
        if m.distance < 0.2 * n.distance:  ## 0.2 may need to be increased ##
            good.append(m)

    # parameters of lines
    draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, flags=2)

    ## draw matches
    img_matches = cv2.drawMatches(img_right, key_right, img_left, key_left, good, None, **draw_params)
    # cv2.namedWindow('img_matches', cv2.WINDOW_NORMAL)
    # cv2.imshow("img_matches", img_matches)
    # cv2.resizeWindow('img_matches', 1000, 500)
    # cv2.waitKey(0)

    ## find overlapping region using matches
    MIN_MATCH_COUNT = 10
    if len(good) > MIN_MATCH_COUNT:

        # query based off right key
        src_pts = np.float32([key_right[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        # train based off of left key
        dst_pts = np.float32([key_left[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # find similarities between right and left (src and dst)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 10.0)

        # give the left image the pixels from the right image (src -> dst)
        h, w, c = img_right.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        # shows user the overlapping region with a rectangle
        # img_left = cv2.polylines(img_left, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
    else:
        print("NOT ENOUGH MATCHES AVAILABLE! -", (len(good) / MIN_MATCH_COUNT))

    dst = cv2.warpPerspective(img_right, M, (img_left.shape[1] + img_right.shape[1], img_left.shape[0]))
    dst[0:img_left.shape[0], 0:img_left.shape[1]] = img_left

    ## return the trimmed composite after stitching the inputs
    return trim(dst)

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

def perspective_correct(img, i):
    #rows, cols, ch = img.shape
    pts1 = np.float32([[56, 65], [368, 52], [28, 387], [389, 390]])
    pts2 = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(img, M, (300, 300))
    plt.subplot(121), plt.imshow(img), plt.title('Input')
    plt.subplot(122), plt.imshow(dst), plt.title('Output')
    plt.show()


path = r"C:\Users\clark\School\Ecen 403\Image Processing\venv\Scripts\input"
loopstitch(path)

# path = r"C:\Users\clark\School\Ecen 403\Image Processing\venv\Scripts\input"
# img = cv2.imread(os.path.join('input', os.listdir(path)[0]))
# cv2.imshow("initial",img)
# resized_image = cv2.resize(img, (500, 500))
# perspective_correct(resized_image, 0)
