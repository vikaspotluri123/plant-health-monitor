import glob
import os
import sys
import numpy as np
import color
from PyQt5 import QtGui, QtWidgets, QtCore
import straight_line_detection as line
import red_detection as red
import cv2


class CalculateIndex:
    ndvi = None

    def applyIndexing(self):
        files_to_index = self.get_files()
        calfolder = r'C:\Users\Jennifer\Downloads\own_test_0'
        outdir = self.make_calibration_out_dir(calfolder)
        outdir2 = color.make_color_out_dir(calfolder)
        for file in files_to_index:
            img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
            self.processIndex(img)
            h, w = img.shape[:2]
            qImg = QtGui.QImage(self.ndvi.data, w, h, w, QtGui.QImage.Format_Grayscale8)
            self.save_indexed_image(file, qImg, outdir)

            testing_LUT = color.LUT(self)
            testing_LUT.applyLUT(file)

            testing_LUT.save_colored_image(file, testing_LUT.LUT_to_save, outdir2)

            #red.findRed(testing_LUT.LUT_to_save, file)
            #line.drawLines(testing_LUT.LUT_to_save, file)




    def processIndex(self, img):
        self.ndvi = self.calculateIndex(img[:, :, 2], img[:, :, 0])
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

    def get_files(self):
        files = []
        files.extend(CalculateIndex.get_tiff_files_in_dir())
        files.extend(CalculateIndex.get_jpg_files_in_dir())
        return files

    @staticmethod
    def get_jpg_files_in_dir():
        file_paths = []
        file_paths.extend(glob.glob(r'C:\Users\Jennifer\Downloads\own_test_0\Calibrated_1' + os.sep + "*.[jJ][pP][gG]"))
        file_paths.extend(
            glob.glob(r'C:\Users\Jennifer\Downloads\own_test_0\Calibrated_1' + os.sep + "*.[jJ][pP][eE][gG]"))
        return file_paths

    @staticmethod
    def get_tiff_files_in_dir():
        file_paths = []
        file_paths.extend(glob.glob(r'C:\Users\Jennifer\Downloads\own_test_0\Calibrated_1' + os.sep + "*.[tT][iI][fF]"))
        file_paths.extend(
            glob.glob(r'C:\Users\Jennifer\Downloads\own_test_0\Calibrated_1' + os.sep + "*.[tT][iI][fF][fF]"))
        return file_paths

    def save_indexed_image(self, in_image_path, indexed_image, out_dir):
        out_image_path = out_dir + "\INDEXED_" + in_image_path.split('\\')[-1]
        if 'tif' in in_image_path.split('.')[1].lower():
            cv2.imencode(".tif", indexed_image)
            cv2.imwrite(out_image_path, indexed_image)
        else:
            indexed_image.save(out_image_path)

    def make_calibration_out_dir(self, parent_dirname):
        foldercount = 1
        endloop = False
        while endloop is False:
            outdir = parent_dirname + os.sep + "Indexed_" + str(foldercount)

            if os.path.exists(outdir):
                foldercount += 1
            else:
                os.mkdir(outdir)
                endloop = True
        return outdir
