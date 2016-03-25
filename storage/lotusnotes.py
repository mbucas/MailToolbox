#!/usr/bin/python
# coding:utf8

import os
from mailbox import Mailbox
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import win32com.client
import tempfile #required for dealing with attachment

from abstractmailstorage import *


LotusNotesCharset = 'iso-8859-15'


class LotusNotesMailbox(Mailbox):
    """
        LotusNotes Mail Storage reader and writer
        For .NSF files
    """

    def __init__(self, path, folder, mailStorage):
        """Initialize a Maildir instance."""
        Mailbox.__init__(self, path, None, False)
        self.folder = folder
        self.mailStorage = mailStorage
        self.view = self.mailStorage.database.GetView(self.mailStorage.toLotus(folder))

    def add(self, message):
        """Add message and return assigned key."""
        raise NotImplementedError('Method is not implemented yet')

    def iterkeys(self):
        """Return an iterator over keys."""
        for i in range(self.view.AllEntries.Count):
            entry = self.view.AllEntries.GetNthEntry(i + 1)
            if entry and entry.IsDocument:
                yield entry.Document.NoteID

    def remove(self, key):
        """Remove the keyed message; raise KeyError if it doesn't exist."""
        raise NotImplementedError('Method is not implemented yet')

    def getValue(self, doc, item):
        val = doc.GetItemValue(item)
        if type(val) == tuple:
            val = val[0]
        if type(val) == unicode:
            return val.encode(LotusNotesCharset, errors='ignore')
        else:
            return val

    def getList(self, doc, item):
        return [
            elem.encode(LotusNotesCharset, errors='ignore')
            for elem in doc.GetItemValue(item)
        ]

    def getNameAndAdress(self, doc, nameItem, adressItem):
        # If there is no name, the address is in the first list
        # The second list contains a "."
        # TODO : don't show the dot if the first part is and email address
        pairs = zip(
            self.getList(doc, nameItem),
            self.getList(doc, adressItem)
        )
        # LDAP identifiers start with CN= and go to the next "/"
        # TODO : Remove it only if it's present
        return ','.join([
            pair[0].split('/')[0][3:]
            + ' <' 
            + pair[1]
            + '>'            
            for pair in pairs
        ])
        
    def attachmentsExist(self, doc):
        for item in doc.Items:
            if item.Name == '$FILE':
                return True
        return False
            
    def addAttachment(self, message, doc, item):
        dtemp = tempfile.mkdtemp()
        tempAttach = os.path.join(dtemp, 'tempAttach')
        attachmentName = item.Values[0]
        attachmentRef = doc.GetAttachment(attachmentName)
        attachmentRef.ExtractFile(tempAttach)
        attachment = MIMEBase('application', 'octet-stream')
        fp = open(tempAttach, 'rb')
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
        fname = attachmentName.encode(LotusNotesCharset, errors='ignore')
        attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename=fname
        )
        message.attach(attachment)
        os.remove(tempAttach)
        os.rmdir(dtemp)
        
    def addAttachments(self, message, doc):
        for item in doc.Items:
            if item.Name == '$FILE':
                self.addAttachment(message, doc, item)
                
    def get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        doc = self.mailStorage.database.GetDocumentByID(key)

        # Debug tools
        items = "-------------------------------------------------\n"
        for item in doc.Items:
            name = item.Name.encode(LotusNotesCharset, errors='ignore')
            text = item.Text.encode(LotusNotesCharset, errors='ignore')
            if name != "Body":
                if text != "":
                    items += name + ':' + text + '\n'
                else:
                    items += name + ':' + str(item.Values) + '\n'
        # /Debug tools

        body = self.getValue(doc, 'Body') + items
        bodymessage = MIMEText(body, _charset=LotusNotesCharset)
        
        if self.attachmentsExist(doc):
            message = MIMEMultipart(charset=LotusNotesCharset)
            message.set_charset(LotusNotesCharset)
            message.attach(bodymessage)
            self.addAttachments(message, doc)
        else:
            message = bodymessage
            
        message['Subject'] = self.getValue(doc, 'Subject')
        message['From'] = self.getNameAndAdress(doc, 'From', 'INetFrom')
        message['To'] = self.getNameAndAdress(doc, 'SendTo', 'InetSendTo')
        message['Cc'] = self.getNameAndAdress(doc, 'CopyTo', 'InetCopyTo')
        message['Date'] = self.getValue(doc, "PostedDate")
        if message['Date'] == u'':
            message['Date'] = self.getValue(doc, "DeliveredDate")
        message['User-Agent'] = self.getValue(doc, "$Mailer")
        message['Message-ID'] = self.getValue(doc, "$MessageID")
        # TODO status
        setContext(message, key, 'read', 'add')
        return message


class LotusNotesMailStorage(AbstractMailStorage):
    """
        LotusNotes Mail Storage reader and writer
        For .NSF files
    """

    def __init__(self, properties):
        AbstractMailStorage.__init__(self, properties)
        self.expectedProperties.append({
            'key': 'user',
            'label': 'User',
            'content': 'string',
            'desc': 'Lotus Notes User',
        })
        self.expectedProperties.append({
            'key': 'password',
            'label': 'Password',
            'content': 'hidden',
            'desc': 'Lotus Notes Password',
        })

    def openSession(self):
        self.session = win32com.client.Dispatch(r'Lotus.NotesSession')
        self.session.Initialize(self.properties['password'])
        self.database = self.session.GetDatabase("", self.properties['path'])
        self.folders = None
        self.LotusFolders = {}

    def closeSession(self):
        raise NotImplementedError('Not implemented as of yet')

    def fromLotus(self, folder):
        out = '/' + folder.encode(LotusNotesCharset).replace('\\', '/')
        self.LotusFolders[out] = folder
        return out

    def toLotus(self, folder):
        return self.LotusFolders[folder]

    def readFolders(self):
        self.folders = []
        for view in self.database.Views:
            if view.isFolder:
                folder = self.fromLotus(view.Name)
                if folder not in self.folders:
                    self.folders.append(folder)
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
        return LotusNotesMailbox(self.properties['path'], folderName, self)

    def createFolder(self, folderName, includingPath=False):
        # Force new read of folders list
        self.readFolders()
        raise NotImplementedError('Method is not implemented yet')

    def deleteFolder(self, folderName, includingChildren=False):
        # Force new read of folders list
        self.readFolders()
        raise NotImplementedError('Method is not implemented yet')

    def hasFolder(self, folderName):
        if not self.folders:
            self.readFolders()
        return folderName in self.folders

RegisterMailStorage(LotusNotesMailStorage)
