#!/usr/bin/python3

import os
import subprocess
import sys
import time
import argparse
import logging
import random

# Configure logging
# logging.basicConfig(format="%(asctime)s %(message)s")
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

# Set main variables
# wallDir = "/mnt/data/files/media/wallpapers"
wallDir = "/home/insight/data/media/wallpapers"
wallList = []
wallLimit = 20

# Set command to run through feh.
# fehCommand = ["feh"]
# fehOptions = []

# define main class
class main():
    def __init__(self):
        pass

    # Get arguments
    def getArgs(self):
        parser = argparse.ArgumentParser(description="Script to show and manage wallpapers.")
        parser.add_argument("--menu", action="store_true", help="Display menu.")
        parser.add_argument("--auto", action="store_true", help="Display automatically.")
        parser.add_argument("--all", action="store_true", help="Display all")
        parser.add_argument("--random", action="store_true", help="Display random wallpaper")
        parser.add_argument("--search", help="Search wallpapers")

        args = parser.parse_args()
        menuArg = args.menu
        autoArg = args.auto
        allArg = args.all
        randomArg = args.random
        searchArg = args.search

        for item in menuArg, autoArg, allArg, randomArg, searchArg:
            try:
                item
            except NameError:
                item = None

        return {
                "menuArg": menuArg,
                "autoArg": autoArg,
                "allArg": allArg,
                "randomArg": randomArg,
                "searchArg": searchArg
                }

    # Cache files
    def cache(self, wallDir):
        try:
            wallDir
        except NameError:
            print("wallDir not found.")
            sys.exit(1)

        if not os.path.exists(wallDir):
            print(wallDir, "not found.")
            sys.exit(1)

        for (root, dirs, files) in os.walk(wallDir):
            for d in dirs:
                dFull = os.path.join(root, d)

            for f in files:
                fFull = os.path.join(root, f)
                fFullMTime = os.stat(fFull).st_mtime
                fFullCTime = os.stat(fFull).st_ctime
                # fFullSize = os.stat(fFull).st_size

                wallList.append([fFull, fFullMTime, fFullCTime])

        wallListTotal = len(wallList)
        print(wallListTotal, "files cached.")

        return(wallList)

    # Auto show everything.
    def auto(self, wallList):
        try:
            wallList
        except NameError:
            print("wallList not set.")
            sys.exit(1)

        wallCount = 0
        wallListTotal = len(wallList)

        for item in wallList:
            wallCount += 1
            itemFile = item[0]
            itemCTime = item[1]
            itemMTime = item[2]

            print("[", wallCount, "/", wallListTotal, "]", itemFile)
            try:
                showCommand = ["feh"]
                showCommandOpts = ["--bg-scale"]
                showCommand.extend(showCommandOpts)
                showCommand.append(itemFile)

                subprocess.run(showCommand, shell=False)
            except subprocess.CalledProcessError:
                print("Could not run command.")
                sys.exit(1)

            time.sleep(1)

    # Show all
    def all(self, wallList):
        try:
            wallList
        except NameError:
            print("wallList not set.")
            sys.exit(1)

        try:
            tempList = [item[0] for item in wallList]
            tempListTotal = len(tempList)
            print("Show", tempListTotal, "files.")
            runCommand = ["feh"]
            runCommand.extend(tempList)
            subprocess.run(runCommand)

        except subprocess.CalledProcessError:
            print("Could not run command.")
            sys.exit(1)

    # Define menu
    def menu(self, wallList):
        try:
            wallList
        except NameError:
            print("wallList not set.")
            sys.exit(1)
        wallCount = 0
        wallListTotal = len(wallList)

        # for item in wallList:
        while True:
            # wallCount += 1
            wallItem = wallList[wallCount-1]
            itemFile = wallItem[0]
            itemMTime = wallItem[1]
            itemCTime = wallItem[2]

            print("[", wallCount, "/", wallListTotal, "]", itemFile)

            try:
                showCommand = ["feh"]
                showCommandOpts = ["--bg-scale"]
                showCommand.extend(showCommandOpts)
                showCommand.append(itemFile)

                subprocess.run(showCommand, shell=False)
            except subprocess.CalledProcessError:
                print("Could not run feh.")
                sys.exit(1)

            wallInput = input("(n/p) Enter command: ")
            # Next wallpaper
            if "n" in wallInput:
                wallCount += 1

            # previous wallpaper
            elif "p" in wallInput:
                wallCount = wallCount - 1

            # Quit menu
            elif "q" in wallInput:
                print("Quitting.")
                sys.exit(1)

            # Invalid input
            else:
                print("Invalid input.")

    # Search cached files and display using menu function.
    def search(self, wallList, searchArg):
        try:
            searchArg
            wallList
        except NameError:
            print("wallList or searchArg not set.")
            sys.exit(1)

        tempList = []
        for item in wallList:
            if searchArg in item[0]:
                tempList.append(item)

        tempListTotal = len(tempList)
        print(tempListTotal, "matches")

        if tempListTotal == 0:
            print("No results found.")
            sys.exit(1)

        # Call menu
        if menuArg:
            m.menu(tempList)

        # Auto
        if autoArg:
            m.auto(tempList)


# Define item
m = main()
wallList = m.cache(wallDir)

menuArg = m.getArgs()["menuArg"]
autoArg = m.getArgs()["autoArg"]
allArg = m.getArgs()["allArg"]
randomArg = m.getArgs()["randomArg"]
searchArg = m.getArgs()["searchArg"]

# If arguments are then, then run function

# Search wallpapers and display results
if searchArg:
    m.search(wallList, searchArg)

# Schuffle wallList to randomize wallpaper
if randomArg:
    random.shuffle(wallList)

# Print menu
if menuArg:
    m.menu(wallList)

# Autoset wallpapers from wallList
if autoArg:
    m.auto(wallList)

# Show all wallpapers in feh
if allArg:
    m.all(wallList)

