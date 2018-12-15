#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""slideshare

Usage:
  slideshare <input>... [--output=<output>]

"""
from docopt import docopt
from bs4 import BeautifulSoup
import requests
import os
import re
import urllib.request
import tempfile
from subprocess import call
import progressbar

def downloadURL(url, output=None):
    print(url)
    print("Download page...")
    r = requests.get(url).text
    slides = list(re.findall("data-full=\"(.*?)\"", r))
    # Title
    title = slides[0].split("/")[-1].split("-")[:-2]
    title = "-".join(title)
    print(title)
    # Set output
    if output is None:
        output = title + ".pdf"
    if os.path.isfile(output):
        print("Output {} already exists, skipping".format(output))
        return
    images = []
    bar = progressbar.ProgressBar(max_value=len(slides))
    with tempfile.TemporaryDirectory() as folder:
        # Download images
        print("Download images...")
        for i, m in bar(enumerate(slides)):
            filename = "{}{}.jpg".format(folder, i)
            urllib.request.urlretrieve(m, filename)
            images.append(filename)
        # Convert to PDF
        print("Converting to PDF...")
        call(["convert"] + images + [output])
        print("Wrote {}".format(output))

def downloadInput(path, output):
    # URL
    if path.startswith("http://"):
        downloadURL(path, output)
    # List of URLs in file
    elif os.path.isfile(path):        
        with open(path, "r") as f:
            for l in f:
                l = l.strip("\n\r")
                if l.startswith("http://"):
                    downloadURL(l)
if __name__ == "__main__":
    args = docopt(__doc__)
    if len(args["<input>"]) > 1:
        args["--output"] = None
    for path in args["<input>"]:
        downloadInput(path, args["--output"])
