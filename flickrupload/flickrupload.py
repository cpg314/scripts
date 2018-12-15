#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""flickrupload

Usage:
  flickrupload [options] <folder> <key> <secret>

  --shotwell=<library>       Export photo sets from Shotwell library
  --check-duplicates         Check for duplicates remotely before uploading
  --resize=<size>            Resize pictures to a maximum of size x size pixels

"""
from docopt import docopt
import flickrapi
import glob
import dataset
import os
from pprint import pprint
import pickle
import progressbar
from multiprocessing.dummy import Pool as ThreadPool
import tempfile
import hashlib
from PIL import Image
import piexif

home = os.getenv("HOME")


def hashFile(filename):  # https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
    sha1 = hashlib.sha1()
    if not os.path.isfile(filename):
        return None
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(128 * sha1.block_size), b""):
            sha1.update(chunk)
            return sha1.hexdigest()


# Remove all sets from Flickr
def removeSets():
    for s in flickr.photosets.getList().find("photosets"):
        flickr.photosets.delete(photoset_id=s.get("id"))


def addSets(results, library, flickr):
    # Shotwell
    db = dataset.connect("sqlite:///{}/.local/share/shotwell/data/photo.db".format(home), engine_kwargs={"connect_args": {"check_same_thread": False}})
    if library[-1] != "/":
        library = library + "/"
    # Add set for each event
    for e in db["EventTable"].all():
        pprint(e)
        photos = list(db["PhotoTable"].find(event_id=e["id"]))
        if len(photos) == 0 or e["name"] is None:
            continue
        if e["id"] in results.keys():
            # Already imported
            continue
        primary = hashFile(photos[0]["filename"])
        if primary in results.keys():
            print("Create set with {} photos".format(len(photos)))
            resp = flickr.photosets.create(title=e["name"], primary_photo_id=results[primary]["flickr_id"], description=e["id"], format="parsed-json")
            photoset = resp["photoset"]["id"]
            results[e["id"]] = {"flickr_photoset": photoset}
            # Add other photos
            for i, p in enumerate(photos):
                if i == 0:
                    continue
                print(p["filename"])
                filehash = hashFile(p["filename"])
                if filehash in results.keys():
                    try:
                        resp = flickr.photosets.addPhoto(photoset_id=photoset, photo_id=results[filehash]["flickr_id"])
                    except Exception as e:
                        print(e)
                else:
                    print("Not found")
        else:
            print("Cannot create set")
        print("-" * 10)


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


# Upload photo
def uploadPhoto(filename, results, flickr, checkDuplicates=False, resize=None):
    filehash = hashFile(filename)
    # Check if already uploaded
    if filehash in results.keys():
        return None
    if checkDuplicates and int(flickr.photos.search(user_id="me", text=filename).find("photos").get("total")) > 0:
        return None
    # Process
    try:
        photo = None
        if resize is not None:
            with tempfile.NamedTemporaryFile() as f:
                img = Image.open(filename)
                img.thumbnail((resize, resize))
                try:
                    # Preserve EXIF
                    exif_dict = piexif.load(img.info["exif"])
                    exif_bytes = piexif.dump(exif_dict)
                    img.save(f.name, "JPEG", exif=exif_bytes)
                except:
                    # No EXIF available
                    img.save(f.name, "JPEG")
                    # Get date from Shotwell
                    # photo = db["PhotoTable"].find_one(filename=library + filename)
                    # if photo is not None:
                    #     t = photo["exposure_time"]
                    #     os.utime(f.name, (t, t))
                photo = flickr.upload(f.name, description=filename)
        else:
            photo = flickr.upload(filename, description=filename)
        return filehash, {"flickr_id": photo.find("photoid").text}
    except Exception as e:
        print(filename)
        print("Error:", e)
        return None


# Upload photos
def uploadPhotos(photos, results, flickr, checkDuplicates=False, resize=None):
    # Progress bar
    bar = progressbar.ProgressBar(max_value=len(photos))
    bar.start()
    # Callback

    def callback(r, results):
        # Update progress
        bar.update(bar.value + 1)
        if r is None:
            return
        filehash, res = r
        results[filehash] = res
        return
    # Threading
    pool = ThreadPool(4)
    for p in photos:
        pool.apply_async(uploadPhoto,
                         args=[p, results, flickr, checkDuplicates, resize],
                         callback=lambda x: callback(x, results))
    pool.close()
    pool.join()
    bar.finish()

def main():
    args = docopt(__doc__)
    # Initialize Flickr API
    flickr = flickrapi.FlickrAPI(args["<key>"], args["<secret>"])
    flickr.authenticate_via_browser(perms="write")
    # Get photos
    photos = list(glob.iglob(args["<folder>"] + "/**/*.*", recursive=True))
    print("{} photos found".format(len(photos)))
    resize = args["--resize"]
    if resize is not None:
        resize = int(resize)
    # Keep track of uploaded pictures
    results = {}
    resultsFile = home + "/.cache/flickr"
    if os.path.isfile(resultsFile):
        results = pickle.load(open(resultsFile, "rb"))
    # Upload pictures
    uploadPhotos(photos, results, flickr, args["--check-duplicates"], resize)
    # Add sets from Shotwell
    if args["--shotwell"] is not None:
        addSets(results, args["--shotwell"], flickr)
    pickle.dump(results, open(resultsFile, "wb"))


if __name__ == "__main__":
    main()
