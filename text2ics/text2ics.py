#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""text2ics

Usage:
  text2ics <input>
  text2ics <input> [--out <file>]

"""
import regex
from icalendar import Calendar, Event
import arrow
from docopt import docopt
from dateutil import tz


def convertAMPM(s):
    def repl(x):
        h = int(x.group(1))
        if x.group(3).lower() == "pm" and h != 12:
            h = 12 + h
        return "{}:{}".format(h, x.group(2))
    return regex.sub("(\d+):(\d+) (am|pm)", repl, s, flags=regex.IGNORECASE)


def convert(s):
    """
    Convert string to icalendar
    """
    cal = Calendar()
    # String normalization
    s = s.replace("–", "-")
    s = convertAMPM(s)
    # Parse lines
    for l in s.split('\n'):
        l = l.strip()
        if len(l) == 0:
            continue
        try:
            # Day
            formats = ["MMMM D, YYYY", "dddd MMMM D, YYYY", "dddd, D MMMM", "dddd D MMMM", "dddd MMMM D, YYYY", "dddd, MMMM Do, YYYY"]
            date = arrow.get(l, formats)
            date = date.replace(year=arrow.now().year, tzinfo=tz.tzlocal())
        except:
            # Event
            hours = regex.search("(\s*(\d+)(?:h|:)(\d+)\s*-*)+ (.*)", l)
            if hours is None:
                continue
            event = Event()
            event["summary"] = hours.captures(4)[0].strip()
            hours = [[int(hours.captures(j)[i]) for j in range(2, 3 + 1)] for i in range(0, len(hours.captures(2)))]
            # Set times
            dt = {}
            for i, t in enumerate(["dtstart", "dtend"]):
                if i < len(hours):
                    dt[t] = date.replace(hour=hours[i][0], minute=hours[i][1])
                else:
                    #dt[t] = dt["dtstart"].replace(hours=+i)  # Default duration
                    dt[t] = dt["dtstart"].replace(minutes=+30)  # Default duration
            # Format times
            for t in ["dtstart", "dtend"]:
                event.add(t, dt[t].to("utc").datetime)
            cal.add_component(event)
    return cal.to_ical().decode("utf-8")


def main():
    arguments = docopt(__doc__)
    with open(arguments["<input>"], "r") as f:
        ics = convert(f.read())
    output = arguments["<file>"]
    if output is None:  # Console output
        print(ics)
    else:  # File output
        with open(output, "w") as f:
            f.write(ics)


if __name__ == '__main__':
    main()
