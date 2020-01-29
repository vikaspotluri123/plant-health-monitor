import sys
import copy
import cv2
from bit_depth_conversion import normalize, normalize_rgb


class Calibration:
    monominmax = {"min": 65535.0, "max": 0.0}
    pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                     "greenmax": 0.0, "greenmin": 65535.0,
                     "bluemax": 0.0, "bluemin": 65535.0}
    seed_pass = False
    firstpass = True
    output_path = ""
    input_path = ""
    img_to_pass = None
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

    def calibrate_prep(self, input_file):
        self.firstpass = True
        self.input_path = input_file
        self.pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                              "greenmax": 0.0, "greenmin": 65535.0,
                              "bluemax": 0.0, "bluemin": 65535.0}
        self.maxes = {}
        self.mins = {}

        img = cv2.imread(self.input_path, cv2.IMREAD_UNCHANGED)
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
        filetype = self.input_path.split(".")[-1]

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

        self.CalibratePhotos(base_coef)


    def calibrate(self, mult_values, value):
        slope = mult_values["slope"]
        intercept = mult_values["intercept"]

        return int((slope * value) + intercept)

    def CalibratePhotos(self, coeffs):
        refimg = cv2.imread(self.input_path, -1)
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

        maxpixel, minpixel = self.get_global_max_and_min_calibrated_pixel_values()
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
        self.img_to_pass = refimg

    def calibrate_channel(self, channel, slope, intercept):
        return channel * slope + intercept


    def get_global_max_and_min_calibrated_pixel_values(self):
        ### find the global maximum (maxpixel) and minimum (minpixel) calibrated pixel values over the entire directory.
        red_min = self.pixel_min_max["redmin"]
        red_max = self.pixel_min_max["redmax"]
        blue_min = self.pixel_min_max["bluemin"]
        blue_max = self.pixel_min_max["bluemax"]
        green_min = self.pixel_min_max["greenmin"]
        green_max = self.pixel_min_max["greenmax"]

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
