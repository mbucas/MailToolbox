#!/usr/bin/env python
# coding:utf8

import os
from ConfigParser import *


class Config():
    """
    Config

    Contains
        - Main section
            - Last project
            - Last session main window size and position

    It's saved as an .ini file in user home directory.
    """

    configAttributes = ['lastProject', 'windowState', 'windowPos', 'windowSize']

    def __init__(self, name):
        self.parser = ConfigParser()
        self.name = name
        self.configFile = os.path.join(os.path.expanduser('~'), '.' + self.name + '.ini')
        for attribute in self.configAttributes:
            setattr(self, attribute, None)

    def read(self):
        if os.path.isfile(self.configFile):
            self.parser.read(self.configFile)

            if self.parser.has_section(self.name):
                for attribute in self.configAttributes:
                    if self.parser.has_option(self.name, attribute):
                        setattr(self, attribute, self.parser.get(self.name, attribute))

    def write(self):
        if not self.parser.has_section(self.name):
            self.parser.add_section(self.name)

        for attribute in self.configAttributes:
            if hasattr(self, attribute) and getattr(self, attribute):
                self.parser.set(self.name, attribute, getattr(self, attribute))

        self.parser.write(open(self.configFile, 'wb'))
