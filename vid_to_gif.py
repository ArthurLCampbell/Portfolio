#!/usr/bin/env python3

import os
import subprocess
import argparse
import platform
import sys
import logging
import math
# import humanize
# from hurry.filesize import size

# Configure logging
# logging.basicConfig(format="%(asctime)s %(message)s")
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

# App to view final product
browser = "brave"
win_browser = "C:/Program Files/Brave/Brave.exe"

# ffmpeg
if platform.system() == "Linux":
    ffmpegName = "ffmpeg"
elif platform.system() == "Windows":
    ffmpegName = r"ffmpeg"

# ffmpeg options
ffmpegOptions = []


# Define convert class
class convert():
    def __init__(self):
        pass

    # Define and get arguments.
    def getArgs(self):
        parser = argparse.ArgumentParser(description="Script to convert input video into gifs.")
        parser.add_argument("-i", "--input", help="Input video file. Ex: -i test.mp4")
        parser.add_argument("-o", "--output", help="Output gif. Ex: -o test.gif")
        parser.add_argument("-s", "--scale", help="Scale output of video. Ex: 360")
        parser.add_argument("-r", "--fps", help="Set Frames Per Second value. Ex: -r 10")
        parser.add_argument("--start", help="Start value for timestamps: Ex: --start '00:00:01'")
        parser.add_argument("--stop", help="stop value for timestamps. Ex: --stop '00:00:10'")

        get_args = parser.parse_args()
        inputArg = get_args.input
        outputArg = get_args.output
        scaleArg = get_args.scale
        fpsArg = get_args.fps
        startArg = get_args.start
        stopArg = get_args.stop

        # Parse args
        if inputArg:
            inputArg = inputArg
        else:
            inputArg = None

        if outputArg:
            outputArg = outputArg
        else:
            outputArg = None

        if scaleArg:
            scaleArg = scaleArg
        else:
            scaleArg = None

        if fpsArg:
            fpsArg = fpsArg
        else:
            fpsArg = None

        if startArg:
           startArg = startArg
        else:
           startArg = False

        if stopArg:
           stopArg = stopArg
        else:
           stopArg = False

        return {
                "inputArg": inputArg,
                "outputArg": outputArg,
                "scaleArg": scaleArg,
                "fpsArg": fpsArg,
                "startArg": startArg,
                "stopArg": stopArg
                }

    # Define run function
    def run(self, inputFile, outputFile, scaleArg, fpsArg, startArg, stopArg):
        # Test inputFile
        if not os.path.exists(inputFile):
            print(inputFile, "not found.")
            sys.exit(1)

        # inputFileExt = inputFile.split("\.")[-1]
        # outputFile = inputFile.replace(inputFileExt, ".gif")
        # print("outputFile: ", outputFile)

        # Get platform
        sys_platform = platform.system()

        try:
            # Convert input file to plette
            # ffmpeg -y -i file.mp4 -vf palettegen palette.png

            outputPaletteFile = "output.jpg"
            ffmpegOptions = ["-i", inputFile, "-vf", "palettegen", outputPaletteFile]

            ffmpegPaletteCommand = []
            ffmpegPaletteCommand.append(ffmpegName)
            ffmpegPaletteCommand.extend(ffmpegOptions)
            logging.debug("ffmpegPaletteCommand: %s", ffmpegPaletteCommand)

            try:
                runPalette = subprocess.run(ffmpegPaletteCommand)
            except subprocess.SubprocessError:
                print("Could not run ffmpegPaletteCommand.")
                sys.exit(1)

            # Die if return a non-zero returncode
            if runPalette.returncode > 0:
                print("Could not run ffmpeg.")
                sys.exit(1)

        except subprocess.CalledProcessError:
            print("Could not run: ", ffmpegPaletteCommand)
            sys.exit(1)

        try:
            # Convert input file with palette
            # ffmpeg -y -i file.mp4 -i palette.png -filter_complex paletteuse -r 10 -s 320x480 file.gif

            if not os.path.exists(outputPaletteFile):
                print(outputPaletteFile, "not found.")
                sys.exit(1)

            # ffmpegOptions = ["-i", inputFile, "-i", outputPaletteFile, "-filter_complex", "fps=" + str(fpsArg) + "," + str(scaleArg) + ":-2"]
            ffmpegOptions = ["-i", inputFile, "-i", outputPaletteFile]
            if scaleArg:
                ffmpegOptions.extend(["-vf", "scale="+str(scaleArg)+":-2"])

            if fpsArg:
                ffmpegOptions.extend(["-r", str(fpsArg)])

            ffmpegGifCommand = []
            ffmpegGifCommand.append(ffmpegName)
            ffmpegGifCommand.extend(ffmpegOptions)
            if outputFile:
                ffmpegGifCommand.append(outputFile)
            else:
                outputFile = inputFile + ".gif"
                ffmpegGifCommand.append(outputFile)
            logging.debug("ffmpegGifCommand: %s", ffmpegGifCommand)

            try:
                runGif = subprocess.run(ffmpegGifCommand)
            except subprocess.SubprocessError:
                print("Could not run ffmpegGifCommand.")
                sys.exit(1)

            # Die if return a non-zero returncode
            if runPalette.returncode > 0:
                print("Could not run ffmpeg.")
                sys.exit(1)

        except subprocess.CalledProcessError:
            print("Could not run: ", ffmpegGifCommand)
            sys.exit(1)

        # Size of files
        c.size(inputFile, sys_platform)
        c.size(outputFile, sys_platform)

        # Remove files
        c.remove(outputPaletteFile, sys_platform)

        # Preview files
        c.preview(outputFile, sys_platform)

    # Get file info
    def size(self, inputFile, platform):
        if not os.path.exists(inputFile):
            print(inputFile, "not found.")
            sys.exit(1)

        inputFileSize = os.path.getsize(inputFile)
        suffixes = ["B", "KB", "MB", "GB", "TB"]
        num = inputFileSize

        for x in suffixes:
            if num < 1024.0:
                print(inputFile, "is", round(num, 2), x)
                break
            num /= 1024.0


    # Preview output gif
    def preview(self, inputFile, sys_platform):
        if not inputFile:
            print(inputFile, "not found.")
            sys.exit(1)

        if sys_platform == "Linux":
            previewCommand = [browser, inputFile]
        elif sys_platform == "Windows":
            previewCommand = [r+win_browser, inputFile]

        try:
            runPreview = subprocess.run(previewCommand)
        except subprocess.CalledProcessError:
            print("Could not run: ", previewCommand)
            sys.exit(1)

    # Remove files
    def remove(self, inputFile, sys_platform):
        if not os.path.exists(inputFile):
            print("Could not find", inputFile)
            sys.exit(1)

        try:
            remove_input = input("Remove " + inputFile + " ?(y/n) ")

            if "y" in remove_input:
                print("Removing", inputFile)
                os.remove(inputFile)
            else:
                print("Not removing", inputFile)
        except:
            print("Could not remove ", inputFile)


# Define main objects
c = convert()

# Get arguments
inputArg = c.getArgs()["inputArg"]
outputArg = c.getArgs()["outputArg"]
scaleArg = c.getArgs()["scaleArg"]
fpsArg = c.getArgs()["fpsArg"]
startArg = c.getArgs()["startArg"]
stopArg = c.getArgs()["stopArg"]

# Debug
logging.debug("inputArg: %s", inputArg)
logging.debug("outputArg: %s", outputArg)
logging.debug("scaleArg: %s", scaleArg)
logging.debug("fpsArg: %s", fpsArg)
logging.debug("startArg: %s", startArg)
logging.debug("stopArg: %s", stopArg)

# Run conversion
c.run(inputArg, outputArg, scaleArg, fpsArg, startArg, stopArg)
