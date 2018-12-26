from setuptools import setup
import time

with open('requirements.txt', 'r') as f:
    lines = f.readlines()
    requirements = [l.strip().strip('\n') for l in lines if l.strip() and not l.strip().startswith('#')]

scripts = ["trackpage", "bvresr", "imapfile", "gnucash2hledger", "zotexport", "radio", "readinglist2ebook", "text2ics", "slideshare", "beetsdiscogs", "flickrupload"]

setup(name="cpg314-scripts",
      version=int(time.time()),
      author="cpg314",
      license="MIT",
      packages=scripts + ["utils"],
      entry_points={"console_scripts": ["{0}={0}.{0}:main".format(s) for s in scripts]},
      install_requires=requirements,
      zip_safe=False)
