from termcolor import cprint
from os import getenv
import yaml


def bprint(s):
    cprint(s, "green", attrs=["bold"])


def loadConfig(filename):
    filename = getenv("HOME") + "/.config/" + filename
    with open(filename, "r") as f:
        return yaml.load(f)
