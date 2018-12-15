#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from blessings import Terminal
import difflib
import hashlib
import os
from utils import loadConfig
from fake_useragent import UserAgent


def hashd(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def cleanup(folder, tracked):
    hashes = [hashd(x["url"]) for x in tracked]
    for f in os.listdir(folder):
        if f not in hashes and f != "trackpage.yaml":
            os.remove(folder + f)


def displayDiff(newhtml, oldhtml, ter):
    diff = list(difflib.unified_diff(oldhtml.splitlines(), newhtml.splitlines()))
    if len(diff) > 0:
        for l in diff:
            try:
                l = l.decode("utf-8")
            except:
                pass
            if l[:3] == "+++" or l[:3] == "---" or l[:2] == "@@":
                continue
            if l[0] == '+':
                print(ter.green(l))
            elif l[0] == '-':
                print(ter.red(l))
            else:
                print(l)
    else:
        print("No changes")


def checkPage(page, folder, ter):
    url = page["url"]
    print(ter.bold("Checking " + url))
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": UserAgent(fallback='Mozilla/5.0 (compatible; Googlebot/2.1;').random})
        parsed = BeautifulSoup(r.text, 'html.parser')
        urlhash = hashd(url)
        filename = folder + urlhash
        if "selector" in page:
            parsed = parsed.select(page["selector"])[0]
        html = str(parsed)
        if not os.path.isfile(filename):
            print("New URL")
        else:
            with open(filename, "r") as f:
                oldhtml = f.read()
                displayDiff(html, oldhtml, ter)
        with open(filename, "w") as f:
            f.write(str(html))
    except Exception as e:
        print("Error", e)


def main():
    folder = os.getenv("HOME") + "/.config/trackpage/"
    tracked = loadConfig("trackpage/trackpage.yaml")
    ter = Terminal()
    for page in tracked:
        checkPage(page, folder, ter)
    cleanup(folder, tracked)


if __name__ == "__main__":
    main()
