import calibrate
import index

directory = ""
testing_calibration = calibrate.Calibration()
testing_calibration.calibrate_prep(directory)

testing_index = index.CalculateIndex()
testing_index.applyIndexing(directory)
