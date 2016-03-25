#!/usr/bin/python
# coding:utf8

import sys
import argparse

from config import config
from storage import storage
from engine import engine
from transformations import transformations
from project import project


def show(text):
    print text


class MailToolboxRunner(object):
    appName = "MailToolboxRunner"

    def __init__(self):
        self.config = config.Config(self.appName)
        self.config.read()
        self.project = project.Project()
        self.parameters = self.parseCommandLine()
        self.project.loadFromFile(self.parameters.project)

    def parseCommandLine(self):
        parser = argparse.ArgumentParser(
            description='Execute projects made with MailToolboxStudio'
        )
        parser.add_argument(
            '--project',
            '-p',
            required=True,
            help='File name of the project'
        )
        return parser.parse_args()

    def main(self):
        runnerEngine = engine.Engine(self.project, folderCallback=show)
        runnerEngine.run()

if __name__ == "__main__":
    app = MailToolboxRunner()
    app.main()
