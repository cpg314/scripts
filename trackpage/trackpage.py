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

import asyncio
import aiohttp


def hashd(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def cleanup(folder, tracked):
    hashes = [hashd(x["url"]) for x in tracked]
    for f in os.listdir(folder):
        if f not in hashes and f != "trackpage.yaml":
            os.remove(folder + f)


def displayDiff(newhtml, oldhtml, ter):
    out = []
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
                out.append(ter.green(l))
            elif l[0] == '-':
                out.append(ter.red(l))
            else:
                out.append(l)
    else:
        out.append("No changes")
    return out


async def checkPage(page, folder, ter):
    out = []
    url = page["url"]
    out.append(ter.bold("Checking " + url))
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30, headers={"User-Agent": UserAgent(fallback='Mozilla/5.0 (compatible; Googlebot/2.1;').random}) as r:
                resp = await r.read()
                parsed = BeautifulSoup(resp, 'html.parser')
        urlhash = hashd(url)
        filename = folder + urlhash
        if "selector" in page:
            parsed = parsed.select(page["selector"])[0]
        if "textonly" in page and page["textonly"]:
            parsed = parsed.text
        html = str(parsed)
        if not os.path.isfile(filename):
            out.append( "New URL")
        else:
            with open(filename, "r") as f:
                oldhtml = f.read()
                out = out + displayDiff(html, oldhtml, ter)
        with open(filename, "w") as f:
            f.write(str(html))
    except Exception as e:
        out.append("Error: {}".format(e))
    print("\n".join(out))

def main():
    folder = os.getenv("HOME") + "/.config/trackpage/"
    tracked = loadConfig("trackpage/trackpage.yaml")
    ter = Terminal()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*(checkPage(page, folder, ter) for page in tracked)))
    cleanup(folder, tracked)


if __name__ == "__main__":
    main()
