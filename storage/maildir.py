#!/usr/bin/python
# coding:utf8

import os
import sys
import email
from email import message
from mailbox import Maildir

from .abstractmailstorage import *


class MaildirMailbox(Maildir):
    """ For Maildir, we use standard Maildir class from Python library"""

    def get_message(self, key):
        """ Overloading for context data"""
        message = Maildir.get_message(self, key)
        # TODO status
        setContext(message, key, 'read', 'add')
        return message


class MaildirMailStorage(AbstractMailStorage):
    """
        Maildir Mail Storage reader and writer
    """

    def __init__(self, properties):
        AbstractMailStorage.__init__(self, properties)
        self.folders = None

    def readFolders(self):
        alldirs = [
            (
                ldir[0]
                .replace(self.properties["path"], '')
                .replace(os.sep, '/')
            )
            for ldir in os.walk(self.properties["path"])
            if ldir[0] != self.properties["path"]
        ]
        self.folders = ['/'] + [
            folder for folder in alldirs
            if not(
                folder.endswith('/cur')
                or folder.endswith('/new')
                or folder.endswith('/tmp')
                or folder == 'cur'
                or folder == 'new'
                or folder == 'tmp'
            )
        ]
        self.folders.sort()

    def getFolders(self):
        if not self.folders:
            self.readFolders()
        return self.folders

    def getFolderMailbox(self, folderName, create=True):
        localFolderName = os.path.join(
            self.properties["path"],
            os.path.join(*(folderName.split('/')))
        )
        # These folders don't always exist in imported mailboxes
        for subdir in ('cur', 'new', 'tmp'):
            mailsubdir = os.path.join(localFolderName, subdir)
            if not os.path.isdir(mailsubdir):
                try:
                    os.mkdir(mailsubdir)
                except Exception as e:
                    raise IOError("Unable to create directory" + mailsubdir)

        return MaildirMailbox(localFolderName, None, True)

    def createFolder(self, folderName, includingPath=True):
        folderpath = os.path.join(
            self.properties["path"],
            os.path.join(*folderName.split('/'))
        )
        if includingPath:
            if sys.platform == 'win32':
                # TODO : create cur new tmp at each level
                try:
                    os.makedirs(folderpath)
                except WindowsError:
                    # TODO : Ignore only WindowsError:
                    # [Error 183] Impossible de creer un fichier deja existant
                    pass
            else:
                try:
                    os.makedirs(folderpath)
                except OSError:
                    # TODO : Ignore only OSError:
                    # [Errno 17] Le fichier existe
                    pass
        else:
            os.mkdir(folderpath)
        for subdir in ('cur', 'new', 'tmp'):
            if sys.platform == 'win32':
                try:
                    os.mkdir(os.path.join(folderpath, subdir))
                except WindowsError:
                    # TODO : Ignore only WindowsError:
                    # [Error 183] Impossible de creer un fichier deja existant
                    pass
            else:
                try:
                    os.mkdir(os.path.join(folderpath, subdir))
                except OSError:
                    # TODO : Ignore only OSError:
                    # [Errno 17] Le fichier existe
                    pass

        # Force new read of folders list
        self.readFolders()

    def deleteFolder(self, folderName, includingChildren=False):
        # Force new read of folders list
        self.readFolders()
        raise NotImplementedError('Not implemented as of yet')

    def hasFolder(self, folderName):
        if not self.folders:
            self.readFolders()

        if folderName in self.folders:
            # Force subdirs creation
            folderpath = os.path.join(
                self.properties["path"],
                os.path.join(*folderName.split('/'))
            )
            for subdir in ('cur', 'new', 'tmp'):
                try:
                    os.mkdir(os.path.join(folderpath, subdir))
                except OSError:
                    pass

        return folderName in self.folders


RegisterMailStorage(MaildirMailStorage)
