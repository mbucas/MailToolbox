#!/usr/bin/python

import os
import sys
import argparse
from datetime import datetime

from logtext import logtext
from storage import imap_utf7


class RepairUTF7:

    def __init__(self):
        self.parameters = self.parseCommandLine()

    def parseCommandLine(self):
        parser = argparse.ArgumentParser(description="Maildir repair UTF7")
        parser.add_argument("--path", "-p", required=True, help="Path to repair")
        return parser.parse_args()

    def main(self):
        logtext.logText("Starting")

        alldirs = [
            (ldir[0].replace(os.sep, "/"))
            for ldir in os.walk(self.parameters.path)
            if ldir[0] != self.parameters.path
        ]

        for dir in alldirs:
            up = os.path.dirname(dir)
            base = os.path.basename(dir)
            newbase = imap_utf7.decode(base.encode("utf-8"))
            if base != newbase:
                print("Before : " + up + "/" + base)
                print("After  : " + up + "/" + newbase)

        logtext.logText("Finished")


if __name__ == "__main__":
    app = RepairUTF7()
    app.main()
