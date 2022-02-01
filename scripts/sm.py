#!/usr/bin/env python3

import os
import argparse
import subprocess
# import shlex
# import getpass
# import pdb
# import operator
# import time
import time
import datetime
import re
from datetime import datetime
from operator import itemgetter, attrgetter, methodcaller
# import multiprocessing as mp
from colorama import init
from colorama import Fore, Back, Style
import logging
import platform
import sys

# Init color
init()

# Set logging.
# CRITICAL 50
# ERROR 40
# WARNING 30
# INFO 20
# DEBUG 10
# NOTSET 0

# logging.basicConfig(format="%(levelname)s - %(name)s - %(message)s", level=logging.DEBUG)
logging.basicConfig(format="%(levelname)s - %(name)s - %(message)s")

# logging.warning("%s event didn't happen.", "Time")
# logging.debug("Item: %s", item)

# Create pool
# processors = mp.cpu_count()
# pool = mp.Pool(processors)

# Define main directories to be looked at
dirList = ["/mnt/nas/web", "/mnt/nas/movies", "/mnt/nas/music", "/mnt/data/files/archive/web", "/mnt/data/files/media"]

# Main file that will be looked for search results if enabled through \
# arguments.
#dbFile = os.path.join("/home", getpass.getuser(), ".sm_db")
dbFile = ".sm_db"

# Main extensions of files to be looked for#.
fileExtList = [".webm", ".mp3", ".mp4", ".mkv", ".avi", ".wav", ".aiff", ".opus", ".ogg", ".m4a", ".flac"]

# Main list that will be used later for positive results.
# [ [File, Modification time], [File, Modification Time] ]
# resultDict = {}
resultList = []

# Main file to use
player = "mpv"

# Array of options for player to be loaded once playing the found results.
playerOptions = ["--pause", "--no-audio-display", "--force-seekable=yes", "--screenshot-format=png"]

# Check platform, change player based on OS
#if platform.system() == "Linux":
    # Main file to use
    #player = "mpv"

    # Array of options for player to be loaded once playing the found results.
    #playerOptions = ["--pause", "--no-audio-display", "--force-seekable=yes", "--screenshot-format=png"]
#elif platform.system() == "Windows":
    # Main file to use
    #player = "C:\Program Files\VideoLan\VLC\vlc.exe"
    #player = "vlc.exe"

    # Array of options for player to be loaded once playing the found results.
    #playerOptions = []
#elif platform.system() == "Mac":
    # Main file to use
    #player = "C:\Program Files\VideoLan\VLC\vlc.exe"
    #player = "vlc.exe"

    # Array of options for player to be loaded once playing the found results.
    #playerOptions = []
#else:
    #print("Invalid system profile.")
    #sys.exit(1)

# Main class to read and write to and from dbFile
class db():
    def __init__(self):
        pass

    # Main function to write
    def read(self, searchQuery, dirList, dbFile, dbUpdateArg, modArg):

        if not os.path.exists(dbFile):
            print(dbFile, "not found.")
            sys.exit(1)

        # If the DB file exists and yes is passed to its argument.
        # open dbFile as read mode and read line by line
        readFile = open(dbFile, "r")
        readLineCount = 0

        for line in readFile:
            readLineCount = readLineCount + 1

            # Search by entire query than incomplete
            linePattern = "^.*" + ''.join(searchQuery) + ".*$"
            lineMatch = re.search(linePattern, line, re.IGNORECASE)

            if lineMatch:
                # Strip out newline on the end of each line to \
                #    properly parse later on
                lineParse = line.replace("\n", "")

                # Now test each file that it matches up with \
                if os.path.isfile(lineParse):
                    lineParseName, lineParseExt = \
                        os.path.splitext(lineParse)

                    if lineParseExt in fileExtList:
                        # Get the modification time of item.
                        # lineParseModTime = os.path.getmtime(lineParse)
                        # lineParseCreateTime = os.path.getctime(lineParse)
                        # lineParseModHuman = datetime.fromtimestamp(lineParseModTime).strftime("%Y-%m-%d %H:%M:%S")
                        # lineParseCreateHuman = datetime.fromtimestamp(lineParseCreateTime).strftime("%Y-%m-%d %H:%M:%S")

                        # Append to resultList
                        # resultList.append([lineParse, lineParseModHuman, lineParseCreateHuman])
                        # logging.debug("lineParse: %s, lineParseModHuman: %s, lineParseCreateHuman: %s", lineParse, lineParseModHuman, lineParseCreateHuman)

                        lineParseStat = os.stat(lineParse)
                        lineParseStatMtime = lineParseStat.st_mtime
                        lineParseStatCtime = lineParseStat.st_ctime

                        resultList.append([lineParse, lineParseStatMtime, lineParseStatCtime])

                elif os.path.isdir(lineParse):
                    # Get the modification time of item.
                    # lineParseModTime = os.path.getmtime(lineParse)
                    # lineParseModHuman = datetime.fromtimestamp(lineParseModTime).strftime("%Y-%m-%d %H:%M:%S")

                    # Append results
                    # resultList.append([lineParse, lineParseModHuman])
                    # logging.debug("lineParse: %s, lineParseModHuman: %s", lineParse, lineParseModHuman)

                    lineParseStat = os.stat(lineParse)
                    lineParseStatMtime = lineParseStat.st_mtime
                    lineParseStatCtime = lineParseStat.st_ctime

                    resultList.append([lineParse, lineParseStatMtime, lineParseStatCtime])

        # close readFile
        readFile.close()

    def write(self, searchQuery, dirList, dbFile, dbUpdteArg, modArg):
        # if not os.path.exists(dbFile):
        #    print(dbFile, "not found.")
        #     sys.exit(1)

        writeFile = open(dbFile, "w")
        writeLineCount = 0

        # Cache files and folders to dbFile
        for dir in dirList:
            if not os.path.exists(dir):
                # print(dir, "not found.")
                # logging.warn("%s not found.", d)
                continue

            for (root, dirs, files) in os.walk(dir):
                # Cache directories
                for d in dirs:
                    dirFullPath = os.path.join(root, d)
                    writeLineCount = writeLineCount + 1

                    dirWriteString = dirFullPath + "\n"
                    dirWriteStringEncode = dirWriteString.encode('utf-8', 'ignore').decode('utf-8')
                    writeFile.write(dirWriteStringEncode)

                # Cache filenames
                for f in files:
                    fileFullPath = os.path.join(root, f)
                    fileName, fileExt = os.path.splitext(f)
                    fileWriteString = fileFullPath + "\n"
                    fileWriteStringEncode = fileWriteString.encode('utf-8', 'ignore').decode('utf-8')

                    if fileExt in fileExtList:
                        writeLineCount = writeLineCount + 1

                    # Write decoded file to file.
                    writeFile.write(fileWriteStringEncode)

        writeFile.close()

        logging.debug("%s lines written to %s", writeLineCount, dbFile)


# Define cache() class
class cache():
    def __init__(self):
        pass

    # Pass dirList to getArgs or it won't reference correctly down the line.
    def getArgs(self):
        parser = argparse.ArgumentParser(description="Pass arguments to search \
    media program.")
        parser.add_argument("-a", "--auto", action="store_true", help="Enable auto \
    play everything found in the script.")
        parser.add_argument("-u", "--update", action="store_true", help="Update \
    dbFile if enabled.")
        parser.add_argument("-f", "--file", help="Custom dbFile.")
        parser.add_argument("--list", action="store_true", help="List files \
    found in path.")
        parser.add_argument("--limit", help="Set page limit. Default 20")
        parser.add_argument("-m", "--modify", action="store_true", help="Sort \
    results by modifcation date.")
        parser.add_argument("-b", "--backwards", action="store_true", help="\
    Reverse sort results by modification date.")
        parser.add_argument("-r", "--repeat", help="Loop through on choice with \
    prompt.")
        parser.add_argument("-v", "--verbose", action="store_true", help="Verbos \
    mode.")
        parser.add_argument("query", nargs="+", help="Search query")

        # Now just sm <query> to be simplier.

        # define global arguments to be made.
        # Define the array to be sorted through as a global,
        # to be redfined and able to be referenced later.
        # global autoPlay, queryArg, dirArg, dirList, , dbUpdateArg

        # Add argument for the program to be added.
        args = parser.parse_args()
        queryArg = args.query
        autoArg = args.auto
        dbUpdateArg = args.update
        modArg = args.modify
        pageLimitArg = args.limit
        modArgReverse = args.backwards
        dbCustomFile = args.file
        listArg = args.list
        repeatArg = args.repeat

        if listArg:
            listArg = True
        else:
            listArg = False

        if repeatArg:
            repeatArg = repeatArg
        else:
            repeatArg = 0

        # Test if custom db file is used.
        if dbCustomFile:
            dbMainFile = dbCustomFile
        else:
            dbMainFile = dbFile

        # Parse modify argument.
        # If true, then sort in order, if reverse is passed, then sort in reverse.
        #    Else, then just present by order of finding them.
        if modArg:
            modArg = "order"
        elif modArgReverse:
            modArg = "reverse"
        else:
            modArg = False

        # Check for update database argument.
        if dbUpdateArg:
            dbUpdateArg = True
        else:
            dbUpdateArg = False

        # If autoArg is yes, then define the global to be set for yes for later on.
        if autoArg:
            autoPlay = True
        else:
            autoPlay = False

        if pageLimitArg:
            pageLimitArg = pageLimitArg
        else:
            pageLimitArg = 20

        # if quryArg is empty, the kill the script for it has nothing to search for
        if not queryArg:
            # print(Fore.RED + "Search query is empty. Must enter something.")
            print("Search query is empty. Must enter something.")
            logging.error("Search query is empty.")
            sys.exit(1)

        # Return back our arguments.
        return {
                "queryArg": queryArg,
                "autoPlay": autoPlay,
                "dbUpdateArg": dbUpdateArg,
                "dbMainFile": dbMainFile,
                "modArg": modArg,
                "pageLimitArg": pageLimitArg,
                "modArgReverse": modArgReverse,
                "listArg": listArg,
                "repeatArg": repeatArg
                }

    # Main function to search through, now will handle dbFile for precached
    # folders and files.
    def search_old(self, searchQuery, dirList, dbFile, dbUpdateArg):
        # If the DB file exists, rewrite it.
        # BUG: dbFile and directory arguments will mismatch and will be overridden
        # by the ~/.sm_db file

        if not os.path.exists(dbFile):
            d.write(searchQuery, dirList, dbFile, dbUpdateArg,
                    modArg)

        # If the DB file doesn't exist, create a new one and write
        # cached media to it.
        if dbUpdateArg:
            d.read(searchQuery, dirList, dbFile, dbUpdateArg,
                   modArg)

        # Cache media manually if db file isn't called for
        else:
            # Bug with seperate results to database.
            for dir in dirList:
                if not os.path.exists(dir):
                    # print(dir, "not found.")
                    # logging.warn("%s not found.", d)
                    continue

                # Check to make sure the directory exists to be used.
                for (root, dirs, files) in os.walk(dir):
                    # Look through directories to find matching results
                    for d in dirs:
                        dirFullPath = os.path.join(root, d)
                        # dirFullModTime = os.path.getmtime(dirFullPath)
                        # dirFullModHuman = datetime.fromtimestamp(dirFullModTime).strftime("%Y-%m-%d %H:%M:%S")
                        # dirFullCreateTime = os.path.getctime(dirFullPath)
                        # dirFullCreateHuman = datetime.fromtimestamp(dirFullCreateTime).strftime("%Y-%m-%d %H:%M:%S")
                        dirFullStat = os.stat(dirFullPath)
                        dirFullStatMtime = dirFullStat.st_mtime
                        dirFullStatCtime = dirFullStat.st_ctime

                        resultList.append([dirFullPath, dirFullStatMtime, dirFullStatCtime])

                        # Match searchQuery to dirFullPath and
                        # cache the result into resultList array.
                        for s in searchQuery:
                            # Match dictionary results
                            dirPattern = "^.*" + s + ".*$"
                            dirPatternMatch = re.\
                                search(dirPattern, dirFullPath, re.IGNORECASE)

                            if dirPatternMatch:
                                # resultList.append([dirFullPath, dirFullModHuman, dirFullCreateHuman])
                                resultList.append([dirFullPath, dirFullStatMtime, dirFullStatCtime])
                                # logging.debug("dirFullPath: %s\ndirFullModHuman: %s\ndirFullCreateHuman: %s", dirFullPath, dirFullModHuman, dirFullCreateHuman)

                    # Loop through files to find matching results
                    for f in files:
                        # Join root and f variables to define the full path for
                        # files that os.walks shows.
                        fileFullPath = os.path.join(root, f)
                        # fileFullModTime = os.path.getmtime(fileFullPath)
                        # fileFullModHuman = datetime.fromtimestamp(fileFullModTime).strftime("%Y-%m-%d %H:%M:%S")
                        # fileFullCreateTime = os.path.getctime(fileFullPath)
                        # fileFullCreateHuman = datetime.fromtimestamp(fileFullCreateTime).strftime("%Y-%m-%d %H:%M:%S")

                        fileFullStat = os.stat(fileFullPath)
                        fileFullStatMtime = fileFullStat.st_mtime
                        fileFullStatCtime = fileFullStat.st_ctime
                        fileName, fileExt = os.path.splitext(fileFullPath)

                        # Now compare the extension of the filetype to a list
                        # of what to find, before storing the results.
                        for s in searchQuery:
                            # Add in support for term1+term2
                            # import re
                            filePattern = "^.*" + s + ".*$"
                            filePatternMatch = re.\
                                search(filePattern, fileFullPath,
                                       re.IGNORECASE)

                            # Match file results
                            if filePatternMatch and fileExt in fileExtList:
                                resultList.append([fileFullPath, fileFullStatMtime, fileFullStatCtime])
                                # resultList.append([fileFullPath, fileFullModHuman, fileFullCreateHuman])
                                # logging.debug("fileFullPath: %s\nfileFullModHuman: %s\nfileFullCreateHuman: %s", fileFullPath, fileFullModHuman, fileFullCreateHuman)

        # Return array after results are found and parsed.
        return(resultList)

    # Main function to search through, now will handle dbFile for precached
    # folders and files.

    def search(self, searchQuery, dirList, dbFile, dbUpdateArg):
        # If the DB file exists, rewrite it.
        # BUG: dbFile and directory arguments will mismatch and will be overridden
        # by the ~/.sm_db file

        # Define our main object to refer to db class
        d = db()

        if not os.path.exists(dbFile):
            d.write(searchQuery, dirList, dbFile, dbUpdateArg,
                    modArg)

        # If the DB file doesn't exist, create a new one and write
        # cached media to it.
        if dbUpdateArg:
            d.read(searchQuery, dirList, dbFile, dbUpdateArg, modArg)
        else:
            d.read(searchQuery, dirList, dbFile, dbUpdateArg, modArg)

        # Return array after results are found and parsed.
        return(resultList)


# Define play class
class play():
    def __init__(self):
        pass

    # Simple function to spit out results of resultList
    def list(self, resultList):
        start = 0
        resultLength = len(resultList)

        print(str(resultLength) + " matches.")
        for line in resultList:
            start += 1
            # print(Fore.GREEN + "[" + start + Fore.GREEN + "/" + resultLength + Fore.GREEN + "]" + line[0] + Style.RESET_ALL)
            print("[", str(start), "/", str(resultLength), "]", line[0])

    # Play item
    def item(self, item):
        # If platform is Linux
        logging.debug("platform.system(): %s", platform.system())
        logging.debug("item: %s", item)

        # Print info on file
        # print("stats:", os.path.stat(item))

        try:
            item
        except KeyError:
            print("item not defined.")
            sys.exit(1)

        if platform.system() == "Linux":
            # Marge results array into single string.
            # fileList = " ".join('"{0}"'.format(f) for f in resultList[0])

            # Combine the file, options and list into one single string then
            # properly parse it with shlex.split
            playerCommand = []
            playerCommand.append(player)
            playerCommand.extend(playerOptions)

            # item_length = len(item)
            # print(Fore.GREEN + "Playing " + str(item_length) + Fore.GREEN + " Items." + Style.RESET_ALL)
            # print("Playing " + str(item_length) + " Items.")

            # Test item
            if isinstance(item, str):
                playerCommand.append(item)
            elif isinstance(item, list):
                playerCommand.extend(item)

            logging.debug("playerCommand: %s", playerCommand)

            try:
                subprocess.run(playerCommand, shell=False)
            except subprocess.CalledProcessError:
                # print(Fore.RED + "Could not run ", playerCommand)
                print("Could not run ", playerCommand)

        # If platform is Windows
        elif platform.system() == "Windows":
            # importing vlc module
            # import vlc

            # creating vlc media player object
            # media = vlc.MediaPlayer("1.mp4")

            # start playing video
            # media.play()

            # import vlc
            # media = vlc.MediaPlayer(item)
            # media.play()

            playerCommand = []
            playerCommand.append(r'C:\Program Files\VideoLAN\VLC\vlc.exe')

            # Test item
            if isinstance(item, str):
                playerCommand.append(item)
            elif isinstance(item, list):
                playerCommand.extend(item)

            logging.debug("playerCommand: %s", playerCommand)

            try:
                subprocess.run(playerCommand, shell=False)
            except subprocess.CalledProcessError:
                print("Could not run ", playerCommand)

    # Prompt if results are greater than 0 and loop through results
    def prompt(self, resultList, modArg, pageLimit):
        resultTotal = len(resultList)
        resultCount = 0

        try:
            resultList
            modArg
            pageLimit
        except NameError:
            print("Prompt arguments not defined.")
            sys.exit(1)


        # File, Modification Date - Sort results by modification date
        # True: Standard order, Reverse: Then flip the \
        # results by modification date.
        if modArg == "order":
            # print(Fore.WHITE + "Sorting by modification date.")
            print("Sorting by modification date.")
            resultCount = 0
            # resultList.sort(key=lambda x: datetime.strptime(x[1], \
            # "%Y-%m-%d %H:%M:%S")[0:6])
            resultList.sort(key=lambda x: x[1], reverse=False)

        elif modArg == "reverse":
            # print(Fore.WHITE + "Sorting by resverse modification date.")
            print("Sorting by resverse modification date.")
            resultList.sort(key=lambda x: x[1], reverse=True)

        if resultTotal > 0:
            print(str(resultTotal) + " matches.")

            # Set limit of items per page.
            # pageLimit = 20
            pageList = []

            # Slice results into pages
            for i in range(0, len(resultList), int(pageLimit)):
                pageList.append(resultList[i:i + int(pageLimit)])

            # pageTotal = len(pageList) -1
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
                    p.item(mainInputFile)

                # Quit prompt
                elif "q" in mainInput:
                    print("Quitting")
                    break

                # Else
                else:
                    print("Invalid input")

    # needs to be updated for resultList being multi-dim (file, mdate, cdate)
    def auto(self, resultList, modArg):
        resultTotal = len(resultList)
        fileList = []

        # Parse out files to main fileList, then append to single string to be played back as a command.
        for item in resultList:
            mfile = item[0]
            mdate = item[1]

            fileList.append(mfile)
            logging.debug("mfile: %s", mfile)

        if modArg == "order":
            print("Sorting by modification date.")
            # resultCount = 0
            # resultList.sort(key=lambda x: datetime.strptime(x[1], "%Y-%m-%d %H:%\
            # M:%S")[0:6])
            fileList.sort(key=lambda x: x[1], reverse=False)
        elif modArg == "reverse":
            # print(Fore.GREEN + "Sorting by resverse modification date.")
            print("Sorting by resverse modification date.")
            fileList.sort(key=lambda x: x[1], reverse=True)
        else:
            pass

        if resultTotal > 0:
            p.item(fileList)

        else:
            # print(Fore.RED + "No files could be found.")
            print("No files could be found.")


# Cache object
c = cache()

# Define our play object for subclass
p = play()

# define database object
d = db()

# Collect arguments.
queryArg = c.getArgs()["queryArg"]
autoPlay = c.getArgs()["autoPlay"]
dbUpdateArg = c.getArgs()["dbUpdateArg"]
dbFile = c.getArgs()["dbMainFile"]
modArg = c.getArgs()["modArg"]
pageLimitArg = c.getArgs()["pageLimitArg"]
listArg = c.getArgs()["listArg"]
repeatArg = c.getArgs()["repeatArg"]
queryArg = c.getArgs()["queryArg"]

# Debug arguments
logging.debug("queryArg: %s", queryArg)
logging.debug("autoPlay: %s", autoPlay)
logging.debug("dbUpdateArg: %s", dbUpdateArg)
logging.debug("dbFile: %s", dbFile)
logging.debug("modArg: %s", modArg)
logging.debug("pageLimitArg: %s", pageLimitArg)
logging.debug("listArg: %s", listArg)
logging.debug("repeatArg: %s", repeatArg)

# If dbFile is not found, create
if not os.path.exists(dbFile):
    d.write(queryArg, dirList, dbFile, dbUpdateArg, modArg)

# if passed, update from it.
if dbUpdateArg:
    d.write(queryArg, dirList, dbFile, dbUpdateArg, modArg)
    d.read(queryArg, dirList, dbFile, dbUpdateArg, modArg)
else:
    # Read from dbFile
    d.read(queryArg, dirList, dbFile, dbUpdateArg, modArg)

# If repeatArt is passed, append to options
if int(repeatArg) > 0:
    playerOptions.append("-loop-playlist="+repeatArg)
    logging.debug("playerOptions: %s", playerOptions)

# list out files found by searchFiles function, if not then just regular prompt
if listArg:
    p.list(resultList)
    sys.exit(0)

# If autoPlay is set, then play everything. If not, play with prompt.
if autoPlay:
    p.auto(resultList, modArg)
else:
    p.prompt(resultList, modArg, pageLimitArg)

# Close pool for threading
# pool.close()
