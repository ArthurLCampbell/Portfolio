#!/usr/bin/python3

# import os
# import subprocess as sp
# import re
from bs4 import BeautifulSoup
# from colorama import init
# from colorama import Fore, Back, Style
import logging
import sys
import requests
import platform
import argparse

# Configure logging
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

# init color
# init()

# Title, timestamp, article
siteData = []
titles = []
timestamps = []
articles = []

# Define main urls
urlAMD64 = "https://archlinux.org"
urlX86 = "https://archlinux32.org"
urlARM = "https://archlinuxarm.org"

# get platform
sysArch = platform.machine()

# Define main class
class main():
    def __init__(self):
        pass

    def getArgs(self):
        parser = argparse.ArgumentParser(description="Fetch latest in arch linux news.")
        parser.add_argument("--all", action="store_true", help="Show all main info of each platform: x86, amd64, arm.")

        args = parser.parse_args()
        allArg = args.all

        #for item in allArg:
        #    try:
        #        item
        #    except NameError:
        #        item = None
        if allArg:
            allArg = allArg
        else:
            allArg = None

        return {
                "allArg": allArg
                }

    # Fetch x86
    def fetchAMD64(self, url):
        print("URL: " + url)
        logging.debug("URL: %s", url)

        try:
            headers = {}
            r = requests.get(url, headers=headers)
            rStatus = r.status_code
            rText = r.text
        except requests.ConnectTimeout:
            print("Timeout!")
            sys.exit(1)

        # Create parser object
        soup = BeautifulSoup(rText, "html.parser")

        # div id="news"
        # h4 -> Title
        # p class="timestamp"
        # div class="article-content"

        #print(soup.prettify())
        #print(soup.get_text())

        #for data in soup.find_all("div"):
        #    print(data)

        # Data
        for data in soup.find_all("div", id="news"):
            # Parse through and find required fields
            for title, timestamp, article in zip(data.find_all("h4"), data.find_all("p", "timestamp"), data.find_all("div", "article-content")):
                titleParse = title.get_text().strip()
                timestampParse = timestamp.get_text().strip()
                articleParse = article.get_text().strip()

                if titleParse is not None and timestampParse is not None and articleParse is not None:
                    siteData.append([titleParse, timestampParse, articleParse])

        # Iterate through siteData array
        articleCount = 0
        for title, timestamp, article in siteData:
            articleCount += 1
            print("[" + str(articleCount) + "]" + " Title: " + title)
            print("Published: " + timestamp)
            print(article, "\n")

            logging.debug("title: %s", title)
            logging.debug("timestamp: %s", timestamp)
            logging.debug("article: %s", article)

    # Fetch x86
    def fetchX86(self, url):
        print("URL: " + url)
        logging.debug("URL: %s", url)

        try:
            headers = {}
            r = requests.get(url, headers=headers)
            rStatus = r.status_code
            rText = r.text
        except requests.ConnectTimeout:
            print("Timeout!")
            sys.exit(1)

        # Create parser object
        soup = BeautifulSoup(rText, "html.parser")

        # div id="news"
        # h4 -> Title
        # p class="timestamp"
        # div class="article-content"

        #print(soup.prettify())
        #print(soup.get_text())

        #for data in soup.find_all("div"):
        #    print(data)

        # Data
        for data in soup.find_all("div", id="news"):
            # Parse through and find required fields
            for title, timestamp, article in zip(data.find_all("h4"), data.find_all("p", "timestamp"), data.find_all("div", "article-content")):
                titleParse = title.get_text().strip()
                timestampParse = timestamp.get_text().strip()
                articleParse = article.get_text().strip()

                if titleParse is not None and timestampParse is not None and articleParse is not None:
                    siteData.append([titleParse, timestampParse, articleParse])

        # Iterate through siteData array
        articleCount = 0
        for title, timestamp, article in siteData:
            articleCount += 1
            print("[" + str(articleCount) + "]" + " Title: " + title)
            print("Published: " + timestamp)
            print(article, "\n")

            logging.debug("title: %s", title)
            logging.debug("timestamp: %s", timestamp)
            logging.debug("article: %s", article)


m = main()
allArg = m.getArgs()["allArg"]
print(sysArch)

# Fetch everything.
if allArg:
    print("Fetching everything.")
    m.fetchX86(urlX86)
    m.fetchX86(urlAMD64)
    m.fetchX86(urlARM)
else:
    # Fetch amd64
    if "x86_64" in sysArch:
        m.fetchAMD64(urlAMD64)

    # Fetch i386
    elif "i386" in sysArch:
        m.fetchAMD64(urlX86)

    # Fetch arm
    elif "arm" in sysArch:
        m.fetchAMD64(urlARM)
    else:
        print("Unable to determine platform.")
        sys.exit(1)

