#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""beets-discogs

Usage:
  beets-discogs [options] <library> <token>

  --ask      Ask for releases that cannot be found.
  --verbose

"""
from docopt import docopt
from beets import library
import discogs_client
from ratelimit import rate_limited
import requests
from bs4 import BeautifulSoup
import os
import sys
import logging
import progressbar

logger = logging.getLogger()
logger.setLevel(logging.INFO)
form = logging.Formatter('%(asctime)s - %(message)s', "%Y-%m-%d %H:%M:%S")
logger.addHandler(logging.StreamHandler(sys.stdout))


# Rate limiting for discogs
@rate_limited(period=55, every=60.0)
def ratelimit():
    return


def addRelease(releaseid, folder, user):
    ratelimit()
    try:
        folder.add(releaseid)
    except:
        c = folder.client
        c._post("{}/users/{username}/collection/folders/{folder_id}/releases/{release_id}".format(c._base_url, username=user.username, folder_id=folder.id, release_id=releaseid), {})


@rate_limited(period=250, every=1.0)
def searchMusicBrainz(albumid, discogs):
    # The API doesn't provide access to the external links field, so we parse the page
    r = requests.get("https://musicbrainz.org/release/{}/details".format(albumid))
    parsed = BeautifulSoup(r.text, 'html.parser')
    res = parsed.select(".discogs-favicon")
    if len(res) > 0:
        logger.debug("Found cross-reference on Musicbrainz")
        res = res[0].find("a")["href"].replace("https://www.discogs.com/", "")
        res = res.split("/")
        if res[0] == "release":
            return int(res[1])
        else:
            ratelimit()
            return int(discogs.master(res[1]).main_release.id)
    return None


def searchDiscogs(a, discogs):
    ratelimit()
    results = discogs.search(artist=a.albumartist, release_title=a.album, type='master')
    if len(results) == 0:
        return None
    logger.debug("Found on Discogs")
    ratelimit()
    return int(results[0].main_release.id)


def search(a, discogs, use_cache=True, ask=False):
    if use_cache and "discogs_id" in a.keys() and a["discogs_id"] is not None:
        logger.debug("Getting from cache")
        return int(a["discogs_id"])
    if len(a.albumartist + a.album + a.mb_albumid) == 0:
        logger.debug("No fields")
        return None
    # First attempt: Musicbrainz cross-referencing
    releaseid = None
    if len(a.mb_albumid) > 0:
        releaseid = searchMusicBrainz(a.mb_albumid, discogs)
    # Second attempt: Search on Discogs
    if releaseid is None:
        releaseid = searchDiscogs(a, discogs)
    # Third attempt: ask
    if ask and releaseid is None:
        print(a.albumartist, a.album, a.year)
        releaseid = input("Enter release url: ")
        if len(releaseid) == 0:
            releaseid = None
        else:
            releaseid = releaseid.split("release/")[1]
            releaseid = int(releaseid)
    # Store Discogs id
    if releaseid is not None:
        a["discogs_id"] = releaseid
        a.store()
    return releaseid


def main():
    args = docopt(__doc__)
    filename = args["<library>"]
    if not os.path.isfile(filename):
        exit("Library not found")
    if args["--verbose"]:
        logger.setLevel(logging.DEBUG)
    # Discogs
    discogs = discogs_client.Client("BeetsImporter/0.1", user_token=args["<token>"])
    # Beets
    beetsLib = library.Library(filename)
    albums = beetsLib.albums()
    # Get collection
    print("Getting collection information from Discogs...")
    me = discogs.identity()
    collection = [r.id for r in me.collection_folders[0].releases]
    print("{} items in collection".format(len(collection)))
    folder = [f for f in me.collection_folders if f.name == "Uncategorized"][0]
    # Search and add albums
    bar = progressbar.ProgressBar(max_value=len(albums))
    for a in bar(albums):
        logging.debug(a)
        releaseid = search(a, discogs, True, args["--ask"])
        if releaseid is not None and releaseid not in collection:
            addRelease(releaseid, folder, me)

if __name__ == "__main__":
    main()
