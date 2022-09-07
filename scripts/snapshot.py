import os
import subprocess
import sys
import argparse
import platform
import logging
import datetime
import shutil

# Configure logging
logging.basicConfig(format="%(levelname)s - %(name)s - %(message)s", level=logging.DEBUG)

# define starting avariables
osName = platform.system()

# If on windows
if osName == "Windows":
    print("Running on windows.")
    # vrDir = r"C:\Users\Anon\Desktop\VR"
    # rsyncBin = r"C:\Users\Anon\Desktop\VR\cwRsync_5.5.0_x86_Free\bin\rsync.exe"
    vrDir = r"D:\VR"
    
    # Use rsync through cywin
    # rsyncBin = r"rsync.exe"
    rsyncBin = r"C:\cygwin64\bin\rsync.exe"
    vrCopyDir = r"D:\VR"
    vrProjectsDir = r"\cgywin64\d\VR\Projects"
    vrRsyncDir = r"\cygwin64\d\VR"
    rsyncOpts = ["-avrpt", "--progress"]
    
# If on linux
elif osName == "Linux":
    print("Running on Linux.")
    vrDir = "/mnt/data/files/VR"
    vrCopyDir = "/mnt/data/files/VR"    
    vrRsyncDir = "/mnt/data/files/VR"
    rsyncBin = "/usr/bin/rsync"
    rsyncOpts = ["-avrpt", "--progress"]
    
    
# Catch all
else:
    print("Running on unsupported platform!")
    sys.exit(1)
    
# Debug
logging.debug("osName: %s", osName)
logging.debug("vrDir: %s", vrDir)
logging.debug("rsyncBin: %s", rsyncBin)
logging.debug("rsyncOpts: %s", rsyncOpts)
    
# Define main class
class main():
    def __init__(self):
        pass

    # Define arguments
    def get_args(self):
        parser = argparse.ArgumentParser(description="Quick script to take snapshots to roll back incase of botch.")
        parser.add_argument("-d", "--dir", help="Set directory to copy.")
        parser.add_argument("-c", "--copy", action="store_true", help="Copy source to target directories.")
        parser.add_argument("-r", "--rsync", action="store_true", help="Use rsync to copy source to target directories.")
        parser.add_argument("--snapshot", action="store_true", help="Take snapshot.")
        parser.add_argument("--restore", action="store_true", help="Restore from previous snapshot.")
        parser.add_argument("--menu", action="store_true", help="Show menu for possible entries to create snapshot.")


        args = parser.parse_args()
        dirArg = args.dir
        copyArg = args.copy
        rsyncArg = args.rsync
        snapshotArg = args.snapshot
        restoreArg = args.restore
        menuArg = args.menu

        # Iterate through arguments and return values
        for i in dirArg, copyArg, rsyncArg, snapshotArg, restoreArg, menuArg:
            try:
                i
            except Exception as e:
                i = None

        return {
            "dirArg": dirArg,
            "copyArg": copyArg,
            "rsyncArg": rsyncArg,
            "menuArg": menuArg,
            "snapshotArg": snapshotArg,
            "restoreArg": restoreArg
        }

    # Create menu to select and run copy for vrDir due to size.
    def menu(self, vrProjectsDir):
        try:
            vrProjectsDir
        except Exception as e:
            print(e)
            sys.exit(1)
            
        # Die if not found
        if not os.path.exists(vrProjectsDir):
            print(vrDir, "not found.")
            sys.exit(1)
            
        # Cache items to vrList
        vrList = []
#        for (root, dirs, files) in os.walk(vrDir):
#            for d in dirs:
#                dFull = os.path.join(root, d)
#                vrList.append(dFull)
#                
#            # Pass on files
#            for f in files:
#                pass
                
        # Item
        for item in os.listdir(vrProjectsDir):
            itemFull = os.path.join(vrProjectsDir, item)
            print("itemFull: ", itemFull)
            if os.path.isdir(itemFull):
                vrList.append(itemFull)
            else:
                pass
        
        # debug
        logging.debug("vrList: %s", vrList)
        
        # Prompt user
        vrCount = 0
        vrTotal = len(vrList)
        for item in vrList:
            vrCount += 1
            print("[", vrCount, "/", vrTotal, "]", item)
        vrInput = input("Select item: ")
        
        # Validate input
        if vrInput.isdigit() and int(vrInput) <= vrTotal:
            vrInputDir = vrList[int(vrInput)-1]
            print("Selected", vrInputDir)
            
            # Run and copied based on selection
            m.snapshot(vrInputDir)
            
        # Else
        else:
            print("Invalid input.")

    # Restore from backups to the original directory.
    def restore(self, vrDir):
        try:
            vrDir
        except Exception as e:
            print(e)
            sys.exit(1)

        if not os.path.exists(vrDir):
            print(vrDir, "not found.")
            sys.exit(1)

        vrDirBase = os.path.dirname(vrDir)
        vrDirName = os.path.basename(vrDir)

        # Set dirList
        dirList = []

        # Iterate over directories to cache entries
        for (root, dirs, files) in os.walk(vrDirBase):
            for d in dirs:
                if vrDirName in d and "_snapshot_" in d:
                    print("Found", d)
                    dFull = os.path.join(root, d)
                    dirList.append(dFull)

            for f in files:
                pass
        # Move current VR to VR_old
        # move snapshot to VR

        # Prompt the user
        while True:
            dirCount = 0
            dirTotal = len(dirList)
            print("Restore from snapshot.")
            for dir in dirList:
                dirCount += 1
                print("[", dirCount, "/", dirTotal, "]", dir)
            ansInput = input("Enter number: ")

            if ansInput.isdigit() and int(ansInput) <= dirTotal:
                ansDir = dirList[int(ansInput)-1]
                print("You entered", ansDir)

                # Move current vrDir to old
                vrDirOld = vrDir + "_old"
                print("Moving ", vrDir, "to", vrDirOld)
                os.rename(vrDir, vrDirOld)

                # move snapshot to current
                print("Moving", ansDir, "to", vrDir)
                os.rename(ansDir, vrDir)
            elif "q" in ansInput or "quit" in ansInput:
                print("Quitting")
                break



    # Define function to take snapshot of directory using rsync.
    def snapshot(self, vrDir):
        try:
            vrDir
        except Exception as e:
            print(e)
            sys.exit(1)

        if not os.path.exists(vrDir):
            print(vrDir, "not found.")
            sys.exit(1)

        try:
            if rsyncArg:
                # Get current timestamp for output directory
                currentTime = datetime.datetime.now()

                # Set timeformat
                timeFormat = "%d-%m-%Y_%M-%S"

                # Convert raw output to human readable
                currentTimeHuman = currentTime.strftime(timeFormat)

                # Now set up target to sync to
                #vrTarget = vrRsyncDir + "_snapshot_" + currentTimeHuman
                vrTarget = vrDir + "_snapshot_" + currentTimeHuman

                # Debug
                logging.debug("vrTarget: %s", vrTarget)

                # Define command and fill with main binary, paramters, source and target
                copyCommand = [rsyncBin]
                copyCommand.extend(rsyncOpts)
                copyCommand.append(vrCopyDir)
                copyCommand.append(vrTarget)

                # debug
                logging.debug("copyCommand: %s", copyCommand)

                # Run command
                subprocess.run(copyCommand, shell=False)

            if copyArg:
                # Get current timestamp for output directory
                currentTime = datetime.datetime.now()

                # Set timeformat
                timeFormat = "%d-%m-%Y_%M-%S"

                # Convert raw output to human readable
                currentTimeHuman = currentTime.strftime(timeFormat)

                # Now set up target to sync to
                #vrTarget = vrCopyDir + "_snapshot_" + currentTimeHuman
                vrTarget = vrDir + "_snapshot_" + currentTimeHuman

                # Debug
                logging.debug("vrTarget: %s", vrTarget)

                print("Copying", vrDir, "to", vrTarget)
                shutil.copytree(vrDir, vrTarget)

        except Exception as e:
            print(e)
            sys.exit(1)


# Run functions
m = main()

# Get arguemnts
dirArg = m.get_args()["dirArg"]
copyArg = m.get_args()["copyArg"]
rsyncArg = m.get_args()["rsyncArg"]
snapshotArg = m.get_args()["snapshotArg"]
restoreArg = m.get_args()["restoreArg"]
menuArg = m.get_args()["menuArg"]

# debug
logging.debug("dirArg: %s", dirArg)
logging.debug("copyArg: %s", copyArg)
logging.debug("rsyncArg: %s", rsyncArg)
logging.debug("snapshotArg: %s", snapshotArg)
logging.debug("restoreArg: %s", restoreArg)
logging.debug("menuArg: %s", menuArg)

# If menu
if menuArg:
    m.menu(vrDir)
else:
    # run snapshot
    if snapshotArg:
        m.snapshot(vrDir)

    # If restoreArg is passed.
    if restoreArg:
        m.restore(vrDir)