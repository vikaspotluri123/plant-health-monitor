import sys
import os
import copy
import glob
import cv2
from bit_depth_conversion import normalize, normalize_rgb

class Calibration:
    monominmax = {"min": 65535.0, "max": 0.0}
    pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                     "greenmax": 0.0, "greenmin": 65535.0,
                     "bluemax": 0.0, "bluemin": 65535.0}
    seed_pass = False
    firstpass = True
    calfolder = ""
    input_path = ""
    JPGS = ["jpg", "JPG", "jpeg", "JPEG"]
    TIFS = ["tiff", "TIFF", "tif", "TIF"]

    BASE_COEFF_SURVEY3_RGN_JPG = {"red": {"slope": 1.3289958195489457, "intercept": -0.17638075239399503},
                                  "green": {"slope": 1.2902528664499517, "intercept": -0.15262065349606874},
                                  "blue": {"slope": 1.387381083964384, "intercept": -0.2193633829181454}
                                  }

    BASE_COEFF_SURVEY3_RGN_TIF = {"red": {"slope": 3.3823966319413326, "intercept": -0.025581742423831766},
                                  "green": {"slope": 2.0198257823722026, "intercept": -0.019624370783744682},
                                  "blue": {"slope": 6.639688121967463, "intercept": -0.025991734455270532}
                                  }




    def calibrate_prep(self, directory):
        self.firstpass = True
        self.input_path = directory
        #r'C:\Users\Jennifer\Downloads\own_test_0'
        files = self.get_files()
        if "tif" or "TIF" or "jpg" or "JPG" in files[0]:
            outdir = self.make_calibration_out_dir()
        self.pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                              "greenmax": 0.0, "greenmin": 65535.0,
                              "bluemax": 0.0, "bluemin": 65535.0}
        self.maxes = {}
        self.mins = {}

        for i, calpixel in enumerate(files):
            img = cv2.imread(calpixel, cv2.IMREAD_UNCHANGED)
            blue = img[:, :, 0]
            green = img[:, :, 1]
            red = img[:, :, 2]

            if self.seed_pass == False:
                self.pixel_min_max["redmax"] = red.max()
                self.pixel_min_max["redmin"] = red.min()

                self.pixel_min_max["greenmax"] = green.max()
                self.pixel_min_max["greenmin"] = green.min()

                self.pixel_min_max["bluemax"] = blue.max()
                self.pixel_min_max["bluemin"] = blue.min()

                self.seed_pass = True

            else:
                try:
                    # compare current image min-max with global min-max (non-calibrated)
                    self.pixel_min_max["redmax"] = max(red.max(), self.pixel_min_max["redmax"])
                    self.pixel_min_max["redmin"] = min(red.min(), self.pixel_min_max["redmin"])

                    self.pixel_min_max["greenmax"] = max(green.max(), self.pixel_min_max["greenmax"])
                    self.pixel_min_max["greenmin"] = min(green.min(), self.pixel_min_max["greenmin"])

                    self.pixel_min_max["bluemax"] = max(blue.max(), self.pixel_min_max["bluemax"])
                    self.pixel_min_max["bluemin"] = min(blue.min(), self.pixel_min_max["bluemin"])


                except Exception as e:
                    print("ERROR: ", e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print(' Line: ' + str(exc_tb.tb_lineno))

        min_max_list = ["redmax", "redmin", "greenmax", "greenmin", "bluemin", "bluemax"]
        filetype = calpixel.split(".")[-1]

        if filetype in self.JPGS:
            base_coef = self.BASE_COEFF_SURVEY3_RGN_JPG
        elif filetype in self.TIFS:
            base_coef = self.BASE_COEFF_SURVEY3_RGN_TIF

        for min_max in min_max_list:
            if len(min_max) == 6:
                color = min_max[:3]

            elif len(min_max) == 7:
                color = min_max[:4]
            else:
                color = min_max[:5]

            self.pixel_min_max[min_max] = self.calibrate(base_coef[color], self.pixel_min_max[min_max])

        self.seed_pass = False

        for i, calfile in enumerate(files):
            self.CalibratePhotos(calfile, base_coef, self.pixel_min_max, outdir)

    def calibrate(self, mult_values, value):
        slope = mult_values["slope"]
        intercept = mult_values["intercept"]

        return int((slope * value) + intercept)

    def make_calibration_out_dir(self):
        foldercount = 1
        endloop = False
        while endloop is False:
            outdir = self.input_path + os.sep + "Calibrated_" + str(foldercount)

            if os.path.exists(outdir):
                foldercount += 1
            else:
                os.mkdir(outdir)
                endloop = True
        return outdir

    def CalibratePhotos(self, photo, coeffs, minmaxes, output_directory):
        refimg = cv2.imread(photo, -1)
        alpha = []
        has_alpha_layer = False
        blue = refimg[:, :, 0]
        green = refimg[:, :, 1]
        red = refimg[:, :, 2]

        if refimg.shape[2] == 4:
            alpha = refimg[:, :, 3]
            has_alpha_layer = True
            refimg = copy.deepcopy(refimg[:, :, :3])

        red = self.calibrate_channel(red, coeffs["red"]["slope"], coeffs["red"]["intercept"])
        green = self.calibrate_channel(green, coeffs["green"]["slope"], coeffs["green"]["intercept"])
        blue = self.calibrate_channel(blue, coeffs["blue"]["slope"], coeffs["blue"]["intercept"])

        maxpixel, minpixel = self.get_global_max_and_min_calibrated_pixel_values("Survey3", "OCN", minmaxes)
        red, green, blue = normalize_rgb(red, green, blue, maxpixel, minpixel)
        if has_alpha_layer:
            original_alpha_depth = alpha.max() - alpha.min()
            alpha = alpha / original_alpha_depth
        if refimg.dtype == 'uint8':
            bit_depth = 8
        elif refimg.dtype == 'uint16':
            bit_depth = 16
        else:
            raise Exception('Calibration input image should be 8-bit or 16-bit')

        red, green, blue, alpha = self.convert_normalized_image_to_bit_depth(bit_depth, red, green, blue, alpha)
        layers = (blue, green, red, alpha) if has_alpha_layer else (blue, green, red)
        refimg = cv2.merge(layers)
        self.save_calibrated_image_without_conversion(photo, refimg, output_directory)

    def calibrate_channel(self, channel, slope, intercept):
        return channel * slope + intercept

    def get_global_max_and_min_calibrated_pixel_values(self, camera_model, filt, minmaxes):
        ### find the global maximum (maxpixel) and minimum (minpixel) calibrated pixel values over the entire directory.
        red_min = minmaxes["redmin"]
        red_max = minmaxes["redmax"]
        blue_min = minmaxes["bluemin"]
        blue_max = minmaxes["bluemax"]
        green_min = minmaxes["greenmin"]
        green_max = minmaxes["greenmax"]

        maxpixel = max([blue_max, red_max, green_max])
        minpixel = min([blue_min, red_min, green_min])

        return maxpixel, minpixel

    @staticmethod
    def convert_normalized_layer_to_bit_depth(layer, bit_depth):
        layer *= 2 ** bit_depth - 1
        layer = layer.astype(int)
        dtype = 'uint' + str(bit_depth)
        layer = layer.astype(dtype)
        return layer

    def convert_normalized_image_to_bit_depth(self, bit_depth, red, green, blue, alpha=None):
        red = Calibration.convert_normalized_layer_to_bit_depth(red, bit_depth)
        green = Calibration.convert_normalized_layer_to_bit_depth(green, bit_depth)
        blue = Calibration.convert_normalized_layer_to_bit_depth(blue, bit_depth)

        if alpha is None:
            alpha = []
        if not alpha == []:
            alpha = Calibration.convert_normalized_layer_to_bit_depth(alpha, bit_depth)

        return red, green, blue, alpha

    def save_calibrated_image_without_conversion(self, in_image_path, calibrated_image, out_dir):
        out_image_path = out_dir + "\CALIBRATED_" + in_image_path.split('\\')[-1]
        if 'tif' in in_image_path.split('.')[1].lower():
            cv2.imencode(".tif", calibrated_image)
            cv2.imwrite(out_image_path, calibrated_image)
        else:
            cv2.imwrite(out_image_path, calibrated_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])


    def get_files(self):
        files = []
        #files.extend(Calibration.get_tiff_files_in_dir())
        files.extend(Calibration.get_jpg_files_in_dir())
        return files

    def get_jpg_files_in_dir(self):
        file_paths = []
        #r'C:\Users\Jennifer\Downloads\own_test_0'
        file_paths.extend(glob.glob(self.input_path + os.sep + "*.[jJ][pP][gG]"))
        file_paths.extend(glob.glob(self.input_path + os.sep + "*.[jJ][pP][eE][gG]"))
        return file_paths

    @staticmethod
    def get_tiff_files_in_dir():
        file_paths = []
        file_paths.extend(glob.glob(r'C:\Users\Jennifer\Downloads\own_test_0' + os.sep + "*.[tT][iI][fF]"))
        file_paths.extend(glob.glob(r'C:\Users\Jennifer\Downloads\own_test_0' + os.sep + "*.[tT][iI][fF][fF]"))
        return file_paths


