#!/usr/bin/python3

import os
import re
import subprocess as sp
import argparse as ap
import logging
from datetime import datetime
import shlex
import platform

# Set up logging
logging.basicConfig(format="%(asctime)s %(message)s")
# logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
# logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARN)

# Define platform
platform = platform.system()

if platform == "Linux":
    # Main player
    player = "mpv"
    playerOpts = []
elif platform == "Windows":
    # Main player for Windows
    player = r"C:\Program Files\VideoLan\VLC\vlc.exe"
    playerOpts = []

# Media allow
mediaExt = [".mp3", ".mp4", ".avi", ".mkv", ".webm"]

# Main list
info = []

# Define main class
class main():
    def __init__(self):
        pass

    def args(self):
        parser = ap.ArgumentParser(description="Simple script to play newest files in a directory.")
        parser.add_argument("-d", "--dir", help="Specifiy directory.")
        parser.add_argument("-l", "--limit", help="Number or 'all' to play everything.")
        parser.add_argument("-m", "--menu", action="store_true", help="Play with menu.")
        parser.add_argument("-a", "--auto", action="store_true", help="Auto play everything.")

        args = parser.parse_args()
        dirArg = args.dir
        limitArg = args.limit
        menuArg = args.menu
        autoArg = args.auto

        # parse flags.
        if dirArg is None:
            print("dir is not set.")
            exit(1)
        else:
            dirArg = dirArg

        # menuArg
        if menuArg:
            menuArg = True
        else:
            menuArg = False

        # autoArg
        if autoArg:
            autoArg = True
        else:
            autoArg = False

        # Limit - bug fiexed with limitArg not being declared an integer before properly handling what its output would be based on argument passed.
        if limitArg is None:
            limitArg = int(20)
        elif "all" in limitArg:
            limitArg = "all"
        else:
            limitArg = int(limitArg)

        return {
                "dirArg": dirArg,
                "limitArg": limitArg,
                "menuArg": menuArg,
                "autoArg": autoArg
                }

    # Cache files to info list and return
    def cache(self, dir):
        if dir is None:
            print("dir is not set.")
            exit(1)

        # if dir not found.
        if not os.path.exists(dir):
            print(dir, "not found.")
            exit(1)

        # cache_count = 0

        # Iterate and cache
        for root, dirs, files in os.walk(dir):
            # for d in dirs:
            #    print(d)

            # Iterate over files and match on extension
            for f in files:
                # Count and die on limit reached.
                # cache_count += 1
                # if cache_count >= limit:
                #    break

                for ext in mediaExt:
                    fPattern = ".*" + ext + "$"
                    fPatternCheck = re.search(fPattern, f, re.IGNORECASE)
                    if fPatternCheck:
                        # Full file
                        fullFile = os.path.join(root, f)

                        fullFileStat = os.stat(fullFile)
                        fullFileStatCtime = fullFileStat.st_ctime
                        fullFileStatMtime = fullFileStat.st_mtime

                        # Get file creation time.
                        # fileCtime = os.path.getctime(fullFile)
                        # fileCtimeHuman = datetime.fromtimestamp(fileCtime).strftime("%Y-%m-%d %H:%M:%S")

                        # Get file modification time.
                        # fileMtime = os.path.getmtime(fullFile)
                        # fileMtimeHuman = datetime.fromtimestamp(fileMtime).strftime("%Y-%m-%d %H:%M:%S")

                        try: 
                            # fullFile
                            # fileCtimeHuman
                            # fileMtimeHuman
                            # info.append([fullFile, fileCtimeHuman, fileMtimeHuman])

                            fullFile
                            fullFileStatCtime
                            fullFileStatMtime
                            info.append([fullFile, fullFileStatCtime, fullFileStatMtime])
                        except KeyError:
                            print("Could not get info on", fullFile)
                            continue

        # Return info list
        return info

    # Print out menu from info list.
    def menu(self, info, limit, platform):
        try:
            info
            limit
            platform
        except KeyError:
            print("info, limit or platform not set.")
            exit(1)

        # Debug
        logging.debug("info: %s", info)
        logging.debug("limit: %s", limit)
        logging.debug("platform: %s", limit)

        # sort by modification time
        info.sort(key=lambda x: x[2], reverse=True)

        # Set limit of items per page.
        if limit == "all":
            limit = len(info)
        pageLimit = limit
        pageList = []

        # Slice results into pages
        for i in range(0, len(info), pageLimit):
            pageList.append(info[i:i + pageLimit])

        pageTotal = len(pageList)
        pageCount = 1
        # pageTotal = len(pageList) - 1
        # pageCount = 0

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
                itemFile = item[0]
                itemTotal = len(pageList[pageCount-1])
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
                mainInputFile = pageList[pageCount-1][int(mainInput)-1][0]
                print("Selected", mainInputFile)

                try:
                    playCommand = []
                    playCommand.append(player)
                    playCommand.extend(playerOpts)
                    playCommand.append(mainInputFile)

                    logging.debug("playComand: %s", playCommand)

                    runPlay = sp.run(playCommand)
                except sp.CalledProcessError:
                    print("Could not run:", playCommand)
                    sys.exit(1)

            # Quit prompt
            elif "q" in mainInput:
                print("Quitting")
                break

            # Else
            else:
                print("Invalid input")


#         while True:
#             count = 0
#             infoTotal = len(info)
# 
#             for file, ctime, mtime in info:
#                 fileBase = file.split("/")[-1]
# 
#                 count += 1
# 
#                 # Adjust if limit a number or string.
#                 if isinstance(limit, int):
#                     if count > limit:
#                         break
# 
#                     print("[", count, "/", limit, "]", fileBase)
#                 else:
#                     print("[", count, "/", infoTotal, "]", fileBase)
# 
#             # Prompt user
#             infoInput = input("Enter Number: ")
# 
#             # Parse input and play
#             if infoInput.isdigit():
#                 logging.debug("infoInput: %s", infoInput)
#                 infoAnswerFile = info[int(infoInput)-1][0]
#                 print("Selected:", infoAnswerFile)
#                 logging.debug("infoAnswerFile: %s", infoAnswerFile)
# 
#                 try:
#                     playCommand = []
#                     playCommand.append(player)
#                     playCommand.extend(playerOpts)
#                     playCommand.append(infoAnswerFile)
# 
#                     logging.debug("playComand: %s", playCommand)
# 
#                     runPlay = sp.check_call(playCommand)
#                 except sp.CalledProcessError:
#                     print("Could not run:", playCommand)
#                     exit(1)
# 
#             # Quit
#             elif "q" in infoInput or "quit" in infoInput:
#                 break
#             else:
#                 print("Invalid input")

    # Autoplay everything in info list.
    def auto(self, info, limit, platform):
        try:
            info
            limit
            platform
        except KeyError:
            print("info, limit, platform not set.")
            exit(1)

        tempList = []
        count = 0

        logging.debug("info: %s", info)
        logging.debug("limit: %s", limit)

        # sort by modification time
        info.sort(key=lambda x: x[2], reverse=True)

        for file, ctime, mtime in info:
            count += 1

            # Adjust if limit a number or string.
            if isinstance(limit, int):
                if count > int(limit):
                    break

            tempList.append(file)

        try:
            print("Playing", len(tempList), "files.")
            # playString = shlex.split(player + " " + ' '.join(playerOpts) + ' '.join(tempList))
            # playRun = sp.call(playString)

            playAutoCommand = []
            playAutoCommand.append(player)
            playAutoCommand.extend(playerOpts)
            playAutoCommand.extend(tempList)

            logging.debug("playAutoCommand: %s", playAutoCommand)
            runPlayAuto = sp.check_call(playAutoCommand)
        except FileNotFoundError:
            print(player, "not found.")
            exit(1)
        except sp.CalledProcessError:
            print("Could not run.")
            exit(1)
        except ValueError:
            print("Not properly set.")
            exit(1)


# define main object
m = main()

# Get args
dirArg = m.args()["dirArg"]
limitArg = m.args()["limitArg"]
menuArg = m.args()["menuArg"]
autoArg = m.args()["autoArg"]

# Debug
logging.debug("dirArg: %s", dirArg)
logging.debug("limitArg: %s", limitArg)
logging.debug("menuArg: %s", menuArg)
logging.debug("autoArg: %s", autoArg)

# Cache
info = m.cache(dirArg)
logging.debug("info: %s", info)
logging.debug("limitArg: %s", limitArg)
logging.debug("platform: %s", limitArg)

# menu
if menuArg is True:
    m.menu(info, limitArg, platform)

# Auto
if autoArg is True:
    m.auto(info, limitArg, platform)
