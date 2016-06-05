#!/usr/bin/python
# coding:utf8

import os

from ui import ui
from config import config
from storage import storage
from engine import engine
from transformations import transformations
from project import project


class MailToolboxStudio(object):
    appName = "MailToolboxStudio"

    def __init__(self):
        self.config = config.Config(self.appName)
        self.config.read()
        self.project = project.Project()
        if self.config.lastProject and os.path.exists(self.config.lastProject):
            self.project.loadFromFile(self.config.lastProject)

    def main(self):
        ui.show(self.appName, self.config, self.project)
        self.config.write()

if __name__ == "__main__":
    app = MailToolboxStudio()
    app.main()
