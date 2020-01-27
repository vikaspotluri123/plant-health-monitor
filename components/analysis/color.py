import numpy as np
import copy
import glob
import sys
import os
import cv2
from PyQt5 import QtGui, QtWidgets, QtCore


class LUT:
    ndvipsuedo = None
    LUT_to_save = None
    LUT_Min = -1.0
    LUT_Max = 1.0
    _lut = None
    _min = None
    _max = None
    yval = [[165, 0, 38],
            [215, 46, 39],
            [251, 174, 98],
            [255, 255, 190],
            [168, 217, 105],
            [33, 178, 25],
            [12, 103, 56]]

    def __init__(self, parent=None):
        self.parent = parent

    def applyLUT(self, file):
        #files_to_color = self.get_files()
        #calfolder = r'C:\Users\Jennifer\Downloads\own_test_0'
        #if "tif" or "TIF" or "jpg" or "JPG" in files_to_color[0]:
        #outdir = self.make_color_out_dir(calfolder)
        self.processLUT()
        #frame = QtGui.QImage(self.ndvipsuedo.data, w, h, w * 4, QtGui.QImage.Format_RGBA8888)
        #self.save_colored_image(file, self.LUT_to_save, outdir)


    def processLUT(self):
        self._lut = np.zeros((256, 1, 3), dtype=np.uint8)

        for x, y in enumerate(range(0, 42)):
            self._lut[y, 0, 0] = int(self.yval[0][0] + (x * ((self.yval[1][0] - self.yval[0][0]) / 42)))
            self._lut[y, 0, 1] = int(self.yval[0][1] + (x * ((self.yval[1][1] - self.yval[0][1]) / 42)))
            self._lut[y, 0, 2] = int(self.yval[0][2] + (x * ((self.yval[1][2] - self.yval[0][2]) / 42)))

        for x, y in enumerate(range(42, 84)):
            self._lut[y, 0, 0] = int(self.yval[1][0] + (x * ((self.yval[2][0] - self.yval[1][0]) / 42)))
            self._lut[y, 0, 1] = int(self.yval[1][1] + (x * ((self.yval[2][1] - self.yval[1][1]) / 42)))
            self._lut[y, 0, 2] = int(self.yval[1][2] + (x * ((self.yval[2][2] - self.yval[1][2]) / 42)))

        for x, y in enumerate(range(84, 126)):
            self._lut[y, 0, 0] = int(self.yval[2][0] + (x * ((self.yval[3][0] - self.yval[2][0]) / 42)))
            self._lut[y, 0, 1] = int(self.yval[2][1] + (x * ((self.yval[3][1] - self.yval[2][1]) / 42)))
            self._lut[y, 0, 2] = int(self.yval[2][2] + (x * ((self.yval[3][2] - self.yval[2][2]) / 42)))

        for x, y in enumerate(range(126, 168)):
            self._lut[y, 0, 0] = int(self.yval[3][0] + (x * ((self.yval[4][0] - self.yval[3][0]) / 42)))
            self._lut[y, 0, 1] = int(self.yval[3][1] + (x * ((self.yval[4][1] - self.yval[3][1]) / 42)))
            self._lut[y, 0, 2] = int(self.yval[3][2] + (x * ((self.yval[4][2] - self.yval[3][2]) / 42)))

        for x, y in enumerate(range(168, 210)):
            self._lut[y, 0, 0] = int(self.yval[4][0] + (x * ((self.yval[5][0] - self.yval[4][0]) / 42)))
            self._lut[y, 0, 1] = int(self.yval[4][1] + (x * ((self.yval[5][1] - self.yval[4][1]) / 42)))
            self._lut[y, 0, 2] = int(self.yval[4][2] + (x * ((self.yval[5][2] - self.yval[4][2]) / 42)))

        for x, y in enumerate(range(210, 256)):
            self._lut[y, 0, 0] = int(self.yval[5][0] + (x * ((self.yval[6][0] - self.yval[5][0]) / 46)))
            self._lut[y, 0, 1] = int(self.yval[5][1] + (x * ((self.yval[6][1] - self.yval[5][1]) / 46)))
            self._lut[y, 0, 2] = int(self.yval[5][2] + (x * ((self.yval[6][2] - self.yval[5][2]) / 46)))

        try:
            self._min = float(self.LUT_Min)
            self._max = float(self.LUT_Max)
            range_ = copy.deepcopy(self.parent.ndvi)
            temp = copy.deepcopy(self.parent.ndvi)

            global_lut_min = round(self.LUT_Min, 2)
            global_lut_max = round(self.LUT_Max, 2)

            workingmin = (((self._min / (abs((global_lut_min)) if self._min < 0 else global_lut_min * -1)) + 1) / 2) * 255
            workingmax = (((self._max / (abs((global_lut_max)) if self._max > 0 else global_lut_min * -1)) + 1) / 2) * 255

            range_[range_ < workingmin] = workingmin
            range_[range_ > workingmax] = workingmax
            range_ = (((range_ - range_.min()) / (range_.max() - range_.min())) * 255).astype("uint8")
            range_ = cv2.cvtColor(range_, cv2.COLOR_GRAY2RGB)
            self.ndvipsuedo = cv2.LUT(range_, self._lut)

            self.ndvipsuedo[temp <= workingmin] = 0
            self.ndvipsuedo[temp >= workingmax] = 0
            self.ndvipsuedo = cv2.cvtColor(self.ndvipsuedo, cv2.COLOR_RGB2RGBA)
            alpha = self.ndvipsuedo[:, :, 3]
            alpha[self.ndvipsuedo[:, :, 0] == 0] = 0
            alpha[self.ndvipsuedo[:, :, 1] == 0] = 0
            alpha[self.ndvipsuedo[:, :, 2] == 0] = 0
            self.LUT_to_save = cv2.cvtColor(self.ndvipsuedo, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(e)


    def save_colored_image(self, in_image_path, indexed_image, out_dir):
        out_image_path = out_dir + "\COLORED_" + in_image_path.split('\\')[-1]
        if 'tif' in in_image_path.split('.')[1].lower():
            cv2.imencode(".tif", indexed_image)
            cv2.imwrite(out_image_path, indexed_image)
        else:
            cv2.imwrite(out_image_path, indexed_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

def make_color_out_dir(parent_dirname):
        foldercount = 1
        endloop = False
        while endloop is False:
            outdir = parent_dirname + os.sep + "Colored_" + str(foldercount)

            if os.path.exists(outdir):
                foldercount += 1
            else:
                os.mkdir(outdir)
                endloop = True
        return outdir