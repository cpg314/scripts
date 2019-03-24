#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""2factors2QR

Usage:
  2factors2QR <label> <username> <secret>
  2factors2QR <filename> [--combine]
"""

import qrcode # https://github.com/lincolnloop/python-qrcode
import qrcode.util
from docopt import docopt
from slugify import slugify
from tempfile import NamedTemporaryFile
import os
import subprocess

def generate(label, username, secret, output=None):
    url = "otpauth://totp/{}:{}?secret={}&issuer={}".format(label, username, secret.replace(" ", ""), label)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=5, border=2)
    qr.add_data(url)
    qr.make(fit=False)
    img = qr.make_image()
    if output is None:
        output = slugify(label)
    output += ".png"
    img.save(output)
    return output

args = docopt(__doc__)
if args["<filename>"] is not None:
    outputs = []
    with open(args["<filename>"], "r") as f:
        while True:
            s = f.readline()
            if not s:
                break
            s = s.split(",")
            if len(s) != 3:
                continue
            s[-1] = s[-1].strip()
            output = None
            if args["--combine"]:
                output = NamedTemporaryFile(delete=False).name
            outputs.append(generate(*s, output=output))
    if args["--combine"]:
        with open(os.devnull, 'w') as devnull:
            subprocess.call(["pdfjoin"] + outputs + ["--outfile", "2factor-codes.pdf"], stdout=devnull, stderr=devnull)
        for f in outputs:
            os.remove(f)        
else:
    generate(args["<label>"], args["<username>"], args["<secret>"])
