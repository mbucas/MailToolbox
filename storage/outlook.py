#!/usr/bin/python
# coding:utf8

import os
import sys
import time

from mailbox import Mailbox
from email.message import Message
from email.header import Header
from email import encoders, utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import win32com.client
import pywintypes
# required for dealing with attachment
import tempfile

from logtext import logtext
from .abstractmailstorage import *

# Constants for OutLook

# See https://msdn.microsoft.com/fr-fr/library/office/ff868695.aspx
PR_SMTP_ADDRESS = "http://schemas.microsoft.com/mapi/proptag/0x39FE001E"

# See http://www.bitpim.org/apidoc/native.outlook.outlook_com-pysrc.html
# from enum OlMailRecipientType
olOriginator = 0x0
olTo = 0x1
olCC = 0x2
olBCC = 0x3
# From observation of existing messages
olReplyTo = 0x1

# from enum OlObjectClass
# https://msdn.microsoft.com/en-us/library/office/ff863329.aspx
olMail = 43
olReport = 46
olMeetingCancellation = 54
olMeetingForwardNotification = 181
olMeetingRequest = 53
olMeetingResponseNegative = 55
olMeetingResponsePositive = 56
olMeetingResponseTentative = 57
MailLikeClasses = [
    olMail,
    olReport,
    olMeetingCancellation,
    olMeetingForwardNotification,
    olMeetingRequest,
    olMeetingResponseNegative,
    olMeetingResponsePositive,
    olMeetingResponseTentative,
]

# OlBodyFormat Enumeration
# https://msdn.microsoft.com/fr-fr/library/office/ff864792.aspx
olFormatUnspecified = 0  # 0 Format non specifie
olFormatPlain = 1        # 1 Format simple
olFormatHTML = 2         # 2 Format HTML
olFormatRichText = 3      # 3 Format RTF (texte enrichi)

OutlookCharset = 'iso-8859-1'


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
        count = self.mailStorage.OutlookFolders[self.folder].Items.Count
        for i in range(count):
            entry = i
            if entry:
                yield entry

    def remove(self, key):
        """Remove the keyed message; raise KeyError if it doesn't exist."""
        raise NotImplementedError('Method is not implemented yet')

    def get_address(self, listsDest, recipient, RFCHeader, OutlookType):
        propAccessor = recipient.PropertyAccessor
        if recipient.Type == OutlookType:
            if ',' in recipient.Name:
                name = '"' + recipient.Name + '"'
            else:
                name = recipient.Name
            try:
                adresse = propAccessor.GetProperty(PR_SMTP_ADDRESS)
            except Exception as e:
                adresse = recipient.Address
            if adresse == '':
                listsDest[RFCHeader].append(name)
            else:
                listsDest[RFCHeader].append(name + ' <' + adresse + '>')

    def addAttachments(self, message, Attachments):
        for item in Attachments:
            dtemp = tempfile.mkdtemp()
            tempAttach = os.path.join(dtemp, 'tempAttach')
            item.SaveAsFile(tempAttach)
            attachment = MIMEBase('application', 'octet-stream')
            try:
                fp = open(tempAttach, 'rb')
                attachment.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(attachment)
                fname = item.DisplayName.encode(
                    OutlookCharset,
                    errors='ignore'
                )
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=fname
                )
                message.attach(attachment)
                os.remove(tempAttach)
                os.rmdir(dtemp)
            except IOError as e:
                # Some attachements are URLs to outside files
                # The result is a "tempAttach.url" file, with the link
                # to attachement
                # Open fails on this type of file
                # Leaving a temporary file and directory is not clean
                # TODO Clean this mess
                pass

    def get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        outlookMessage = (
            self
            .mailStorage
            .OutlookFolders[self.folder]
            .Items[key]
        )
        if outlookMessage.Class not in MailLikeClasses:
            logtext.logText(outlookMessage.Class)
            return None

        # Body
        dumpError = ''
        if outlookMessage.Class == olMail:
            if outlookMessage.BodyFormat == olFormatHTML:
                try:
                    body = outlookMessage.HTMLBody.encode('utf-8')
                    bodymessage = MIMEText(
                        body,
                        _subtype='html',
                        _charset='utf-8'
                    )
                except UnicodeEncodeError as e:
                    dumpError = (
                        ('-' * 80) + '\n'
                        + "BodyFormat: " + str(outlookMessage.BodyFormat)
                        + '\n'
                        + e.reason + '\n'
                        + e.encoding + '\n'
                        + ('-' * 80) + '\n'
                        + outlookMessage.HTMLBody + '\n'
                    )
                    body = outlookMessage.HTMLBody
                    bodymessage = MIMEText(
                        body,
                        _subtype='html',
                        _charset='utf-8'
                    )
            elif outlookMessage.BodyFormat == olFormatRichText:
                try:
                    # RTFBody is an array of bytes, so a join is necessary
                    body = (
                        ""
                        .join(outlookMessage.RTFBody)
                        .decode(OutlookCharset)
                        .encode('utf-8')
                    )
                    bodymessage = MIMEText(
                        body,
                        _subtype='rtf',
                        _charset='utf-8'
                    )
                except UnicodeEncodeError as e:
                    dumpError = (
                        ('-' * 80) + '\n' +
                        "BodyFormat: " + str(outlookMessage.BodyFormat) +
                        '\n' +
                        "UnicodeEncodeError: " + e.reason + '\n' +
                        e.encoding + '\n' +
                        ('-' * 80) + '\n' +
                        str(dir(outlookMessage.RTFBody)) + '\n'
                    )
                    body = "".join(outlookMessage.RTFBody)
                    bodymessage = MIMEText(
                        body,
                        _subtype='rtf',
                        _charset='utf-8'
                    )
                except UnicodeDecodeError as e:
                    dumpError = (
                        ('-' * 80) + '\n' +
                        "BodyFormat: " + str(outlookMessage.BodyFormat) +
                        '\n' +
                        "UnicodeDecodeError: " + e.reason + '\n' +
                        e.encoding + '\n' +
                        ('-' * 80) + '\n' +
                        str(dir(outlookMessage.RTFBody)) + '\n'
                    )
                    body = "".join(outlookMessage.RTFBody)
                    bodymessage = MIMEText(
                        body,
                        _subtype='rtf',
                        _charset='utf-8'
                    )
            else:
                # All other formats are considered text
                try:
                    body = outlookMessage.Body.encode(OutlookCharset)
                    bodymessage = MIMEText(
                        body,
                        _subtype='plain',
                        _charset='utf-8'
                    )
                except UnicodeEncodeError as e:
                    dumpError = (
                        ('-' * 80) + '\n'
                        + "BodyFormat: " + str(outlookMessage.BodyFormat)
                        + '\n'
                        + e.reason + '\n'
                        + e.encoding + '\n'
                        + ('-' * 80) + '\n'
                        + outlookMessage.Body + '\n'
                    )
                    body = outlookMessage.Body.encode('utf-8')
                    bodymessage = MIMEText(
                        body,
                        _subtype='plain',
                        _charset='utf-8'
                    )
        else:
            # All other classes are considered text
            try:
                body = outlookMessage.Body.encode(OutlookCharset)
                bodymessage = MIMEText(
                    body,
                    _subtype='plain',
                    _charset='utf-8'
                )
            except UnicodeEncodeError as e:
                dumpError = (
                    ('-' * 80) + '\n'
                    + "Class: " + str(outlookMessage.Class)
                    + '\n'
                    + e.reason + '\n'
                    + e.encoding + '\n'
                    + ('-' * 80) + '\n'
                    + outlookMessage.Body + '\n'
                )
                body = outlookMessage.Body.encode('utf-8')
                bodymessage = MIMEText(
                    body,
                    _subtype='plain',
                    _charset='utf-8'
                )

        # Attached files
        if outlookMessage.Attachments.Count > 0:
            message = MIMEMultipart(charset=OutlookCharset)
            message.invalidAttachment = False
            message.set_charset(OutlookCharset)
            message.attach(bodymessage)
            self.addAttachments(message, outlookMessage.Attachments)
        else:
            message = bodymessage
            message.invalidAttachment = False

        # Subject
        message['Subject'] = Header(outlookMessage.Subject, OutlookCharset)

        # Date
        try:
            if outlookMessage.SentOn is None:
                mDate = outlookMessage.ReceivedTime
            else:
                mDate = outlookMessage.SentOn
        except AttributeError as e:
            mDate = None

        if mDate is not None:
            tDate = (
                mDate.year, mDate.month, mDate.day,
                mDate.hour, mDate.minute, mDate.second,
                0, 0, 0
            )
            message['Date'] = (
                time.strftime(
                    "%a, %d %b %Y %H:%M:%S -0000",
                    tDate
                )
            )

        # Sender
        try:
            if outlookMessage.Sender is not None:
                if ',' in outlookMessage.Sender.Name:
                    name = '"' + outlookMessage.Sender.Name + '"'
                else:
                    name = outlookMessage.Sender.Name
                exUser = outlookMessage.Sender.GetExchangeUser()
                if exUser is not None:
                    if exUser.PrimarySmtpAddress != '':
                        adresse = ' <' + exUser.PrimarySmtpAddress + '>'
                    else:
                        adresse = ''
                else:
                    adresse = ' <' + outlookMessage.SenderEmailAddress + '>'
                message['From'] = Header(name + adresse, OutlookCharset)
        except AttributeError as e:
            message['From'] = 'Unknown'

        # Recipients
        if hasattr(outlookMessage, 'Recipients'):
            listsDest = {}
            listsDest['To'] = []
            listsDest['Cc'] = []
            listsDest['Bcc'] = []
            for recipient in outlookMessage.Recipients:
                self.get_address(listsDest, recipient, 'To', olTo)
                self.get_address(listsDest, recipient, 'Cc', olCC)
                self.get_address(listsDest, recipient, 'Bcc', olBCC)
            for header in ('To', 'Cc', 'Bcc'):
                if len(listsDest[header]) > 0:
                    message[header] = Header(
                        ','.join(listsDest[header]),
                        OutlookCharset
                    )
        if hasattr(outlookMessage, 'ReplyRecipients'):
            listsDest = {}
            listsDest['Reply-To'] = []
            for recipient in outlookMessage.ReplyRecipients:
                self.get_address(
                    listsDest,
                    recipient,
                    'Reply-To',
                    olReplyTo
                )
            if len(listsDest['Reply-To']) > 0:
                message['Reply-To'] = Header(
                    ','.join(listsDest['Reply-To']),
                    OutlookCharset
                )

        # TODO status
        setContext(message, key, 'read', 'add')

        # Debug tools
        dump = ('-' * 80) + '\n'
#        dump = "== Outlook Headers ==\n"
#        if hasattr(outlookMessage, 'ReplyRecipients'):
#            dump += (
#               'ReplyRecipients Count: '
#               + str(outlookMessage.ReplyRecipients.Count)
#               + '\n'
#            )
#            for recipient in outlookMessage.ReplyRecipients:
#                dump += 'ReplyRecipients Type: ' + str(recipient.Type) + '\n'
#                dump += 'ReplyRecipients: ' + str(recipient.Name) + '\n'
#        dump += "== Message Headers ==\n"
#        if message['From'] is not None:
#            dump += 'From: ' + str(message['From']) + '\n'
#        if message['Date'] is not None:
#            dump += 'Date: ' + str(message['Date']) + '\n'
#        if message['Reply-To'] is not None:
#            dump += 'Reply-To: ' + str(message['Reply-To']) + '\n'
        dump += "== Message Body ==\n"
        dump += dumpError
        dump += '\n'
        if dumpError == '':
            message.dump = ''
        else:
            message.dump = dump
        # /Debug tools

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
        self.session = win32com.client.Dispatch(r"Outlook.Application")
        self.database = self.session.GetNamespace("MAPI")
        self.folders = None
        self.OutlookFolders = {}

    def closeSession(self):
        pass

    def getSubFolders(self, baseFolder, basePath):
        """ Recursive function """
        NbFolders = baseFolder.Count
        for i in range(NbFolders):
            folderName = baseFolder[i].Name
            folder = basePath + '/' + folderName
            # Keep a reference to Outlook objects to avoid recursive search
            self.OutlookFolders[folder] = baseFolder[i]

            if folder not in self.folders:
                self.folders.append(folder)
                if baseFolder[i].Folders:
                    # Recursive call
                    self.getSubFolders(baseFolder[i].Folders, folder)

    def readFolders(self):
        self.folders = []
        self.getSubFolders(self.database.Folders, '')
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
        return OutlookMailbox(self.properties['path'], folderName, self)

    def createFolder(self, folderName, includingPath=False):
        raise NotImplementedError('Method must be implemented by subclass')

    def deleteFolder(self, folderName, includingChildren=False):
        raise NotImplementedError('Method must be implemented by subclass')

    def hasFolder(self, folderName):
        if not self.folders:
            self.readFolders()
        return folderName in self.folders


RegisterMailStorage(OutlookMailStorage)
