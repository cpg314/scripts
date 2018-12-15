#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""radio

Usage:
  radio
  radio <name-or-id>

"""
import subprocess
import sys
import signal
import requests
import time
import threading
import platform
from docopt import docopt
from utils import loadConfig


# Get current title from stream
def getTitle(url):
    r = requests.get(url, headers={"Icy-MetaData": "1"}, stream=True)
    h = r.headers
    title = ""
    if "icy-metaint" in h:
        metaint = int(h["icy-metaint"])
        metadata = next(r.iter_content(metaint + 255, decode_unicode=True))[metaint:]
        title = metadata.split(b";")[0].split(b"=")[-1][1:-2]
        try:
            title = title.decode("utf-8")
        except:
            title = title.decode("latin-1", errors="ignore")
    return title


# Print current title (if changed), and refresh after 60 seconds
def printTitle(url, previous=""):
    title = getTitle(url)
    if title != previous:
        print(time.strftime('%X'), title)
    t = threading.Timer(60, printTitle, [url, title])
    t.daemon = True
    t.start()


def selectChannel(channels):
    for i, c in enumerate(channels):
        print("[{}] {}".format(i, c[0]))
    try:
        i = int(input("Channel: "))
        return channels[i]
    except:
        print("Invalid input")
        exit()


def play(channel):
    print("Playing " + channel[0])
    printTitle(channel[1])
    vlcpath = "/usr/bin/vlc" if platform.system() == "Linux" else "/Applications/VLC.app/Contents/MacOS/VLC"
    return subprocess.Popen([vlcpath, "-Idummy", channel[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)


def getChannel(nameorid, channels):
    try:
        return channels[int(nameorid)]
    except:
        pass
    try:
        return [c for c in channels if c[0] == nameorid][0]
    except Exception as e:
        return selectChannel(channels)


def main():
    channels = loadConfig("radios.yaml")
    args = docopt(__doc__)
    process = play(getChannel(args["<name-or-id>"], channels))

    # Handle exit
    def signal_handler(signal, frame):
        process.kill()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()


if __name__ == '__main__':
    main()
