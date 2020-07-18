#!/usr/bin/python
# coding:utf8

from .abstractmailstorage import *


class NoMailStorage(AbstractMailStorage):
    pass


RegisterMailStorage(NoMailStorage)
