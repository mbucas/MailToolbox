#!/usr/bin/python
# coding:utf8

from mailbox import Mailbox
from email.message import Message

from .abstractmailstorage import *


class DumpMailbox(Mailbox):
    """
        Store all mails in a file, for tests purposes
        Ignores any reads
    """
    def __init__(self, path, factory=None, create=True, file=None):
        Mailbox.__init__(self, path, factory, create)
        self.file = file

    def add(self, message):
        if hasattr(message, "dump"):
            try:
                self.file.write(message.dump)
            except Exception as e:
                self.file.write(
                    message.dump.encode('iso-8859-15', errors='ignore')
                )
        else:
            self.file.write(('-' * 80) + '\n' + message.as_string() + '\n\n')

    def __len__(self):
        """Return a count of messages in the mailbox."""
        return 0

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

    def openSession(self):
        self.file = open(self.properties["path"], "wb")

    def closeSession(self):
        self.file.close()

    def getFolders(self):
        return ['/']

    def getFolderMailbox(self, folderName, create=True):
        if not self.mailbox:
            self.mailbox = DumpMailbox(
                self.properties["path"],
                None,
                True,
                self.file
            )
        return self.mailbox

    def createFolder(self, folderName, includingPath=False):
        pass

    def deleteFolder(self, folderName, includingChildren=False):
        pass

    def hasFolder(self, folderName):
        return True


RegisterMailStorage(DumpMailStorage)
