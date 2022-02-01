#!/usr/bin/python3

import os
import subprocess
import argparse
import sys
import re
import logging
import psutil
import resource
import getpass

# Import multiprocessing libarary as mp
# import multiprocessing as mp

# Configure logging
#logging.basicConfig(format="%(asctime)s %(message)s")
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

# Create pool and size baised on number of physical cores.
# pool = mp.Pool(mp.cpu_count())

# Youtube-dl
current_user = getpass.getuser()
#ytdlFile = "/home/insight/.local/bin/youtube-dl"

#ytdlFile = "youtube-dl"

# Die if ytdlFile not found.
#if not os.path.exists(ytdlFile):
#    print("Could not find", ytdlFile)
#    sys.exit(1)

# Main archive file
#arcFileArg = "webarc_data.txt"

## Main list. -> directory1, [link1, link2, link3, link4]
mainList = []


# Main class
class main():
    def __init__(self):
        pass

    # Fetch arguments
    def getArgs(self):
        parser = argparse.ArgumentParser(description="Fetch items defined in mainList to archive and play back.")
        parser.add_argument("--cookies-file", help="Set cookies file to read from.")
        parser.add_argument("--arc-file", help="Set archive file to read from.")
        parser.add_argument("--download-menu", action="store_true", help="Enable menu instead of auto.")
        parser.add_argument("--download-auto", action="store_true", help="Auto download")
        parser.add_argument("--download-only", help="Download only item mentioned.")
        parser.add_argument("--encode-menu", action="store_true", help="Encode menu.")
        parser.add_argument("--encode-auto", action="store_true", help="Auto encode.")
        parser.add_argument("--encode-only", help="Encode only specified directory.")
        parser.add_argument("--quality", help="Set quality. Example: 360p")
        parser.add_argument("--max-quality", action="store_true", help="Set quality. Example: 360p")
        parser.add_argument("--rate", help="Download rate. Example: 3M")
        parser.add_argument("--max-download", help="Max number of videos to download for each entry. Example: 10")
        parser.add_argument("--crf", help="Apply crf limits to webarc.py")
        parser.add_argument("--nice", help="Apply nice limits to webarc.py. Default: 16")
        parser.add_argument("--core", help="Apply core limits to webarc.py, default: 1")

        args = parser.parse_args()
        cookiesFileArg = args.cookies_file
        arcFileArg = args.arc_file
        downloadMenuArg = args.download_menu
        downloadAutoArg = args.download_auto
        downloadOnlyArg = args.download_only
        encodeMenuArg = args.encode_menu
        encodeAutoArg = args.encode_auto
        encodeOnlyArg = args.encode_only
        qualityArg = args.quality
        maxQualityArg = args.max_quality
        rateArg = args.rate
        maxArg = args.max_download
        niceArg = args.nice
        #threadsArg = args.threads
        crfArg = args.crf
        coreArg = args.core

        # Iterate over items, default to None if nothing is set.
        for item in downloadMenuArg, downloadAutoArg, downloadOnlyArg, encodeMenuArg, encodeAutoArg, encodeOnlyArg, rateArg, maxArg, niceArg:
            try:
                item = item
            except KeyError:
                item = None
            except Exception as e:
                print(e)

        # Apply default values
        if cookiesFileArg:
            cookiesFileArg = cookiesFileArg
        else:
            cookiesFileArg = None

        if arcFileArg:
            arcFileArg = arcFileArg
        else:
            arcFileArg = "webarc.txt"

        #if threadsArg:
        #    threadsArg
        #else:
        #    threadsArg = 4

        if crfArg:
            crfArg
        else:
            crfArg = 30

        if coreArg:
            coreArg = coreArg
        else:
            coreArg = 1

        if qualityArg:
            qualityArg = qualityArg
        else:
            qualityArg = "best"
            #qualityArg = "bestvideo+bestaudio"

        if maxQualityArg:
            maxQualityArg = "bestvideo+bestaudio"
        else:
            maxQualityArg = None

        return {
                "cookiesFileArg": cookiesFileArg,
                "arcFileArg": arcFileArg,
                "downloadMenuArg": downloadMenuArg,
                "downloadAutoArg": downloadAutoArg,
                "downloadOnlyArg": downloadOnlyArg,
                "encodeMenuArg": encodeMenuArg,
                "encodeAutoArg": encodeAutoArg,
                "encodeOnlyArg": encodeOnlyArg,
                "qualityArg": qualityArg,
                "rateArg": rateArg,
                "maxArg": maxArg,
                "maxQualityArg": maxQualityArg,
                "niceArg": niceArg,
                #"threadsArg": threadsArg,
                "crfArg": crfArg,
                "coreArg": coreArg,
                }

    # check for directory and create if not found.
    def checkDir(self, dir, auto):
        if not os.path.exists(dir):
            print("Creating", dir)
            os.mkdir(dir)

    # Function to pass links and download through youtube-dl.
    #def download(self, dir, link, rateArg, maxArg):
    def download(self, dir, link, rateArg):
        if dir is None or link is None:
            print("Nothing passed for dir or link.")
            sys.exit(1)

        if not os.path.exists(dir):
            print(dir, "Not found.")
            sys.exit(1)

        # Enter directory
        print("Entering", dir)
        os.chdir(dir)

        # main file and arguments.
        ytdlCommand = []

        # Append main file, options, download speed and link to run as command
        # ytdlCommand.append("youtube-dl")
        ytdlCommand.append("yt-dlp")
        ytdlCommand.extend(ytdlOptions)

        # if maxArg is passed
        if maxArg:
            ytdlCommand.extend(["--max-downloads", str(maxArg)])

        # if rateArg is passed
        if rateArg:
            ytdlCommand.extend(["-r", rateArg])

        ytdlCommand.append(link)
        # ytdlCommand.extend([ytdlFile, ytdlOptions, "-r", rateArg, link])

        # output to user
        #print("Trying:", ytdlCommand)
        logging.debug("ytdlCommand: %s", ytdlCommand)

        try:
            ytdlFetch = subprocess.run(ytdlCommand, shell=False)
        except subprocess.CalledProcessError:
            # print("Could not run youtube-dl.")
            print("Could not run yt-dlp")
            sys.exit(1)
        except Exception as e:
            print(e)

    # Download
    def downloadMenu(self, mainList, rateArg):
        # Main counter
        # dirCount = 0

        # Die if list not set
        if mainList is None:
            print("mainList not set.")
            sys.exit(1)

        # Set limit of items per page.
        pageLimit = 20
        pageList = []

        # Slice results into pages
        for i in range(0, len(mainList), pageLimit):
            pageList.append(mainList[i:i + pageLimit])

        # pageTotal = len(pageList) - 1
        # pageCount = 0
        pageTotal = len(pageList)
        pageCount = 1

        # Loop prompt
        while True:
            # logging.debug("page: %s", page)
            logging.debug("pageCount: %s", pageCount)
            logging.debug("pageTotal: %s", pageTotal)

            print("Page", str(pageCount), "of", str(pageTotal))
            itemCount = 0

            # Print each item on page
            for item in pageList[pageCount-1]:
                itemCount += 1
                itemTotal = len(pageList[pageCount-1])
                itemFile = item[0]
                print("[", itemCount, "]", itemFile)

            # Input
            mainInput = input("(n/p) Enter Item Number: ")

            # Next page
            if "n" in mainInput:
                print("Next page.")
                if pageCount + 1 > pageTotal:
                    pageCount = pageCount
                else:
                    pageCount = pageCount + 1

            # Previous page
            elif "p" in mainInput:
                print("Previous page.")
                if pageCount - 1 < 0:
                    pageCount = pageCount
                else:
                    pageCount = pageCount - 1

            # Input number
            elif mainInput.isdigit() and int(mainInput) <= itemTotal:
                userDir = pageList[pageCount-1][int(mainInput)-1][0]
                userLinks = pageList[pageCount-1][int(mainInput)-1][1]

                print("Selected Dir", userDir)
                print("Selected Links", userLinks)

                logging.debug("userDir: %s", userDir)
                logging.debug("userLinks: %s", userLinks)

                # Check and create dir if not found.
                m.checkDir(userDir, False)

                linkCount = 0
                linkTotal = len(userLinks)

                # Download links
                for link in userLinks:
                    linkCount += 1
                    print("Link [", linkCount, "/", linkTotal, "]", userDir, link)
                    m.download(userDir, link, rateArg)

            # Quit prompt
            elif "q" in mainInput:
                print("Quitting")
                break

            # Else
            else:
                print("Invalid input")

#        while True:
#            print("Download Menu.")
#            dirCount = 0
#            dirTotal = len(mainList)
#
#            for item in mainList:
#                dir = item[0]
#                dirCount += 1
#                print("Dir [", dirCount, "/", dirTotal, "]", dir)
#            userInput = input("Enter Number: ")
#
#            # If input is valid
#            if userInput.isdigit() and int(userInput) <= dirTotal:
#                userDir = mainList[int(userInput)-1][0]
#                userLinks = mainList[int(userInput)-1][1]
#                print("Selected:", userDir)
#
#                # Check for the selected directory by full path, change to it or die
#                fullUserDir = userDir
#
#                # Check and create dir if not found.
#                m.checkDir(fullUserDir, False)
#
#                # Change to directory
#                #os.chdir(fullUserDir)
#
#                linkCount = 0
#                linkTotal = len(userLinks)
#
#                # Set max downloads (if passed)
#                #try:
#                #    maxArg = mainList[int(userInput)-1][2]
#                #except IndexError:
#                #    # print("maxArg not set.")
#                #    maxArg = None
                 #except Exception as e:
                 #   print(e)
#
#                # Download links
#                for link in userLinks:
#                    linkCount += 1
#                    print("Link [", linkCount, "/", linkTotal, "]", userDir, link)
#                    #m.download(userDir, link, rateArg, maxArg)
#                    m.download(userDir, link, rateArg)
#
#            # Quit
#            elif userInput == "q":
#                print("Quiting.")
#                break
#            else:
#                print("Invalid input.")

    def downloadAuto(self, mainList, onlyArg):
        logging.debug("mainList: %s\nonlyArg: %s", mainList, onlyArg)

        # if onlyArg is set. Match what can be read from mainList
        if onlyArg:
            for item in mainList:
                if onlyArg in item[0]:
                    onlyDir = item[0]
                    logging.debug("onlyDir: %s", onlyDir)
                    m.checkDir(onlyDir, True)

                    print("Entering", onlyDir)
                    os.chdir(onlyDir)

                    linkCount = 0
                    linkTotal = len(item[1])

                    #try: 
                    #    # Set max downloads
                    #    maxArg = item[2]
                    #except IndexError:
                    #    print("maxArg not set.")
                    #    maxArg = None

                    for itemLink in item[1]:
                        linkCount += 1
                        print("Link [", linkCount, "/", linkTotal, "]", itemLink)

                        # m.checkDir
                        m.download(onlyDir, itemLink, rateArg)
        # Download everything
        else:
            dirCount = 0
            # Loop through mainList
            for item in mainList:
                linksCount = 0

                # Define directory entry
                dir = item[0]
                dirTotal = len(item[0])
                dirCount += 1

                # Define links list to iterate through
                links = item[1]
                linksTotal = len(links)

                # Set max downloads
                #maxArg = item[2]

                # Define full path to enter and download playlist links
                dirFull = dir

                # Check for directory
                m.checkDir(dirFull, True)

                # Iterate through links
                for link in links:
                    linksCount += 1

                    # Enter directory
                    print("Dir [", dirCount, "/", dirTotal, "] Entering", dirFull)
                    os.chdir(dirFull)

                    # Fetch playlist
                    print("Link [", linksCount, "/", linksTotal, "] Fetching", link)
                    #m.download(dir, link, rateArg, maxArg)
                    m.download(dir, link, rateArg)

                # Close mp pool after fetching
                # pool.close()


# Define file class
class file():
    def __init__(self):
        pass

    # check webarc_data file, cache to mainList.
    def readFile(self, arcFileArg):
        if not os.path.exists(arcFileArg):
            print("Could not find", arcFileArg)
            sys.exit(1)

        # webarc format
        # <directory> | <link1> <link2> <link3> | <max_downloads>

        # Read file and parse lines to get main directory and links within.
        file_read = open(arcFileArg)
        for line in file_read:
            # linkCount = 0
            linkTempList = []

            # Ignore comments starting with #
            if line[0] == "#" or not line:
                # Debug
                # print("Ignoring line.")
                continue

            # Split lines up and clean out extra spaces and quotes in directory
            #mainDir = re.sub(" $", "", line.split("|")[0]).replace("\"", "")
            mainDir = re.sub(" $", "", line.split("|")[0])

            # debug
            # logging.debug("mainDir: %s", mainDir)

            # Debug
            # print("Directory:", mainDir)

            # Iterate over links and split up by spaces
            for link in line.split("|")[1].split(" "):
                if link != "":
                    # debug
                    # logging.debug("link: %s", link)

                    # Clean up links for parsing later on.
                    linkClean = link.replace("\n", "").replace("\"", "").replace(" ", "")
                    if linkClean:
                        # Debug
                        # logging.debug("linkClean: %s", linkClean)

                        # debug
                        # linkCount += 1
                        # print("Link [", linkCount, "]:", linkClean)
                        linkTempList.append(linkClean)

            mainList.append([mainDir, linkTempList])
            # Append if maxArg is set in config file
            #try:
            #    # Set max downloads per entry if found in file.
            #    maxArg = line.split("|")[2].replace("\n", "").replace("\"", "").replace(" ", "")
            #    if maxArg:
            #        # Debug
            #        # print("maxArg set to", maxArg)
            #
            #        # Append mainList
            #        mainList.append([mainDir, linkTempList, maxArg])
            #except IndexError:
            #    # Append mainList
            #    mainList.append([mainDir, linkTempList])
            #
            #    # Debug
            #    # print("Nothing set for maxArg")

        file_read.close()

        # Debug
        # print(mainList)
        return(mainList)


# Define encode class
class encode():
    def __init__(self):
        pass

    # Define pre-encoding limits
    def encodeLimits(self, niceArg, coreArg):
        try:
            niceArg
            coreArg
        except ValueError:
            print("Invalid number.")
            sys.exit(1)
        except NameError:
            print("Arguments not set for encoding limits.")
            sys.exit(1)

        # Get pid and set limits.
        pid = os.getpid()
        ps = psutil.Process(pid)
        ps.nice(int(niceArg))
        # resource.setrlimit(resource.RLIMIT_CPU, (int(coreArg), int(coreArg)))

    def encodeMenu(self, mainList):
        # Die if list not set
        if mainList is None:
            print("mainList not set.")
            sys.exit(1)

        # Main counter
        dirCount = 0

        while True:
            print("Encode Menu.")
            dirCount = 0
            dirTotal = len(mainList)

            for item in mainList:
                dir = item[0]
                dirCount += 1
                print("Dir [", dirCount, "/", dirTotal, "]", dir)
            userInput = input("Enter Number: ")

            # If input is valid
            if userInput.isdigit() and int(userInput) <= dirTotal:
                userDir = mainList[int(userInput)-1][0]
                print("Selected:", userDir)

                # encode selected directory
                e.encodeDir(userDir)

            # Quit
            elif userInput == "q":
                print("Quiting.")
                break
            else:
                print("Invalid input.")

    # Auto encode directories
    def encodeAuto(self, mainList, onlyArg):
        if mainList is None:
            print("Nothing passed for mainList")
            sys.exit(1)

        logging.debug("mainList: %s\nonlyArg: %s", mainList, onlyArg)

        # if onlyArg is set. Match what can be read from mainList
        if onlyArg:
            for item in mainList:
                if onlyArg in item[0]:
                    onlyDir = item[0]
                    logging.debug("onlyDir: %s", onlyDir)

                    e.encodeDir(onlyDir)
        else:
            dirCount = 0
            # Loop through mainList
            for item in mainList:
                dir = item[0]

                # Define directory entry
                dirCount += 1
                dirTotal = len(mainList[0])

                # Enter directory
                print("[", dirCount, "/", dirTotal, "] Encoding directory", dir)
                e.encodeDir(dir)

    # Encode single file
    def encodeFile(self, file):
        try:
            file
        except NameError:
            print("Nothing set for file.")
            sys.exist(1)
        except FileNotFoundError:
            print("Could not find", file)
            sys.exit(1)
        except Exception as e:
            print(e)

        # Set output pattern to be used for all encoded files
        # output_pattern = "-x265.mp4"
        output_pattern = "-x265.mkv"

        # Skip if output file already exists or pattern specified in main file
        file_output = file + output_pattern
        if os.path.exists(file_output) or output_pattern in file:
            print(file_output, "exists. Skipping.")
            return

        # ffmpeg options
        # crf = 30
        # threads = 4

        # nice -19 cpulimit -l 1200 --

        ffmpegCommand = []
        # ffmpegCommand.extend(["ffmpeg", "-i", file, "-c:v", "libx265", "-c:a", "libopus", "-c:s", "mov_text", "-crf", str(crfArg), "-threads", str(threadsArg)])
        ffmpegCommand.extend(["ffmpeg", "-i", file, "-c:v", "libx265", "-c:a", "libopus", "-c:s", "mov_text", "-crf", str(crfArg)])

        ffmpegCommand.append(file_output)

        # Debug
        logging.debug("ffmpegCommand: %s", ffmpegCommand)

        # Try and use ffmpeg to run and convert each file to specified ffmpeg options
        try:
            #runffmpegCommand = subprocess.run(ffmpegCommand)
            #runffmpegCommand = subprocess.run(ffmpegCommand, preexec_fn=e.encodeLimits(16))
            if niceArg:
                print("Running with nice arguments.")
                runffmpegCommand = subprocess.Popen(ffmpegCommand, preexec_fn=e.encodeLimits(niceArg, coreArg))
                runffmpegCommand.wait()
            else:
                runffmpegCommand = subprocess.Popen(ffmpegCommand)
                runffmpegCommand.wait()
        except subprocess.CalledProcessError:
            print("Could not run ffmpeg.")
            sys.exit(1)
        except Exception as e:
            print(e)

    # ffmpeg -i "${INPUT_FILE}" -c:v libx265 -c:a libopus -c:s mov_text -crf "${CRF}" -threads "${THREADS}" -ss "${START}" -to "${STOP}" "${OUTPUT_FILE}"
    # Iterate over directory and convert files.
    def encodeDir(self, dir):
        fileList = []
        dirList = []
        print("dir:", dir)

        # Test directory
        try:
            dir
        except FileNotFoundError:
            print(dir, "not found.")
            sys.exit(1)
        except Exception as e:
            print(e)

        for (root, dirs, files) in os.walk(dir):
            for d in dirs:
                dirFull = os.path.join(root, d)
                dirList.append(dirFull)

            for f in files:
                fileFull = os.path.join(root, f)
                fileList.append(fileFull)

        # iterate over files
        fileListCount = 0
        fileListTotal = len(fileList)

        # dirListCount = 0
        # dirListTotal = len(dirList)

        # Iterate over files and run if output file is not found.
        for file in fileList:
            fileListCount += 1
            print("[", fileListCount, "/", fileListTotal, "]", file)

            # Encode file
            e.encodeFile(file)


# Define main classes for each section
m = main()
e = encode()
f = file()

# Fetch (menu) arguments
cookiesFileArg = m.getArgs()["cookiesFileArg"]
arcFileArg = m.getArgs()["arcFileArg"]
downloadMenuArg = m.getArgs()["downloadMenuArg"]
downloadAutoArg = m.getArgs()["downloadAutoArg"]
downloadOnlyArg = m.getArgs()["downloadOnlyArg"]
encodeMenuArg = m.getArgs()["encodeMenuArg"]
encodeAutoArg = m.getArgs()["encodeAutoArg"]
encodeOnlyArg = m.getArgs()["encodeOnlyArg"]
qualityArg = m.getArgs()["qualityArg"]
rateArg = m.getArgs()["rateArg"]
maxArg = m.getArgs()["maxArg"]
maxQualityArg = m.getArgs()["maxQualityArg"]
niceArg = m.getArgs()["niceArg"]
#threadsArg = m.getArgs()["threadsArg"]
crfArg = m.getArgs()["crfArg"]
coreArg = m.getArgs()["coreArg"]

# Read file
mainList = f.readFile(arcFileArg)

# Debug
logging.debug("cookiesFileArg: %s", cookiesFileArg)
logging.debug("arcFileArg: %s", arcFileArg)
logging.debug("downloadMenuArg: %s", downloadMenuArg)
logging.debug("downloadAutoArg: %s", downloadAutoArg)
logging.debug("downloadOnlyArg: %s", downloadOnlyArg)
logging.debug("encodeMenuArg: %s", encodeMenuArg)
logging.debug("encodeAutoArg: %s", encodeAutoArg)
logging.debug("encodeOnlyArg: %s", encodeOnlyArg)
logging.debug("qualityArg: %s", qualityArg)
logging.debug("rateArg: %s", rateArg)
logging.debug("maxArg: %s", maxArg)
logging.debug("maxQualityArg: %s", maxQualityArg)
logging.debug("niceArg: %s", niceArg)
logging.debug("crfArg: %s", crfArg)
logging.debug("coreArg: %s", coreArg)
#logging.debug("ThreadsArg: %s", threadsArg)

# Options for youtube-dl
# ytdlOptions = ["-i", "--cookies", cookiesFileArg, "-f", qualityArg, "--external-downloader", "aria2c", "--prefer-ffmpeg", "--sub-format", "best",  "--sub-lang=en", "--write-sub", "--write-auto-sub", "--embed-subs", "--merge-output-format", "mkv", "--download-archive", "progress.txt", "--continue", "--no-overwrites", "-o", "%(uploader)s - %(title)s-%(id)s.%(ext)s"]

# If max quality argument is passed, then adjust quality to bestvideo+bestaudio
if maxQualityArg:
    qualityArg = maxQualityArg

ytdlOptions = ["-i", "-f", qualityArg, "--external-downloader", "aria2c", "--prefer-ffmpeg", "--sub-format", "best",  "--sub-lang=en", "--write-sub", "--write-auto-sub", "--embed-subs", "--merge-output-format", "mkv", "--download-archive", "progress.txt", "--continue", "--no-overwrites", "-o", "%(uploader)s - %(title)s-%(id)s.%(ext)s"]

# Argument is true, pass related function
if downloadMenuArg:
    m.downloadMenu(mainList, rateArg)

if downloadAutoArg:
    m.downloadAuto(mainList, None)

if downloadOnlyArg:
    m.downloadAuto(mainList, downloadOnlyArg)

if encodeMenuArg:
    e.encodeMenu(mainList)

if encodeAutoArg:
    e.encodeAuto(mainList, None)

if encodeOnlyArg:
    e.encodeAuto(mainList, encodeOnlyArg)
