#!/usr/bin/python
# coding:utf8

from mailbox import Mailbox
from email.message import Message

from abstractmailstorage import *


class ImapMailbox(Mailbox):
    """
        Imap Mail Storage reader and writer
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
        """ Return a Message representation or raise a KeyError."""
        message = Message()
        message.set_payload("IMAP message " + key)
        # TODO status
        setContext(message, key, 'read', 'add')
        return message


class ImapMailStorage(AbstractMailStorage):
    """
        Imap Mail Storage reader and writer
    """

    def __init__(self, properties):
        AbstractMailStorage.__init__(self, properties)
        self.expected_properties.append({
            'key': 'user',
            'label': 'User',
            'content': 'string',
            'desc': 'IMAP User',
        })
        self.expected_properties.append({
            'key': 'password',
            'label': 'Password',
            'content': 'hidden',
            'desc': 'IMAP Password',
        })

    def openSession(self):
        raise NotImplementedError('Not implemented as of yet')

    def closeSession(self):
        raise NotImplementedError('Not implemented as of yet')

    def getFolders(self):
        raise NotImplementedError('Not implemented as of yet')

    def getFolderMailbox(self, folderName, create=True):
        raise NotImplementedError('Not implemented as of yet')

    def createFolder(self, folderName, includingPath=False):
        raise NotImplementedError('Not implemented as of yet')

    def deleteFolder(self, folderName, includingChildren=False):
        raise NotImplementedError('Not implemented as of yet')

    def hasFolder(self, folderName):
        raise NotImplementedError('Not implemented as of yet')


RegisterMailStorage(ImapMailStorage)
