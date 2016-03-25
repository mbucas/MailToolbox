#!/usr/bin/python
# coding:utf8

from mailbox import Mailbox
from email.message import Message

from abstractmailstorage import *


class OutlookMailbox(Mailbox):
    """
        Outlook Mail Storage reader and writer
        For .PST files
    """

    def __init__(self, path, folder, mailStorage):
        """Initialize a Maildir instance."""
        Mailbox.__init__(self, path, None, False)
        self.folder = folder
        self.mailStorage = mailStorage

    def add(self, message):
        """Add message and return assigned key."""
        raise NotImplementedError('Method is not implemented yet')

    def iterkeys(self):
        """Return an iterator over keys."""
        for i in range(0):
            entry = i
            if entry:
                yield entry

    def remove(self, key):
        """Remove the keyed message; raise KeyError if it doesn't exist."""
        raise NotImplementedError('Method is not implemented yet')

    def get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        message = Message()
        message.set_payload("Outlook message " + key)
        # TODO status
        setContext(message, key, 'read', 'add')
        return message


class OutlookMailStorage(AbstractMailStorage):
    """
        Outlook Mail Storage reader and writer
        For .PST files
    """

    def __init__(self, properties):
        AbstractMailStorage.__init__(self, properties)
        self.expectedProperties.append({
            'key': 'user',
            'label': 'User',
            'content': 'string',
            'desc': 'Outlook User',
        })
        self.expectedProperties.append({
            'key': 'password',
            'label': 'Password',
            'content': 'hidden',
            'desc': 'Outlook Password',
        })

    def openSession(self):
        pass

    def closeSession(self):
        pass

    def getFolders(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def getFolderMailbox(self, folderName, create=True):
        raise NotImplementedError('Method must be implemented by subclass')

    def createFolder(self, folderName, includingPath=False):
        raise NotImplementedError('Method must be implemented by subclass')

    def deleteFolder(self, folderName, includingChildren=False):
        raise NotImplementedError('Method must be implemented by subclass')

    def hasFolder(self, folderName):
        raise NotImplementedError('Method must be implemented by subclass')

RegisterMailStorage(OutlookMailStorage)
