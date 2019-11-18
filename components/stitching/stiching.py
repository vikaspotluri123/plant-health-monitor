import os
import sys
os.environ['OPENCV_IO_MAX_IMAGE_PIXELS']=str(2**64)
import cv2
import numpy as np

def loopstitch(path, i):
    for indx, f in enumerate(os.listdir(path), start=0):
        j = path[len(path) - 1]
        if (len(os.listdir(path))-1>indx):
            img_left = os.path.join(path, os.listdir(path)[indx])
            img_right = os.path.join(path, os.listdir(path)[indx + 1])
            comp = stitch(img_left, img_right, i)
            print("write to " + os.listdir(path)[indx + 1])
            ## command to save the composite
            cv2.imwrite(os.path.join(path, os.listdir(path)[indx + 1]), comp)
        else:
            print("loop complete")

    comp_rotate = rotate_img(comp, 90)
    cv2.imwrite("output0/test"+ str(j) + ".jpg", comp_rotate)
    print("comp_rotate written")
    return comp_rotate

def stitch(init_left, init_right, i):
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
        if m.distance < 0.5 *  n.distance: #and i%100 == 1:  ## 0.2 may need to be increased ##
            good.append(m)

    if  i==1:
        # parameters of lines
        draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, flags=2)

        ## draw matches
        img_matches = cv2.drawMatches(img_right, key_right, img_left, key_left, good, None, **draw_params)
        cv2.imshow("debug_matches",img_matches)
        cv2.waitKey(0)

    ## find overlapping region using matches
    MIN_MATCH_COUNT = 10
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

    if i == 1:
        cv2.imshow("stitched_img", stitched_img)
        cv2.waitKey(0)
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

def perspective_correct(img, i):
    #rows, cols, ch = img.shape
    pts1 = np.float32([[56, 65], [368, 52], [28, 387], [389, 390]])
    pts2 = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(img, M, (300, 300))
    plt.subplot(121), plt.imshow(img), plt.title('Input')
    plt.subplot(122), plt.imshow(dst), plt.title('Output')
    plt.show()

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

def erase_black_lines(img):
    # Create mask from all the black lines
    mask = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    cv2.inRange(img, (0, 0, 0), (1, 1, 1), mask)
    mask[mask == 0] = 1
    mask[mask == 255] = 0
    mask = mask * 255

    b_channel, g_channel, r_channel = cv2.split(img)

    # Create a new image with 4 channels the forth channel Aplha will give the opacity for each pixel
    return cv2.merge((b_channel, g_channel, r_channel, mask))

def yes_or_no():
    reply = str(input('would you like to use the debugging mode? (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")

def main(i):
    path0 = r"input0"
    path1 = r"input1"
    # path2 = r"input2"
    # path3 = r"input3"
    pathf = r"output0"

    comp0 = loopstitch(path0, i)
    comp0 = rotate_img(comp0,-90)

    comp1 = loopstitch(path1, i)
    comp1 = rotate_img(comp1,-90)

    # comp2 = loopstitch(path2)
    # comp2 = rotate_img(comp2, -90)
    #
    # comp3 = loopstitch(path3)
    # comp3 = rotate_img(comp3, -90)

    output_comp = loopstitch(pathf, i)

    final = finalize_img(output_comp)

    cv2.imwrite("output0/final.jpg", final)

if __name__ == "__main__":
    i = yes_or_no()
    main(i)

    # img_1 = cv2.imread("test_images/row-1-col-1", 0)
    # img_2 = cv2.imread("test_images/row-1-col-2", 0)
    # img_3 = cv2.imread("test_images/row-1-col-3", 0)
    # img_4 = cv2.imread("test_images/row-1-col-4", 0)
    #
    # cv2.imwrite("test_composites/graypic1.jpg", img_1)
    # cv2.imwrite("test_composites/graypic2.jpg", img_2)
    # cv2.imwrite("test_composites/graypic3.jpg", img_3)
    # cv2.imwrite("test_composites/graypic4.jpg", img_4)


