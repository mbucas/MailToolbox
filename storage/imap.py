#!/usr/bin/python
# coding:utf8

from mailbox import Mailbox
from email import message_from_string
from email.message import Message
from email.utils import parsedate
import imaplib
import re
import time

from logtext import logtext
from .abstractmailstorage import *
from . import imap_utf7


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
        try:
            msg_date_str = message.get("date")
            msg_date = parsedate(msg_date_str)
        except Exception as e:
            # Fallback to current time
            logtext.logText(str(msg_date) + ' ' + str(e))
            msg_date = time.time()
        try:
            self.mailStorage.session.append(
                self.mailStorage.toIMAP(self.folder),
                '',
                imaplib.Time2Internaldate(msg_date),
                message.as_string().encode('utf-8')
            )
        except imaplib.IMAP4.error as err:
            # TODO Identify the mail that caused error
            logtext.logText(str(err))

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
        self.session.login(
            self.properties['user'],
            self.properties['password']
        )
        self.folders = None
        self.IMAPFolders = {}

    def closeSession(self):
        self.session.logout()

    def fromIMAP(self, IMAPFolder):
        # Remove quotes if present
        # See https://stackoverflow.com/questions/25186394/
        localFolder = imap_utf7.decode(IMAPFolder).strip('"')
        self.IMAPFolders[localFolder] = IMAPFolder
        return localFolder

    def toIMAP(self, localFolder):
        # Add quotes if white space in folder name
        # See https://stackoverflow.com/questions/25186394/
        if localFolder in self.IMAPFolders:
            return self.IMAPFolders[localFolder]
        else:
            if ' ' in localFolder:
                IMAPFolder = b'"' + imap_utf7.encode(localFolder) + b'"'
            else:
                IMAPFolder = imap_utf7.encode(localFolder)
            self.IMAPFolders[localFolder] = IMAPFolder
            return IMAPFolder

    def readFolders(self):
        self.list_pattern = re.compile(
            r'\((?P<flags>.*?)\) '
            + '"(?P<delimiter>.*)"'
            + ' (?P<folder>.*)'
        )
        self.folders = []
        status, list = self.session.list()
        if status == 'OK':
            for elem in list:
                flags, delimiter, folder_utf7 = (
                    self
                    .list_pattern
                    .match(elem.decode('utf-8'))
                    .groups()
                )
                folder = self.fromIMAP(folder_utf7)
                # This folder makes imaplib complain, because
                # it doesn't really exist
                # But subfolders like /[Gmail]/Spam exist
                if folder != '/[Gmail]':
                    self.folders.append(folder)
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

    def createFolder(self, folderName, includingPath=True):
        if includingPath:
            if '/' in folderName:
                self.createFolder('/'.join(folderName.split('/')[:-1]))
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
