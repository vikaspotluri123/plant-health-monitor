import calibrate
import index
import sys

def analysis_main(directory):
    testing_calibration = calibrate.Calibration()
    testing_calibration.calibrate_prep(directory)

    testing_index = index.CalculateIndex()
    testing_index.applyIndexing(directory)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: stitching.py inputDirectory")
        exit()

    analysis_main(sys.argv[1])
