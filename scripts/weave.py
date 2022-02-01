#!/usr/bin/python3

import os
import subprocess
import logging
import sys
import argparse

#logging.basicConfig(format="%(astime)s %(message)s")
logging.basicConfig(format="%(astime)s %(message)s", level=logging.DEBUG)

# Args: ./weave.py <output_file> <files>
args = sys.argv
#output_file = args[1]

# Remove args and remains for files.
#args.pop(0)
#args.pop(0)
#files = args

#print("args:", args)
#print("output_file:", output_file)
#print("files:", files)

# Debug
#logging.debug("args: %s", args)
#logging.debug("output_file: %s", output_file)
#logging.debug("files: %s", files)

# ffmpeg -i input1.mp4 -i input2.webm \
# -filter_complex "[0:v:0] [0:a:0] [1:v:0] [1:a:0] concat=n=2:v=1:a=1 [v] [a]" \
# -map "[v]" -map "[a]" output.mp4

# Define main class
class main():
    # Set main
    def __init__(self):
        pass

    # Define arguments
    def get_args(self):
        parser = argparse.ArgumentParser(description="Weave files together with ffmpeg.")
        parser.add_argument("--output", help="Set output file.")
        parser.add_argument("--files", nargs="*", help="Set files to merge together.")

        args = parser.parse_args()
        outputArg = args.output
        filesArg = args.files

        if outputArg: 
            outputArg = outputArg
        else:
            outputArg = None

        if filesArg:
            filesArg = filesArg
        else:
            filesArg = None


        return {
                "outputArg": outputArg,
                "filesArg": filesArg
                }

    # Check files
    def check(self, files):
        if files is None:
            print("Files not set.")
            sys.exit(1)

        for file in files:
            if not os.path.exists(file):
                print("Could not find", file)
                sys.exit(1)

        return(files)

    # Convert files
    # def convert(self, files):
    #    pass

    # Weave files together
    def weave(self, output_file, files):
        if output_file is None or files is None:
            print("output_file or files not set.")
            sys.exit(1)
        files_num = len(files)

        ffmpeg_command = []
        ffmpeg_command.extend(["ffmpeg", "-stats"])

        # ffmpeg -i input1.mp4 -i input2.webm \
        # -filter_complex "[0:v:0] [0:a:0] [1:v:0] [1:a:0] concat=n=2:v=1:a=1 [v] [a]" \
        # -map "[v]" -map "[a]" output.mp4
        for file in files:
            ffmpeg_command.extend(["-i", file])

            # Get size of input files
            m.size(file)

        # append filtering
        ffmpeg_command.extend(['-filter_complex', '[0:v:0] [0:a:0] [1:v:0] [1:a:0] concat=n='+str(files_num)+':v=1:a=1 [v] [a]', "-map", '[v]', "-map", '[a]'])

        # Append output_file
        ffmpeg_command.append(output_file)

        # run command
        print("ffmpeg_command:", ffmpeg_command)
        logging.debug("ffmpeg_command: %s", ffmpeg_command)
        try:
            run_ffmpeg = subprocess.run(ffmpeg_command)

            # Get size of output file
            m.size(output_file)
        except subprocess.RuntimeError:
            print("Could not run ffmpeg.")
            sys.exit(1)

    # Print output size of file
    def size(self, inputArg):
        if inputArg is None:
            print("inputArg not defined.")
            sys.exit(1)

        if not os.path.exists(inputArg):
            print(inputArg, "not found.")
            return 1
            # sys.exit(1)

        inputArgSize = os.path.getsize(inputArg)
        num = inputArgSize
        suffixes = ["B", "KB", "MB", "GB", "TB"]
        for x in suffixes:
            if num < 1024.0:
                print(inputArg, "is", round(num, 2), x)
                break
            num /= 1024.0
# Run
m = main()

# Get args
outputArg = m.get_args()["outputArg"]
filesArg = m.get_args()["filesArg"]

# Debug
logging.debug("outputArg: %s", outputArg)
logging.debug("filesArg: %s", filesArg)

# Check each file
files = m.check(filesArg)

# Merge files to output_file
m.weave(outputArg, filesArg)
