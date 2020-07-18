#!/usr/bin/python
# coding:utf8

from mailbox import Mailbox
import xml.etree.ElementTree as ET


def setContext(message, key, status, action):
    """
    setContext

    Function that adds external informations to an email message:
     - message is an email.Message instance
     - sourceKey is the identifier within a MailBox, and is specific to each
     type of MailBox
     - status is 'read' or 'unread'
     - action is 'add', 'remove' or 'update', and is used when the target
     is configured to do 'data driven' actions
    """
    if message:
        message.sourceKey = key
        message.status = status
        message.action = action


class AbstractMailStorage(object):
    """
        Parent abstract class for all mail storages
        Defines reading and writing methods for mails and folders
    """

    def __init__(self, properties=None):
        self.action = 'add'
        self.properties = properties
        self.expectedProperties = []
        self.expectedProperties.append({
            'key': 'name',
            'label': 'Name',
            'content': 'string',
            'desc': 'Storage name',
        })
        self.expectedProperties.append({
            'key': 'storagetype',
            'label': 'Storage Type',
            'content': 'list',
            'desc': 'Storage Type',
            'values': [s for s in MailStorageRegistry],
        })
        self.expectedProperties.append({
            'key': 'path',
            'label': 'Path',
            'content': 'string',
            'desc': 'Base Path or URL for IMAP',
        })
        self.expectedProperties.append({
            'key': 'action',
            'label': 'Action',
            'content': 'list',
            'desc': 'Action on target',
            'values': ['add', 'update', 'remove'],
        })

    def openSession(self):
        pass

    def closeSession(self):
        pass

    def isValid(self):
        for p in self.expectedProperties:
            if not p['key'] in properties:
                return False
        return True

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

    def serializeToXml(self):
        storage = ET.Element('storage', classname=self.__class__.__name__)
        for p in self.expectedProperties:
            if p['key'] in self.properties:
                ET.SubElement(
                    storage,
                    'property',
                    name=p['key'],
                    value=self.properties[p['key']]
                )
        return storage


MailStorageRegistry = {}


def RegisterMailStorage(mailstorageclass):
    MailStorageRegistry[mailstorageclass.__name__] = mailstorageclass


def MailStorageFactory(name, properties):
    """
        Create apropriate MailStorage for mail storage description
    """
    if name:
        if name not in MailStorageRegistry:
            raise NotImplementedError(
                "MailStorage %s is not implemented" % name
            )
        else:
            return MailStorageRegistry[name](properties)
    else:
        raise Exception("Mail Storage Description is invalid")
