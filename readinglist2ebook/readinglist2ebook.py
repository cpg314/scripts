#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""readinglist2ebook

Usage:
  readinglist2ebook login <server> <user> <token>
  readinglist2ebook export [--mobi] [--limit=<n>]
  readinglist2ebook toKindle
"""
from ebooklib import epub
import os
from urllib.parse import urlparse, urljoin
import hashlib
import requests
from bs4 import BeautifulSoup
from shutil import copyfile, rmtree
from subprocess import DEVNULL, STDOUT, call
from utils import bprint
import pickle
import warnings
from docopt import docopt
from getpass import getuser
from readability import Document

warnings.filterwarnings("ignore")


def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def getFeed(server, user, token):
    if server == "pocket":
        url = "https://getpocket.com/users/{}/feed/unread".format(token)
    else:
        url = "{}/u/{}/?feed&type=home&user_id=1&token={}".format(server, user, token)
    rss = requests.get(url).text
    rss = BeautifulSoup(rss, "html.parser")
    feed = []
    for f in rss.findAll("item"):
        content = None
        try:
            content = f.find("description").text
        except:
            pass
        feed.append({
            "title": f.find("title").text,
            "url": f.find("guid").text,
            "hash": sha1(f.find("guid").text),
            "content": content
        })
    return feed


def cleanup(unread, path):
    hashes = [a["hash"] for a in unread]
    for d in os.listdir(path):
        if d not in hashes and os.path.isdir(path + d):
            print("Remove", d)
            rmtree(path + d)


def addImages(parsed, path, book, url):
    for img in parsed.findAll("img"):
        if not img.has_attr("src"):
            img["src"] = img["data-srcset"]
        uid = sha1(img["src"])
        ext = os.path.splitext(urlparse(img["src"]).path)[1]
        filename = path + uid + ext
        src = img["src"]
        # Check URL
        if "http" not in src:
            src = urljoin(url, src)
        try:
            if not os.path.isfile(filename):  # File not already downloaded
                response = requests.get(src, stream=True)
                print("\tDownloading", src)
                if response.ok:
                    # Write file
                    with open(filename, 'wb') as h:
                        for b in response.iter_content(1024):
                            h.write(b)
                else:
                    raise Exception()
            # Read file
            with open(filename, "rb") as f:
                # Add image to book
                book.add_item(epub.EpubItem(content=f.read(), file_name=uid + ext))
                # Edit image url in epub
                img["src"] = uid + ext
        except Exception as e:
            print("\tError retrieving image")
            pass
    return parsed


def fetchFullContents(url, path):
    contentsFile = path + "contents.txt"
    if not os.path.isfile(contentsFile):
        r = requests.get(url)
        url = r.url  # Update url
        with open(contentsFile, "w") as f:
            f.write(Document(r.text).summary(html_partial=True))
    with open(contentsFile, "r") as f:
        return f.read(), url


def convertArticle(a, book, path):
    c = epub.EpubHtml(title=a["title"], file_name=a["hash"] + ".xhtml")
    # Cache folder
    path = "".join([path, a["hash"], "/"])
    if not os.path.exists(path):
        os.mkdir(path)
    # Fetch full contents
    if a["content"] is None:
        try:
            a["content"], a["url"] = fetchFullContents(a["url"], path)
        except:
            return None
    parsed = BeautifulSoup(a["content"], "lxml")
    # Add images
    parsed = addImages(parsed, path, book, a["url"])
    # Estimate reading time
    readingTime = round(len(parsed.text.split()) / 250)
    c.title = "{} ({} min)".format(c.title, readingTime)
    # Add title
    c.content = "<h1>" + a["title"] + "</h1>" + str(parsed)
    return c


def copyToKindle(filename):
    kindlePath = "/run/media/{}/Kindle/documents/".format(getuser())
    if os.path.exists(kindlePath):
        hanFile = kindlePath + filename + ".han"
        if os.path.isfile(hanFile):
            os.remove(hanFile)
        copyfile("export.mobi", kindlePath + filename + ".mobi")
        print("Done")
    else:
        print("Kindle not connected")


def convertMOBI(input, output):
    call(["kindlegen", input, "-c2", "-o", output], stdout=DEVNULL, stderr=STDOUT)


def main():
    args = docopt(__doc__)
    path = os.path.expanduser("~")
    config = path + "/.config/readinglist2ebook"
    path = path + "/readinglist2ebook/"
    # Copy to Kindle
    if args["toKindle"]:
        bprint("Copying to Kindle...")
        copyToKindle("export")
        exit()
    # Login
    if args["login"]:
        with open(config, "wb") as f:
            pickle.dump({k: args[k] for k in ["<server>", "<user>", "<token>"]}, f)
        exit()
    # Export
    if not os.path.isfile(config):
        print("Not logged in.")
        exit(1)
    with open(config, "rb") as f:
        config = pickle.load(f)
    # Create downloads folder
    if not os.path.exists(path):
        os.mkdir(path)
    # Get feed
    bprint("Getting feed...")
    unread = getFeed(config["<server>"], config["<user>"], config["<token>"])
    if args["--limit"] is not None:
        unread = unread[:int(args["--limit"])]
    # Generate epub
    bprint("Generating epub...")
    book = epub.EpubBook()
    book.set_title("Reading list export")
    book.set_language("en")
    chapters = []
    for i, a in enumerate(unread):
        print("{}/{}: {}".format(i + 1, len(unread), a["title"]))
        c = convertArticle(a, book, path)
        if c is not None:
            book.add_item(c)
            chapters.append(c)
            book.toc.append(c)
    # Create epub
    bprint("Creating epub...")
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters
    epub.write_epub("export.epub", book, {})
    # Convert to MOBI
    if args["--mobi"]:
        bprint("Converting to MOBI...")
        convertMOBI("export.epub", "export.mobi")
    # Cleanup old downloads
    bprint("Cleanup old downloads...")
    cleanup(unread, path)


if __name__ == '__main__':
    main()
