#!/usr/bin/python
# coding:utf8

from mailbox import Mailbox
from email.message import Message

from abstractmailstorage import *


class DumpMailbox(Mailbox):
    """
        Store all mails in a file, for tests purposes
        Ignores any reads
    """
    def __init__(self, path, factory=None, create=True):
        Mailbox.__init__(self, path, factory, create)
        self.file = open(self._path, "wb")

    def add(self, message):
        self.file.write(message)

    def remove(self, key):
        pass

    def get_message(self, key):
        pass

    def get_string(self, key):
        pass

    def get_file(self, key):
        pass


class DumpMailStorage(AbstractMailStorage):
    """
        Store all mails in a file, for tests purposes
        Ignores any reads
    """

    def __init__(self, properties):
        AbstractMailStorage.__init__(self, properties)
        self.mailbox = None

    def getFolders(self):
        return ['/']

    def getFolderMailbox(self, folderName, create=True):
        if not self.mailbox:
            self.mailbox = DumpMailbox(self.properties["path"], None, True)
        return self.mailbox

    def createFolder(self, folderName, includingPath=False):
        pass

    def deleteFolder(self, folderName, includingChildren=False):
        pass

    def hasFolder(self, folderName):
        return True

RegisterMailStorage(DumpMailStorage)
