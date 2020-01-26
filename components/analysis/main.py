import calibrate
import index
import color
import cv2

testing_calibration = calibrate.Calibration()
testing_calibration.calibrate_prep()

testing_index = index.CalculateIndex()
testing_index.applyIndexing()

