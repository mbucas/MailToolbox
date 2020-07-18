#!/usr/bin/python
# coding:utf8

import os
from time import time
from mailbox import Mailbox
from email import encoders, utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import win32com.client
# required for dealing with attachment
import tempfile

from .abstractmailstorage import *


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
        self.view = (
            self
            .mailStorage
            .database
            .GetView(self.mailStorage.toLotus(folder))
        )

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
        if item in ('PostedDate', 'DeliveredDate'):
            return utils.formatdate(float(int(val)))
        else:
            return str(val)

    def getList(self, doc, item):
        return [
            elem.encode(LotusNotesCharset, errors='ignore')
            for elem in doc.GetItemValue(item)
        ]

    def getNameAndAdress(self, doc, nameItem, adressItem):
        # If there is no name, the address is in the first list
        # The second list contains a "."
        # Using "map" instead of "zip" because lists can have different lengths
        pairs = map(
            None,
            self.getList(doc, nameItem),
            self.getList(doc, adressItem)
        )
        # LDAP identifiers start with CN= and go to the next "/"
        names = []
        for pair in pairs:
            if pair[0] is None:
                name = ''
            elif pair[0][:3] == "CN=":
                name = pair[0].split('/')[0][3:]
            else:
                name = pair[0]
            if pair[1] == '.' or pair[1] == '' or pair[1] is None:
                addr = ''
            else:
                addr = ' <' + pair[1] + '>'
            if name != '':
                names.append(name + addr)

        return ','.join(names)

    def attachmentsExist(self, doc):
        for item in doc.Items:
            if item.Name == '$FILE':
                return True
        return False

    def addAttachment(self, message, doc, item):
        attachmentName = item.Values[0]
        attachmentRef = doc.GetAttachment(attachmentName)
        if attachmentRef:
            dtemp = tempfile.mkdtemp()
            tempAttach = os.path.join(dtemp, 'tempAttach')
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
        else:
            message.invalidAttachment = True

    def addAttachments(self, message, doc):
        for item in doc.Items:
            if item.Name == '$FILE':
                self.addAttachment(message, doc, item)

    def setHeaderIfPresent(self, message, RFCHeader, doc, LotusHeader, INetLotusHeader):
        text = self.getNameAndAdress(doc, LotusHeader, INetLotusHeader)
        if len(text) != 0:
            message[RFCHeader] = text

    def get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        doc = self.mailStorage.database.GetDocumentByID(key)

        body = self.getValue(doc, 'Body')
        bodymessage = MIMEText(body, _charset=LotusNotesCharset)

        if self.attachmentsExist(doc):
            message = MIMEMultipart(charset=LotusNotesCharset)
            message.invalidAttachment = False
            message.set_charset(LotusNotesCharset)
            message.attach(bodymessage)
            self.addAttachments(message, doc)
        else:
            message = bodymessage
            message.invalidAttachment = False

        message['Subject'] = self.getValue(doc, 'Subject')
        self.setHeaderIfPresent(
            message, 'From', doc, 'From', 'INetFrom'
        )
        self.setHeaderIfPresent(
            message, 'Reply-To', doc, 'ReplyTo', '$INetReplyTo'
        )
        self.setHeaderIfPresent(
            message, 'To', doc, 'SendTo', 'InetSendTo'
        )
        self.setHeaderIfPresent(
            message, 'Cc', doc, 'CopyTo', 'InetCopyTo'
        )
        self.setHeaderIfPresent(
            message, 'Bcc', doc, 'BlindCopyTo', 'InetBlindCopyTo'
        )
        mDate = self.getValue(doc, "PostedDate")
        if mDate is None or mDate == '':
            mDate = self.getValue(doc, "DeliveredDate")
        message['Date'] = mDate
        message['User-Agent'] = self.getValue(doc, "$Mailer")
        message['Message-ID'] = self.getValue(doc, "$MessageID")
        # TODO status
        setContext(message, key, 'read', 'add')

        # Debug tools
        dump = ('-' * 80) + '\n' + "== Lotus Notes Headers ==\n"
        hasPostedDate = False
        hasDeliveredDate = False
        for item in doc.Items:
            name = item.Name.encode(LotusNotesCharset, errors='ignore')
            if name in ('PostedDate', 'DeliveredDate'):
                dump += (
                    name
                    + ':('
                    + str(type(item.Values))
                    + ') '
                    + str(item.Values)
                    + ' -> '
                    + utils.formatdate(float(int(item.Values[0])))
                    + '\n'
                )
            if name == 'PostedDate':
                hasPostedDate = True
            if name == 'DeliveredDate':
                hasDeliveredDate = True
            text = item.Text.encode(LotusNotesCharset, errors='ignore')
            if name != "Body":
                if text != "":
                    dump += name + ':' + text + '\n'
                else:
                    dump += (
                        name
                        + ':('
                        + str(type(item.Values))
                        + ') '
                        + str(item.Values)
                        + '\n'
                    )
        dump += 'hasPostedDate:' + str(hasPostedDate) + '\n'
        dump += 'hasDeliveredDate:' + str(hasDeliveredDate) + '\n'
        dump += "== Message Headers ==\n"
        dump += 'typeOfmDate:' + str(type(mDate)) + ' ' + mDate + '\n'
        for name, text in message.items():
            dump += name + ': (' + str(type(text)) + ')' + text + '\n'
        dump += '\n\n'
        message.dump = dump
        # /Debug tools
        if message.invalidAttachment:
            print("Attachment not found for mail")
            print(message.dump)

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
        # Hope it's enough to terminate a session cleanly
        # I didn't find a function to do it directly
        # See http://www.ibm.com/support/knowledgecenter/SSVRGU_9.0.0/
        # com.ibm.designer.domino.main.doc/H_NOTESSESSION_CLASS.html
        self.LotusFolders = None
        self.folders = None
        self.database = None
        self.session = None

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
