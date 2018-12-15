#!/usr/bin/env python
# -*- coding: utf-8 -*-
import imaplib
import email
import email.header
import arrow
from utils import loadConfig


def getMessage(imap, rv, n, full=False):
    rv, data = imap.fetch(n, "(BODY.PEEK[{}])".format("" if full else "HEADER"))
    return email.message_from_string(data[0][1].decode('utf-8'))


def getMessages(imap):
    rv, mailboxes = imap.list()
    rv, data = imap.select("INBOX")
    rv, data = imap.search(None, "(ALL)")
    messages = data[0].split()
    messages.reverse()
    return messages


def handleMessage(msg, match):
    date = arrow.Arrow.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(msg["Date"])))
    filename_base = "-".join([match[2], date.format("YYYY-MM-DD")])
    num = 0
    # Get files
    for i, part in enumerate(msg.walk()):
        if any([e in part.get_content_type() for e in match[3]]):
            filename = [filename_base]
            if num > 0:
                filename.append(str(num))
            filename = "-".join(filename)
            ext = part.get_filename().split(".")[-1].lower()
            filename = ".".join([filename, ext])
            with open(filename, "wb") as f:
                f.write(part.get_payload(decode=1))
            num = num + 1
            print("\tWrote", filename)


def main():
    config = loadConfig("imapfile.yaml")
    # Connect
    imap = imaplib.IMAP4_SSL(config["imap"][0])
    try:
        rv, data = imap.login(config["imap"][1], config["imap"][2])
    except imaplib.IMAP4.error:
        print("Login failed")
        exit(1)
    # Get messages
    messages = getMessages(imap)[:10]
    # Parse messages
    for k, n in enumerate(messages):
        print("{}/{} ({}%)".format(k, len(messages), round(k / len(messages) * 100)))
        msg = getMessage(imap, rv, n)
        subject, charset = email.header.decode_header(msg['Subject'])[0]
        match = next((x for x in config["headers"] if x[0] in msg["From"] and x[1] in msg["subject"]), False)
        if match is not False:
            # Handle message
            print(msg["subject"])
            handleMessage(getMessage(imap, rv, n, True), match)
    imap.close()
    imap.logout()

if __name__ == '__main__':
    main()
