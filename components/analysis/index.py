import sys
import numpy as np
import color
import cv2


class CalculateIndex:
    ndvi = None

    def applyIndexing(self, calibrated_image, output_file):
        self.processIndex(calibrated_image)
        #h, w = calibrated_image.shape[:2]
        #qImg = QtGui.QImage(self.ndvi.data, w, h, w, QtGui.QImage.Format_Grayscale8)

        cv2.imwrite(r'C:\Users\Jennifer\Downloads\own_test_0\indexed.JPG', self.ndvi)

        testing_LUT = color.LUT(self)
        testing_LUT.applyLUT()


        testing_LUT.save_colored_image(testing_LUT.LUT_to_save, output_file)


    def processIndex(self, img):
        self.ndvi = self.calculateIndex(img[:, :, 0], img[:, :, 2])
        self.ndvi -= self.ndvi.min()
        self.ndvi /= (self.ndvi.max())
        self.ndvi *= 255.0
        self.ndvi = np.around(self.ndvi)
        self.ndvi = self.ndvi.astype("uint8")
        self.ndvi = cv2.equalizeHist(self.ndvi)

    def calculateIndex(self, visible, nir):
        try:
            nir[nir == 0] = 1
            visible[visible == 0] = 1
            if nir.dtype == "uint8":
                nir = nir / 255.0
                visible = visible / 255.0
            elif nir.dtype == "uint16":
                nir /= 65535.0
                visible /= 65535.0

            numer = nir - visible
            denom = nir + visible

            index = numer / denom
            return index
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))
            return False







