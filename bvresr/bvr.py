#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""bvr

Usage:
  bvr <filename>
  bvr <filename> [--page <page>]

"""
from docopt import docopt
import re
import itertools
import os
from subprocess import call
import tempfile
from tabulate import tabulate
import shutil


# Recursive mod 10
class Recursivemod(object):
    @staticmethod
    def generate(n):
        table = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5]
        matrix = [[0] * 10 for i in range(10)]
        for z in itertools.product(range(10), range(10)):
            i, j = z
            matrix[i][j] = table[(i + j) % 10]
        c = 0
        for nn in n:
            c = matrix[c][int(nn)]
        return (10 - c) % 10

    @staticmethod
    def verify(n):
        return Recursivemod.generate(n[:-1]) == int(n[-1])


# Tesseract OCR
def tesseract(filename, page=None):
    # Convert to tiff
    _, tiff = tempfile.mkstemp(suffix=".tiff")
    if page is not None:
        filename = filename + "[{}]".format(page - 1)
    call(["convert", "-density", "300", "-depth", "8", "-alpha", "off", filename, tiff])
    # Tesseract
    _, tesseract_out = tempfile.mkstemp(suffix=".txt")
    tesseract_out = "out.txt"
    with open(os.devnull, 'w') as null:
        call(["tesseract", tiff, tesseract_out.split(".")[0], "-l", "fra"], stdout=null, stderr=null)
    with open(tesseract_out, "r") as f:
        out = f.read()
    # Delete temporary files
    for f in [tiff, tesseract_out]:
        os.remove(f)
    return out


# Find BVR/ESR in text
def findBVR(text):
    results = []
    for m in re.findall(r"((\d{2})(0*)(\d*)(\d)>(\d*)\+ (\d*)>)", text):
        m = list(m)
        results.append({
            "type": types[m[1]],
            "amount": float(m[3]) / 100,
            "reference": m[5].lstrip("0"),
            "account": m[6],
            "coding": m[0],
            "checkums": Recursivemod.verify(m[5]) and Recursivemod.verify(''.join([m[i] for i in range(1, 5)]))
        })
    return results
# BVR/ESR types
types = {
    "01": "BVR/ESR CHF",
    "03": "BVR/ESR-Rbt CHF",
    "04": "BVR/ESR+ CHF",
    "11": "BVR/ESR CHF own account",
    "14": "BVR/ESR+ CHF own account",
    "21": "BVR/ESR EUR",
    "23": "BVR/ESR EUR own account",
    "31": "BVR/ESR+ EUR",
    "33": "BVR/ESR+ EUR own account"
}


def main():
    args = docopt(__doc__)
    filename = args["<filename>"]
    try:
        page = int(args["<page>"])
    except:
        page = None
    w, _ = shutil.get_terminal_size()
    # Check arguments
    if not os.path.isfile(filename):
        exit("File does not exist")
    # OCR
    print("Performing OCR...")
    out = tesseract(filename, page)
    # Display results
    print("BVR/ESR numbers found:")
    print("-" * w)
    for m in findBVR(out):
        table = [[k.capitalize() + ":", mm] for k, mm in m.items()]
        print(tabulate(table, tablefmt="plain"))
        print("-" * w)


if __name__ == "__main__":
    main()
