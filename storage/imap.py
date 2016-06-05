#!/usr/bin/python
# coding:utf8

from mailbox import Mailbox
from email import message_from_string
from email.message import Message
import imaplib
import re
import time

from abstractmailstorage import *
import imap_utf7


class ImapMailbox(Mailbox):
    """
        Imap Mail Storage reader and writer
    """

    def __init__(self, path, folder, mailStorage):
        """Initialize a Maildir instance."""
        Mailbox.__init__(self, path, None, False)
        self.folder = folder
        self.mailStorage = mailStorage
        self.mailStorage.session.select(self.mailStorage.toIMAP(folder))

    def add(self, message):
        """Add message and return assigned key."""
        self.mailStorage.session.append(
            self.mailStorage.toIMAP(self.folder),
            '',
            # TODO Time should be from the original message
            imaplib.Time2Internaldate(time.time()),
            message.as_string()
        )

    def iterkeys(self):
        """Return an iterator over keys."""
        status, [msg_ids] = self.mailStorage.session.search(None, 'ALL')
        # TODO Check status
        for id in msg_ids.split():
            if id:
                yield id

    def remove(self, key):
        """Remove the keyed message; raise KeyError if it doesn't exist."""
        raise NotImplementedError('Method is not implemented yet')

    def get_message(self, key):
        """ Return a Message representation or raise a KeyError."""
        typ, msg_data = self.mailStorage.session.fetch(key, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                message = message_from_string(response_part[1])
        # TODO check for errors
        # TODO status
        setContext(message, key, 'read', 'add')
        return message


class ImapMailStorage(AbstractMailStorage):
    """
        Imap Mail Storage reader and writer
    """

    def __init__(self, properties):
        AbstractMailStorage.__init__(self, properties)
        self.expectedProperties.append({
            'key': 'user',
            'label': 'User',
            'content': 'string',
            'desc': 'IMAP User',
        })
        self.expectedProperties.append({
            'key': 'password',
            'label': 'Password',
            'content': 'hidden',
            'desc': 'IMAP Password',
        })
        self.expectedProperties.append({
            'key': 'ssl',
            'label': 'Use SSL',
            'content': 'list',
            'desc': 'Use SSL to connect to IMAP server',
            'values': ['Yes', 'No'],
        })

    def openSession(self):
        IMAPserver = self.properties['path'].split('://')[1]
        if self.properties['ssl'] == 'Yes':
            self.session = imaplib.IMAP4_SSL(IMAPserver)
        else:
            self.session = imaplib.IMAP4(IMAPserver)
        self.session.login(self.properties['user'], self.properties['password'])
        self.folders = None
        self.IMAPFolders = {}

    def closeSession(self):
        self.session.logout()

    def fromIMAP(self, folder):
        out = '/' + imap_utf7.decode(folder).encode('utf8')
        self.IMAPFolders[out] = folder
        return out

    def toIMAP(self, folder):
        if folder in self.IMAPFolders:
            return self.IMAPFolders[folder]
        else:
            return imap_utf7.encode(folder[1:].decode('utf8'))

    def readFolders(self):
        self.list_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<folder>.*)')
        self.folders = []
        status, list = self.session.list()
        if status == 'OK':
            for elem in list:
                flags, delimiter, folder_utf7 = self.list_pattern.match(elem).groups()
                folder = self.fromIMAP(folder_utf7.strip('"'))
                # This folder makes imaplib complain, because it doesn't really exist
                # But subfolders like /[Gmail]/Spam exist
                if folder != '/[Gmail]':
                    self.folders.append(folder)
                    #~ print folder
        else:
            # TODO Handle errors
            pass
        self.folders.sort()

    def getFolders(self):
        if not self.folders:
            self.readFolders()
        return self.folders

    def getFolderMailbox(self, folderName, create=True):
        if not self.hasFolder(folderName):
            if create:
                self.createFolder(folderName, True)
            else:
                return None
        return ImapMailbox(self.properties['path'], folderName, self)

    def createFolder(self, folderName, includingPath=False):
        # TODO create recursively
        status, result = self.session.create(self.toIMAP(folderName))
        # TODO Handle errors
        # Force new read of folders list
        self.readFolders()

    def deleteFolder(self, folderName, includingChildren=False):
        # TODO delete recursively
        status, result = self.session.delete(self.toIMAP(folderName))
        # TODO Handle errors
        # Force new read of folders list
        self.readFolders()

    def hasFolder(self, folderName):
        if not self.folders:
            self.readFolders()
        return folderName in self.folders


RegisterMailStorage(ImapMailStorage)
