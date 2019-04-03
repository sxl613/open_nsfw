#!/usr/bin/python
import argparse 
import os
from nsfw_model import NSFWDetect

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to the input file")
    # Optional arguments.
    parser.add_argument("--model_def", help="Model definition file.")
    parser.add_argument("--pretrained_model", help="Trained model weights file.")
    args = parser.parse_args()
    args.input_file = os.path.normpath(args.input_file)
    if not os.path.exists(args.input_file) or not os.path.isfile(args.input_file):
        raise IOError("File does not exist / checkFiletype's argument is not a file.")

    print('Running NSFWDetect on {}'.format(args.input_file))

    nsfw_detect = NSFWDetect(args.model_def, args.pretrained_model)
    #nsfw_detect.classify_video(args.input_file)
    print(args.input_file)
    nsfw_detect.run(args.input_file)


if __name__ == "__main__":
    main()