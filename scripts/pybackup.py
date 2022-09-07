import os
import subprocess
import datetime
import argparse
import subprocess
import logging
import platform
import shutil
import sys
import math 
import time

# Get platform
osSystem = platform.system()

# Get hostname
hostname = platform.node()

# Setup logging
logging.basicConfig(format="%(levelname)s - %(name)s - %(message)s", level=logging.DEBUG)

# Set main dateformat
#dateFormat="%d-%m-%Y_%M-%S"
dateFormat="%d-%m-%Y"

# Format for main log
logDateFormat="%d-%m-%Y_%H-%M-%S"

# Set variables needed for main portion of the script
if osSystem == "Windows":
    print("Running on Windows.")
    
    # Set rsyncBinCygwin to read from.
    rsyncBin = r"C:\cygwin64\bin\rsync.exe"
    
    # Set exclude file
    excludeFile = r"C:\Users\Anon\Desktop\code\windows\pybackup_exclude.txt"
    
    # Set remote options for ssh to be called from cygwin's build of ssh to correctly excute ssh portion of rsync
    rsyncOpts=["-arpt", "--exclude-from="+excludeFile]
    
    # Set rsync options for root files
    rsyncRootOpts=["-aAXv"]
    
    # Set mainlog
    mainLog = "D:\PyBackups\Pybackup_mainLog.log"
    
    # set backup list for windows
    #localBackupList = [r"/cygdrive/d/PyBackups", r"/cygdrive/e/PyBackups"]
    localBackupList = [r"D:\PyBackups", r"E:\PyBackups"]
    
    # Set boolean to adapt script to windows if ran on windows
    isWindows = True
    
elif osSystem == "Linux":
    print("Running on Linux.")
    rsyncBin = "/usr/bin/rsync"

    # Set rsync options
    #rsyncOpts=("-arptR" "--inplace")
    
    # Set exclude file
    excludeFile = "/home/insight/code/windows/pybackup_exclude.txt"
    
    rsyncOpts=["-arpt", "--exclude-from="+excludeFile]
    
    mainLog = "/PyBackups/mainLog.log"
    
    # Set backup list for linux
    localBackupList = ["/PyBackups"]
    
    # Set linux boolean
    isLinux = True
    
else:
    print("Unsupported platform")
    sys.exit(1)

# define main log
mainLog = "D:\PyBackups\mainLog.log"

# Set localhost backup locations
localList = [r"C:\cygwin64\home",
r"C:\Users\Anon\Desktop\Work",
r"C:\Users\Anon\Desktop\Data",
r"C:\Users\Anon\Desktop\Vid_Effects",
r"C:\Users\Anon\Desktop\Soundboard",
r"C:\Users\Anon\Desktop\bd-fetch",
r"C:\Users\Anon\Documents",
r"C:\Users\Anon\Pictures",
r"C:\Users\Anon\Desktop\main.kdbx",
r"C:\Users\Anon\Desktop\main_arch.kdbx",
r"C:\Users\Anon\Desktop\code"]

# set remote hosts to be contacted and backed up
# Set ITEM for VR directory
vrDir=r"D:\VR"

# Set ITEM for VM directory
vmDir=r"D:\VM"

# Set dir for OBS directory
obsDir=r"D:\OBS"

# Set dir for Downloads directory
downloadsDir=r"C:\Users\Anon\Downloads"

# Setup remote hosts to sync
remoteHosts=["laptop00", 
"pi00",
"pi01", 
"archvm", 
"mindbond.xyz",
"mindbondvm"]

# set remove directories to be backed up
remoteList=["/etc",
"/var/log",
"/root",
"/home",
"/var/www",
"/usr/local/searxng"]

# define main class
class main():
    def __init__(self):
        pass
    
    # return date
    def getDate(self):
        # Get current timestamp for output directory
        currentTime = datetime.datetime.now()
        
        # Convert raw output to human readable
        currentTimeHuman = currentTime.strftime(logDateFormat)
        
        # Return back date
        return (currentTimeHuman)
    
    # Set main file to write log
    def writeLog(self, log, message):
        if log is None or message is None:
            print("log or message is not properly set.")
            sys.exit(1)
        
        # If log doesn't exist, create with created timestamp
        if not os.path.exists(log):
            createFile = open(log, "w")
            print("Log created at", m.getDate())
            createFile.write("Log created at "+m.getDate()+"\n")
            createFile.close()
        
        # Open log file to append mode
        openFile = open(log, "a")
        logMessage = "[ Log: " + str(log) + "] [ Date: " + str(m.getDate()) + " ]" + str(message)+"\n"
        openFile.write(logMessage)
        openFile.close()
   
    # Convert windows directories to cygwin format
    def convertToCygwin(self, item):
        if item is None:
            print("Nothing set for item.")
            sys.exit(1)
            
        # Get drive letter from windows directory
        itemLetter = item.split(":")[0].lower()
        itemPath = item.split(":")[1].replace("\\", "/")
        cygwinPath = "/cygdrive/" + itemLetter + itemPath
        
        # Debug
        logging.debug("itemLetter: %s", itemLetter)
        logging.debug("itemPath: %s", itemPath)
        logging.debug("cygwinPath: %s", cygwinPath)
        
        # /cygdrive/<letter>/<path>
        
        # Return back converted path
        return(cygwinPath)
   
    # convert cygwin path to windows
    def convertToWindows(self, item):
        if item is None:
            print("Nothing set for item.")
            sys.exit(1)
            
        itemLetter = item.split("/")[2].upper()
        itemPath = '\\'.join(item.split("/")[3:])
        windowsPath = itemLetter + ":\\" + itemPath
        
        # <letter>:\<path>
        
        # debug
        logging.debug("itemLetter: %s", itemLetter)
        logging.debug("itemPath: %s", itemPath)
        logging.debug("windowsPath: %s", windowsPath)
        
        # return back converted path
        return(windowsPath)
 
    # Get size from bytes to human readable format.
    def getSize(self, item):
        if item is None:
            print("Nothing set for item.")
            sys.exit(1)
        
        # Convert raw output of bytes into human readable format
        #inputFileSize = os.path.getsize(inputFile)
        #num = item
        suffixes = ["B", "KB", "MB", "GB", "TB"]
        for x in suffixes:
            if item < 1024.0:
                #print(inputFile, "is", round(num, 2), x)
                itemHuman = str(round(item, 2))+str(x)
                break
            item /= 1024.0
            
        return (itemHuman)
 
    # check space and item passed, die if not found or not properly set.
    def checkSpace(self, item):
        if item is None:
            print("Nothing set for item to check.")
            sys.exit(1)
            
        if not os.path.exists(item):
            print("Could not find", item)
            sys.exit(1)
            
        # Set threshold to trigger if disk reports back being over capacity.
        threshold = 90
        
        # Get main disk info in bytes
        itemBytesTotal = shutil.disk_usage(item)[0]
        itemBytesUsed = shutil.disk_usage(item)[1]
        itemBytesFree = shutil.disk_usage(item)[2]
        
        # Debug
        logging.debug("Item Bytes Total: %s", itemBytesTotal)
        logging.debug("Item Bytes Used: %s", itemBytesUsed)
        logging.debug("Item Bytes Free: %s", itemBytesFree)
        
        # Convert sizes
        itemHumanTotal = m.getSize(itemBytesTotal)
        itemHumanUsed = m.getSize(itemBytesUsed)
        itemHumanFree = m.getSize(itemBytesFree)
        
        # Get our percentage and round up
        itemPerc = round((itemBytesUsed/itemBytesTotal) * 100)
        
        # Notify user
        print(item+" - "+itemHumanUsed+" of "+itemHumanTotal+" - "+str(itemPerc)+"%")
        
        # Write log
        if logArg:
            m.writeLog(logArg, item+" - "+itemHumanUsed+" of "+itemHumanTotal+" - "+str(itemPerc)+"%")
        #m.writeLog(mainLog, item+" - "+itemHumanUsed+" of "+itemHumanTotal+" - "+str(itemPerc)+"%")
        
        # If over threshold, notify user and exit.
        if itemPerc > threshold:
            print(item, "is over threshold and must be cleared off.")
            sys.exit(1)
        
   
    # clear old entries to clear space on drives
    def clearOld(self, item):
        # main list to clear old entries from.
        clearList = []
        
        # Set the number of days the entry is older than to be cleared by
        # 86,400 seconds for one day
        if dayLimitArg:
            dayLimit = int(dayLimitArg)
        else:
            dayLimit = 7
        
        # Die if item is not properly set or found.
        if item is None:
            print("Item is not set.")
            sys.exit(1)
            
        if not os.path.exists(item):
            print(item, "not set.")
            sys.exit(1)

        # Example
        #import time
        #from path import path

        #seven_days_ago = time.time() - 7 * 86400   
        #base = path('/path/to/dir')

        #for somefile in base.walkfiles():
        #    if somefile.mtime < seven_days_ago:
        #        somefile.remove()
   
        # Iterate over items
        for i in os.listdir(item):
            iFull = os.path.join(item, i)
            
            # Skip item if not directory
            if not os.path.isdir(iFull):
                continue
            
            # If so, go down and gather matches with current date
            for e in os.listdir(iFull):
                if "_date_" in e:
                    # Get full path for proper removal, stats and check if its over age date for removal.
                    eFull = os.path.join(iFull, e)
                    eMTime = os.path.getmtime(eFull)
                    curTime = time.time()
                    eTestTime = round((curTime - eMTime) / 86400)
                    
                    # Debug
                    logging.debug("eFull: %s", eFull)
                    logging.debug("eMTime: %s", eMTime)
                    logging.debug("curTime: %s", curTime)
                    logging.debug("eTestTime: %s", eTestTime)
                    
                    # If over dayLimit, then append.
                    if eTestTime > dayLimit:
                        clearList.append(eFull)
                        
        # Iterate over gathered results
        iCount = 0
        iTotal = len(clearList)
        
        # Print out results
        for i in clearList:
            iCount += 1 
            print("[", iCount, "/", iTotal, "] Found", i)
        
        readAns = input("Remove entries? ")
        if "y" in readAns:
            for dir in clearList:
                if os.path.exists(dir):
                    print("Removing "+dir)
                    # Remove results
                    try:
                        shutil.rmtree(dir)
                    except Exception as e:
                        print(e)
        else:
            print("Not removing.")
                    
    # Set function to handle system commands with subprocess
    # Get arguments
    def setArgs(self):
        parser = argparse.ArgumentParser(description="Backup local and remote systems.")
        parser.add_argument("--local", action="store_true", help="Run local sync.")
        parser.add_argument("--remote", action="store_true", help="Run remote sync.")
        parser.add_argument("--date", action="store_true", help="Run sync with creating timestamp format.")
        parser.add_argument("--verbose", action="store_true", help="Run sync with verbose output.")
        parser.add_argument("--delete", action="store_true", help="Run sync with deleting old files from backup sync.")
        parser.add_argument("--check", action="store_true", help="Check space on drives.")
        parser.add_argument("--clear", action="store_true", help="Clear old backups on drives to save space.")
        parser.add_argument("--root", action="store_true", help="Sync root instead of set directories.")
        parser.add_argument("--vr", action="store_true", help="Run local sync on vr directory.")
        parser.add_argument("--vm", action="store_true", help="Run local sync on vm directory.")
        parser.add_argument("--obs", action="store_true", help="Run local sync on obs directory.")
        parser.add_argument("--downloads", action="store_true", help="Run local sync on downloads directory.")
        parser.add_argument("--limit", help="Set limit for rsync to transfer data over.")
        parser.add_argument("--limit-all", help="Set limit for entire pybackup script.")
        parser.add_argument("--host", help="Set single host to backup.")
        parser.add_argument("--dir", help="Set custom directory to backup instead of backupItems.")
        parser.add_argument("--log", help="Set log file.")
        parser.add_argument("--day-limit", help="Set number of days that the clearOld portion will remove by. Default is 7 days.")
       
        args = parser.parse_args()
        localArg = args.local
        remoteArg = args.remote
        vrArg = args.vr
        vmArg = args.vm
        obsArg = args.obs
        downloadsArg = args.downloads
        verboseArg = args.verbose
        deleteArg = args.delete
        dateArg = args.date
        checkArg = args.check
        clearArg = args.clear
        rootArg = args.root
        limitArg = args.limit
        limitAllArg = args.limit_all
        hostArg = args.host
        dirArg = args.dir
        logArg = args.log
        dayLimitArg = args.day_limit
        
        return {
            "localArg": localArg,
            "remoteArg": remoteArg,
            "vmArg": vmArg, 
            "vrArg": vrArg,
            "obsArg": obsArg,
            "downloadsArg": downloadsArg,
            "verboseArg": verboseArg,
            "deleteArg": deleteArg,
            "dateArg": dateArg,
            "checkArg": checkArg,
            "clearArg": clearArg,
            "rootArg": rootArg,
            "limitArg": limitArg,
            "limitAllArg": limitAllArg,
            "hostArg": hostArg,
            "dirArg": dirArg,
            "logArg": logArg,
            "dayLimitArg": dayLimitArg
            }

# define main class for syncing files
class sync():
    def __init__(self):
        pass
     
    # Sync root
    #sudo rsync -aAXv / --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found"} /mnt
     
    # Do local sync
    def local(self, dir, hostname, item):
        if dir is None or item is None or hostname is None:
            print("dir, item or hostname is not properly set.")
            sys.exit(1)

        # item basename
        itemBase = os.path.basename(item)
        
        # Example
        # rsync -avrpt --progress <item> <item_current>
  
        # Set current directory
        itemCurrent = dir+"\\"+hostname+"\\"+itemBase+"_current"
        
        # Debug
        logging.debug("item: %s", item)
        logging.debug("itemCurrent: %s", itemCurrent)

        # create itemCurrent if not found
        if not os.path.exists(itemCurrent):
            print("Creating", itemCurrent)
            os.makedirs(itemCurrent)
        
        # convert to cygwin path before running
        if isWindows is True:
            if ":" in item:
                item = m.convertToCygwin(item)
            
            if ":" in itemCurrent:
                itemCurrent = m.convertToCygwin(itemCurrent)
       
       # check for exclude file
        if not os.path.exists(excludeFile):
            print("Could not find exclude file.")
            sys.exit(1)
            
        # Create main local sync command
        rsyncCommand = [ rsyncBin ]
        rsyncCommand.extend(rsyncOpts)
        if logArg:
            rsyncCommand.append("--log-file="+logArg)
        #rsyncCommand.append("--log-file="+mainLog)
        rsyncCommand.append(item)
        rsyncCommand.append(itemCurrent)
        print("rsyncCommand: ", rsyncCommand)
      
        # Write to log
        if logArg:
            m.writeLog(mainLog, rsyncCommand)
    
        # Notify user
        print("[ "+m.getDate()+" ] [ Local sync ] Syncing " + item + " to " + itemCurrent)
    
        # Run local rsyncCommand
        runLocalSync = subprocess.run(rsyncCommand)
        
        # Get returncode
        runReturn = runLocalSync.returncode
        logging.debug("runReturn: %s", runReturn)
        
    # Sync local root
    def localRoot(self, host, dir):
        if dir is None or host is None:
            print("dir or host is not properly set.")
            sys.exit(1)
        
        # Set rootfs name.
        rootName = "rootfs"
        
        # Set current directory for rootfs
        rootCurrent = dir+"\\"+host+"\\"+rootName+"_current"
      
        # If current directory is not found, then create
        if not os.path.exists(rootCurrent):
            print("Creating "+rootCurrent)
            os.mkdir(rootCurrent)
            
        # check for exclude file
        if not os.path.exists(excludeFile):
            print("Could not find exclude file.")
            sys.exit(1)
            
        syncRootCommand = [ rsyncBin ]
        syncRootCommand.extend(rsyncRootOpts)
        
        # If windows set ssh
        if isWindows is True:
            syncRootCommand.extend(["-e", r"C:\cygwin64\bin\ssh.exe"])
        
        syncRootCommand.append("/")
        syncRootCommand.append(rootCurrent)
            
        # Debug
        logging.debug("syncRootCommand: %s", syncRootCommand)
            
        #runSyncRoot = subprocess.run(syncRootCommand)
        #if runSyncRoot.returncode > 0:
        #    print("Could not run local root sync.")
      
    # Do remote sync
    def remote(self, dir, host, item):
        # Die if everything is not properly set
        if dir is None or item is None or host is None:
            print("dir, item, host is not properly set.")
            sys.exit(1)
        
        # get itemBasename
        itemBasename = os.path.basename(item)
        
        # Example
        # rsync -avrpt --progress <host>:<item> <item_sync>

        itemCurrent = dir+"\\"+host+"\\"+itemBasename+"_current"
        
        # Create main directory and subdirectories
        if not os.path.exists(itemCurrent):
            print("Creating", itemCurrent)
            os.makedirs(itemCurrent)
        
        # Must have root access to remote box.
        syncUser = "root"
        
        # convert paths if windows
        if isWindows is True:
            if ":" in item:
                item = m.convertToCygwin(item)
            
            if ":" in itemCurrent:
                itemCurrent = m.convertToCygwin(itemCurrent)

        # Create remote sync command
        rsyncCommand = [ rsyncBin ]
        rsyncCommand.extend(rsyncOpts)
        
        # if limitArg is passed  
        if limitArg:
            rsyncCommand.append("--bwlimit="+limitArg)
        
        # if logArg is passed
        if logArg:
            rsyncCommand.append("--log-file="+logArg)
        #rsyncCommand.append("--log-file="+mainLog)
        
        # Set ssh for windows 
        if isWindows:
            rsyncCommand.extend(["-e", r"C:\cygwin64\bin\ssh.exe"])
        
        rsyncCommand.append(syncUser+"@"+host+":"+item)
        rsyncCommand.append(itemCurrent)
        
        # debug
        logging.debug("rsyncCommand: %s", rsyncCommand)

        # Notify user
        print("[ "+m.getDate()+" ] [ Remote sync ] Syncing " + item + " from " + host + " to " + itemCurrent)

        # Write to log
        if logArg:
            m.writeLog(logArg, rsyncCommand)
        #m.writeLog(mainLog, rsyncCommand)

        # Run command
        runRemoteSync = subprocess.run(rsyncCommand)
        
        # Get return code and debug
        runSyncReturncode = runRemoteSync.returncode
        logging.debug("runSyncReturncode: %s", runSyncReturncode)
        
     # Sync local root
    def remoteRoot(self, host, dir):
        if dir is None or host is None:
            print("dir or host is not properly set.")
            sys.exit(1)
        
        # Set rootfs name.
        rootName = "rootfs"
        
        # Set current directory for rootfs
        rootCurrent = dir+"\\"+host+"\\"+rootName+"_current"
      
        # Convert to cygwin if on windows
        if isWindows is True:
            if ":" in dir:
                dir = m.convertToCygwin(dir)
      
            if ":" in rootCurrent:
                rootCurrent = m.convertToCygwin(rootCurrent)
      
        # If current directory is not found, then create
        if not os.path.exists(rootCurrent):
            print("Creating "+rootCurrent)
            os.mkdir(rootCurrent)
            
        # check for exclude file
        if not os.path.exists(excludeFile):
            print("Could not find exclude file.")
            sys.exit(1)

        # Setup remote root command
        syncRootCommand = [ rsyncBin ]
        syncRootCommand.extend(rsyncRootOpts)
        
        # if limitArg is passed  
        if limitArg:
            syncRootCommand.append("--bwlimit="+limitArg)
       
        # Set ssh for windows 
        if isWindows is True:
            rsyncCommand.extend(["-e", r"C:\cygwin64\bin\ssh.exe"])
       
        syncRootCommand.append(host+":"+dir)
        syncRootCommand.append(rootCurrent)
            
        # Debug
        logging.debug("syncRootCommand: %s", syncRootCommand)
            
        #runSyncRoot = subprocess.run(syncRootCommand)
        #if runSyncRoot.returncode > 0:
        #    print("Could not run local root sync.")

    # Sync current directory to date timestamp.
    def date(self, dir, host, item):
       if dir is None or item is None or host is None:
            print("dir or item is not properly set.")
            sys.exit(1)
        
       # get itemBasename
       itemBasename = os.path.basename(item)
        
       # item basename
       itemBase = os.path.basename(item)
      
       # Example
       # rsync -avrpt --progress <item> <item_sync>
        
       # Create current directory
       itemCurrent = dir + "\\" + host + "\\" + itemBase + "_current"
       
       # die if itemCurrent is not found.
       if not os.path.exists(itemCurrent):
            print(itemCurrent, "not exists. Skipping.")
            if logArg:
                m.writeLog(logArg, "[ Date ]"+itemCurrent+" not exists. Skipping.")
            #m.writeLog(mainLog, "[ Date ]"+itemCurrent+" not exists. Skipping.")
            return 1
        
       # Set timeformat
       timeFormat = "%d-%m-%Y"

       # Get current timestamp for output directory
       currentTime = datetime.datetime.now()

       # Convert raw output to human readable
       currentTimeHuman = currentTime.strftime(timeFormat)
        
       # Example
       # rsync -avrpt --progress <host>:<item> <item_sync>
      
       itemDate = itemCurrent+"_date_"+currentTimeHuman
 
       # debug
       logging.debug("itemCurrent: %s", itemCurrent)
       logging.debug("itemDate: %s", itemDate)

       # create itemDate if not found
       if not os.path.exists(itemDate):
           print("Creating", itemDate)
           os.makedirs(itemDate)

       # Convert paths to cygwin if on windows
       if isWindows is True:
            if ":" in itemCurrent:
                itemCurrent = m.convertToCygwin(itemCurrent)
       
            if ":" in itemDate:
                itemDate = m.convertToCygwin(itemDate)

       # check for exclude file
       if not os.path.exists(excludeFile):
           print("Could not find exclude file.")
           sys.exit(1)

       # Create remote sync command
       rsyncCommand = [ rsyncBin ]
       rsyncCommand.extend(rsyncOpts)
       
       if logArg:
            rsyncCommand.append("--log-file="+logArg)
       #rsyncCommand.append("--log-file="+mainLog)
       
       rsyncCommand.append(itemCurrent)
       rsyncCommand.append(itemDate)
       
       # Debug
       logging.debug("rsyncCommand: %s", rsyncCommand)
       
       # Notify user
       print("[ "+m.getDate()+" ] [ Local date ] Syncing "+str(itemCurrent)+" to "+str(itemDate))
       
       # Write to log
       if logArg:
            m.writeLog(logArg, rsyncCommand)
       #m.writeLog(mainLog, rsyncCommand)

       # Run command
       runDateSync = subprocess.run(rsyncCommand)
       
       runDateReturncode = runDateSync.returncode
       logging.debug("runDateReturncode: %s", runDateReturncode)

# Define main object
m = main()
s = sync()

# Set arguments
vrArg = m.setArgs()["vrArg"]
vmArg = m.setArgs()["vmArg"]
obsArg = m.setArgs()["obsArg"]
downloadsArg = m.setArgs()["downloadsArg"]
localArg = m.setArgs()["localArg"]
remoteArg = m.setArgs()["remoteArg"]
verboseArg = m.setArgs()["verboseArg"]
deleteArg = m.setArgs()["deleteArg"]
dateArg = m.setArgs()["dateArg"]
checkArg = m.setArgs()["checkArg"]
clearArg = m.setArgs()["clearArg"]
rootArg = m.setArgs()["rootArg"]
limitArg = m.setArgs()["limitArg"]
limitAllArg = m.setArgs()["limitAllArg"]
hostArg = m.setArgs()["hostArg"]
dirArg = m.setArgs()["dirArg"]
logArg = m.setArgs()["logArg"]
dayLimitArg = m.setArgs()["dayLimitArg"]

# debug
logging.debug("vrArg: %s", vrArg)
logging.debug("vmArg: %s", vmArg)
logging.debug("obsArg: %s", obsArg)
logging.debug("downloadsArg: %s", downloadsArg)
logging.debug("localArg: %s", localArg)
logging.debug("remoteArg: %s", remoteArg)
logging.debug("verboseArg: %s", verboseArg)
logging.debug("deleteArg: %s", deleteArg)
logging.debug("dateArg: %s", dateArg)
logging.debug("checkArg: %s", checkArg)
logging.debug("clearArg: %s", clearArg)
logging.debug("rootArg: %s", rootArg)
logging.debug("limitAllArg: %s", limitAllArg)
logging.debug("limitArg: %s", limitArg)
logging.debug("hostArg: %s", hostArg)
logging.debug("dirArg: %s", dirArg)
logging.debug("logArg: %s", logArg)
logging.debug("dayLimitArg: %s", dayLimitArg)

# Test conversion
#testItem = r"C:\Users\Anon\Desktop\test.txt"
#testItem = m.convertToCygwin(testItem)
#estItem = m.convertToWindows(testItem)

# if verboseArg is passed, append both options of rsync to enable rsync's verbose progress
if verboseArg:
    rsyncOpts.append("--verbose")
    rsyncOpts.append("--progress")
    rsyncOpts.append("--info=progress2")

#if deleteArg is passed
if deleteArg:
    rsyncOpts.append("--delete")

# if hostArg is set, set remoteHosts to specified host.
if hostArg:
    print("Backing up remote host: "+hostArg)
    remoteHosts = [ hostArg ]

# if dirArg is set, set localBackupList to dirArg
if dirArg:
    print("Backing up to "+dirArg)
    localBackupList = [ dirArg ]

# if limitAllArg is passed  
if limitAllArg:
    rsyncOpts.append("--bwlimit="+limitAllArg)

# if VR argument
if vrArg:
    backupCount = 0
    backupTotal = len(localBackupList)
    
    # Iterate over local drives
    for backupItem in localBackupList:
        backupCount += 1
        print("[ "+m.getDate()+"] [ VR Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ] "+str(backupItem))
        
        # write log
        if logArg:
            m.writeLog(logArg, "[ VR Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        #m.writeLog(mainLog, "[ VR Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        
        # Run
        s.local(backupItem, hostname, vrDir)
        
        if dateArg:
            print("[ VR Backup Date ]", vrDir)
            s.date(backupItem, hostname, vrDir)
    
# if VM argument is passed
if vmArg:
    backupCount = 0
    backupTotal = len(localBackupList)
    
    # Iterate over local drives
    for backupItem in localBackupList:
        backupCount += 1
        print("[ "+m.getDate()+" ] [ VM Backup ] ["+str(backupCount)+" / "+str(backupTotal)+" ] "+backupItem)
        
        # write to log
        if logArg:
            m.writeLog(logArg, "[ VM Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        #m.writeLog(mainLog, "[ VM Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        
        # Run
        s.local(backupItem, hostname, vmDir)
        
# if OBS argument is passed
if obsArg:
    backupCount = 0
    backupTotal = len(localBackupList)
    
    # Iterate over local drives
    for backupItem in localBackupList:
        backupCount += 1
        print("[ "+m.getDate()+" ] [ OBS Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ] "+backupItem)
        
        # write to log
        if logArg:
            m.writeLog(logArg, "[ OBS Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        #m.writeLog(mainLog, "[ OBS Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        
        # Run
        s.local(backupItem, hostname, obsDir)
        
# if downloads argument is passed
if downloadsArg:
    backupCount = 0
    backupTotal = len(localBackupList)
    
    # Iterate over local drives
    for backupItem in localBackupList:
        backupCount += 1
        print("[ "+m.getDate()+" ] [ downloads Backup ] ["+str(backupCount)+" / "+str(backupTotal)+" ] "+backupItem)
        
        # write to log
        if logArg:
            m.writeLog(logArg, "[ downloads Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        #m.writeLog(mainLog, "[ downloads Backup ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        
        # Run
        s.local(backupItem, hostname, downloadsDir)

# check disks
if checkArg:
    backupCount = 0 
    backupTotal = len(localBackupList)
    
    for backupItem in localBackupList:
        backupCount += 1
        
        # Notify user
        print("[ "+str(backupCount) +"/"+str(backupTotal)+" ] [ Checking: " + backupItem + " ]")
        
        # check each item
        m.checkSpace(backupItem)
        
# clear space off disks
if clearArg:
    backupCount = 0 
    backupTotal = len(localBackupList)
    
    # Iterate and setup each location to clear off old backups
    for backupItem in localBackupList:
        backupCount += 1
        
        # Notify user
        print("[ " +str(backupCount) + "/" + str(backupTotal) + " ] [ Clearing: "+backupItem+" ]")
        
        # Run
        m.clearOld(backupItem)

# Setup local backup
if localArg:
    backupCount = 0
    backupTotal = len(localBackupList)
    
    # Iterate over local drives
    for backupItem in localBackupList:
        backupCount += 1
        print("[ "+m.getDate()+" ] [ Backup ] [", backupCount, "/", backupTotal, "]", backupItem)
        
        # Create counters
        localCount = 0
        localTotal = len(localList)
        
        # Iterate over directories in localList
        for localItem in localList:
            localCount += 1
            
            # Notify user
            print("[ "+m.getDate()+" ] [ Local ] [ "+str(localCount)+" / "+str(localTotal)+" ] "+localItem)
            
            # Write to log
            if logArg:
                m.writeLog(logArg, "[ Local ] [ "+str(localCount)+" / "+str(localTotal)+" ]"+localItem)
            #m.writeLog(mainLog, "[ Local ] [ "+str(localCount)+" / "+str(localTotal)+" ]"+localItem)
            
            # Skip over item if backupItem could not be found on the system.
            if not os.path.exists(backupItem):
                print("Could not find "+backupItem)
                continue
                
            # Run local windows sync
            s.local(backupItem, hostname, localItem)
            
            # if date arg is passed
            if dateArg:
                s.date(backupItem, hostname, localItem)
        
        # if root is set
        if rootArg:
            print("[ "+m.getDate()+" ] [ Local Root ]")
                
            # write log
            if logArg:
                m.writeLog(logArg, "[ Local Root ]")
            #m.writeLog(mainLog, "[ Local Root ]")
        
            # Run local sync of root
            s.localRoot(backupItem, hostname, "/")
        
            # if date arg is passed
            if dateArg:
                s.date(backupItem, hostname, "/")
        
        # # If date argument is passed, create date timestamp
        # if dateArg:
            # # Create counters
            # localCount = 0
            # localTotal = len(localList)
        
            # # Iterate over directories in localList
            # for localItem in localList:
                # localCount += 1
                # print("[ "+m.getDate()+" ] [ Local Date ] [ "+str(localCount)+" / "+str(localTotal)+" ]"+str(localItem))
                
                # # write log
                # if logArg:
                    # m.writeLog(logArg, "[ Local Date ] [ "+str(localCount)+" / "+str(localTotal)+" ]"+localItem)
                # #m.writeLog(mainLog, "[ Local Date ] [ "+str(localCount)+" / "+str(localTotal)+" ]"+localItem)
                
                # # Now create snapshot of local item
                # s.date(backupItem, hostname, localItem)
        
# Setup remote backup
if remoteArg:
    backupCount = 0
    backupTotal = len(localBackupList)
    
    for backupItem in localBackupList:
        backupCount += 1
        print("[ "+m.getDate()+" ] [ Remote ] ["+str(backupCount)+" / "+str(backupTotal)+" ] "+str(backupItem))
        
        # Write log
        if logArg:
            m.writeLog(logArg, "[ Remote ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        #m.writeLog(mainLog, "[ Remote ] [ "+str(backupCount)+" / "+str(backupTotal)+" ]"+str(backupItem)+"\n")
        
        # check space
        m.checkSpace(backupItem)
        
        # Iterate over hosts
        hostCount = 0
        hostTotal = len(remoteHosts)
        for host in remoteHosts:
            hostCount += 1
            print("[ "+m.getDate()+" ] [ host ] [ "+str(hostCount)+" / "+str(hostTotal)+" ] "+str(host))
            
            # Write log
            if logArg:
                m.writeLog(logArg, "[ host ] [ "+str(hostCount)+"/"+str(hostTotal)+"]"+str(host))
            #m.writeLog(mainLog, "[ host ] ["+str(hostCount)+"/"+str(hostTotal)+"]"+str(host))
            
            # iterate over remote directories on host and sync to local
            remoteCount = 0
            remoteTotal = len(remoteList)
            
            for remoteItem in remoteList:
                remoteCount += 1
                print("[ "+m.getDate()+" ] [ Remote ] [ "+str(remoteCount)+" / "+str(remoteTotal)+" ] "+remoteItem)
                
                # Write log
                if logArg:
                    m.writeLog(logArg, "[ Remote ] [ "+str(remoteCount)+" / "+str(remoteTotal)+" ]"+str(remoteItem)+"\n")
                #m.writeLog(mainLog, "[ Remote ] [ "+str(remoteCount)+" / "+str(remoteTotal)+" ]"+str(remoteItem)+"\n")
                
                # Backup from remote host to local
                s.remote(backupItem, host, remoteItem)
                
                # if dateArg is passed
                if dateArg:
                    s.date(backupItem, host, remoteItem)
                
            # if root is set
            if rootArg:
                print("[ "+m.getDate()+" ] [ Remote Root ] "+host)
                
                # Write log
                if logArg:
                    m.writeLog(logArg, "[ Remote Root ] \n")
                #m.writeLog(mainLog, "[ Remote Root ] \n")
                
                s.remoteRoot(backupItem, hostname, "/")
                
                # If date is set.
                if dateArg:
                    s.date(backupItem, host, "/")
            
            # # If date argument is passed, create date timestamp
            # if dateArg:
                # # Create counters
                # remoteCount = 0
                # remoteTotal = len(remoteList)
        
                # # Iterate over directories in localList
                # for remoteItem in remoteList:
                    # remoteCount += 1
                    # print("[ "+m.getDate()+" ] [ Remote date ] [ "+str(remoteCount)+" / "+str(remoteTotal)+" ] "+remoteItem)
                    
                    # # Write log
                    # if logArg:
                        # m.writeLog(logArg, "[ Remote date ] [ "+str(remoteCount)+" / "+str(remoteTotal)+" ]"+str(remoteItem)+"\n")
                    # #m.writeLog(mainLog, "[ Remote date ] [ "+str(remoteCount)+" / "+str(remoteTotal)+" ]"+str(remoteItem)+"\n")
 
                    # # Create timestamp
                    # s.date(backupItem, host, remoteItem)