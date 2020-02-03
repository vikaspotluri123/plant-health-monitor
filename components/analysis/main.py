import calibrate
import index
import sys

def analysis_main(input_file, output_file):
    calibration = calibrate.Calibration()
    calibration.calibrate_prep(input_file)

    indexing = index.CalculateIndex()
    indexing.applyIndexing(calibration.img_to_pass, output_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: stitching.py inputDirectory")
        exit()

    analysis_main(
        sys.argv[1].replace('"', ''),
        sys.argv[2].replace('"', '')
    )

