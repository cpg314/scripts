# -*- coding: utf-8 -*-
"""zotexport

Usage:
  zotexport login <userID> <key>
  zotexport list
  zotexport export <collection> [--recursive]

"""
from pyzotero import zotero
import os
import shutil
from slugify import slugify
from docopt import docopt
import pickle

# Get Zotero storage folder


def getzotStorage():
    zotStorage = os.path.expanduser("~") + "/.zotero/zotero/"
    for d in os.listdir(zotStorage):
        if ".ini" not in d:
            return zotStorage + d + "/zotero/storage/"


def displayCollections(c, i=0, parent=False):
    for cc in c:
        if cc["data"]["parentCollection"] == parent:
            print("{}- {} ({})".format('\t' * i, cc["data"]["name"], cc["key"]))
            displayCollections(c, i + 1, cc["key"])


def exportAttachments(items, basename):
    count = 0
    # Export attachments
    for a in items:
        if a["data"]["itemType"] == "attachment":
            ext = os.path.splitext(a["data"]["filename"])[1]
            path = getzotStorage() + a["key"] + "/"
            for f in os.listdir(path):
                if ext in f:
                    shutil.copyfile(path + f, basename + ("-{}".format(count) if count > 0 else "") + ext)
                    count = count + 1


def exportCollection(zot, c, recursive=False, folder=""):
    print("Export collection", c["data"]["name"])
    folder = folder + slugify(c["data"]["name"]) + "/"
    if not os.path.isdir(folder):
        os.mkdir(folder)
    items = zot.collection_items(c["key"])
    for i in items:        
        if i["data"]["itemType"] != "attachment":
            if "title" not in i["data"]:
                continue
            try:
                print(" " * 5, i["data"]["title"])
                filename = u"{}-{}-{}".format(
                    i["data"]["date"].replace("/", "-"),
                    "".join([a["lastName"] for a in i["data"]["creators"]]),
                    slugify(i["data"]["title"]))
                exportAttachments([a for a in items if "parentItem" in a["data"] and a["data"]["parentItem"] == i["key"]], folder + filename)
            except:
                print("\tError")
    # Recurse on children
    if recursive:
        for cc in zot.collections_sub(c["key"]):
            exportCollection(cc, True, folder)


def main():
    args = docopt(__doc__)
    configFile = getzotStorage() + "/.zotexport"
    if args["login"]:
        pickle.dump({k: args[k] for k in ["<userID>", "<key>"]}, open(configFile, "wb"))
    if not os.path.isfile(configFile):
        print("Not logged in.")
        exit(1)
    config = pickle.load(open(configFile, "rb"))
    zot = zotero.Zotero(config["<userID>"], "user", config["<key>"])
    # Display
    if args["list"]:
        print("Getting list of collections...")
        # displayCollections(zot.collections_top()) #too slow
        displayCollections(zot.all_collections())
    elif args["export"]:
        exportCollection(zot, zot.collection(args["<collection>"]), args["--recursive"])

if __name__ == '__main__':
    main()
