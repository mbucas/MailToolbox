#!/usr/bin/python
# coding:utf8

import os
from mailbox import mbox

from .abstractmailstorage import *


class ThunderbirdMailbox(mbox):
    """ For Thunderbird, we use standard mbox class from Python library"""

    def get_message(self, key):
        """ Overloading for context data"""
        message = super(mbox, self).get_message(key)
        # TODO status
        setContext(message, key, 'read', 'add')
        return message


class ThunderbirdMailStorage(AbstractMailStorage):
    """
        Thunderbird Mail Storage reader and writer
        According to Thunderbird Local Folders structure
    """

    def getSubFolders(self, folder):
        # A user visible folder "a" is represented as
        # - a file named "a" in Mbox format
        # - a file named "a.msf" (Mail Summary File)
        # - an optional directory "a.sbd" if that folder contains subfolders
        hierarchy = [
            subfolder + ".sbd"
            for subfolder in folder.split("/")
            if subfolder != ""
        ]
        diskSubFolder = "/".join(hierarchy)

        fullContent = [
            entry
            for entry in os.listdir(
                os.path.join(
                    self.properties["path"],
                    diskSubFolder
                )
            )
        ]
        result = []
        for entry in fullContent:
            if entry + ".msf" in fullContent:
                result.append(folder + entry + "/")
            if entry + ".sbd" in fullContent:
                subfolders = self.getSubFolders(folder + entry + "/")
                for subfolder in subfolders:
                    result.append(subfolder)

        return result

    def getFolders(self):
        return self.getSubFolders("/")

    def getRealPath(self, folderName):
        hierarchy = [
            subfolder
            for subfolder in folderName.split("/")
            if subfolder != ""
        ]
        realHierarchy = [f + ".sbd" for f in hierarchy[:-1]] + hierarchy[-1:]
        diskSubFolder = "/".join(realHierarchy)
        return os.path.join(self.properties["path"], diskSubFolder)

    def getFolderMailbox(self, folderName, create=True):
        return ThunderbirdMailbox(self.getRealPath(folderName), None, create)

    def createFolder(self, folderName, includingPath=False):
        if not os.path.exists(self.getRealPath(folderName)):
            if includingPath:
                pass  # TODO
            else:
                if os.path.exists(
                    os.path.basename(self.getRealPath(folderName))
                ):
                    return mailbox.mbox(
                        self.getRealPath(folderName), None, True
                    )

    def deleteFolder(self, folderName, includingChildren=False):
        pass

    def hasFolder(self, folderName):
        return os.path.exists(self.getRealPath(folderName))


RegisterMailStorage(ThunderbirdMailStorage)
