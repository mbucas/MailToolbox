#!/usr/bin/python
# coding:utf8

from mailbox import Mailbox
from email.message import Message

from abstractmailstorage import *


class FakeMailbox(Mailbox):
    """
        Create fake mails using a Python script, for tests purposes
        Ignores any writes
        (Like /dev/zero for reading and /dev/null for writing)
    """

    def __init__(self, path, factory=None, create=True, fakeSpec=None, folderName="/"):
        Mailbox.__init__(self, path, factory, create)

        try:
            import fakeSpec
            self._messages = fakeSpec.fakeMailBuilder()
        except ImportError:
            self._messages = {}
            for i in range(10):
                m = Message()
                m.set_payload("Fake message " + str(i))
                self._messages[i] = m

        self.iterkeys = self._messages.iterkeys
        self.has_key = self._messages.has_key
        self.__len__ = self._messages.__len__

    def add(self, message):
        pass

    def remove(self, key):
        pass

    def get_message(self, key):
        if key in self._messages:
            message = self._messages[key]
        else:
            message = None
        # TODO status
        setContext(message, key, 'read', 'add')
        return message

    def get_string(self, key):
        return self.get_message(key)

    def get_file(self, key):
        return self.get_message(key)


class FakeMailStorage(AbstractMailStorage):
    """
        Create fake mails based on data files, for tests purposes
        Ignores any writes
        (Like /dev/zero for reading and /dev/null for writing)

        Expected options:
         - path: passed to Mailbox base class, must be a string, unused
         - fakeSpec: optional, Python script that creates fake messages
    """

    def getFolders(self):
        return ['/']

    def getFolderMailbox(self, folderName, create=True):
        return FakeMailbox(
            self.properties["path"],
            None,
            True,
            self.properties["fakeSpec"],
            folderName
        )

    def createFolder(self, folderName, includingPath=False):
        pass

    def deleteFolder(self, folderName, includingChildren=False):
        pass

    def hasFolder(self, folderName):
        return folderName == "/"

    def serializeToXml(self):
        raise NotImplementedError('Method is not implemented yet')

RegisterMailStorage(FakeMailStorage)
