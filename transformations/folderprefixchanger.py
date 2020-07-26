#!/usr/bin/python
# coding:utf8

from .abstracttransformation import *


class FolderPrefixChanger(AbstractTransformation):
    """
    FolderPrefixChanger
    """

    def __init__(self, instance, properties):
        AbstractTransformation.__init__(self, instance, properties)
        self.expectedProperties.append({
            'key': 'changeMethod',
            'label': 'Method',
            'content': 'list',
            'desc': 'Change Method',
            # TODO : prepare translation : labels are used directly in
            # the next function !
            'values': ['Remove Prefix', 'Change Prefix', 'Add Prefix', ],
        })
        self.expectedProperties.append({
            'key': 'folderRemoveValue',
            'label': 'Folder Prefix To Remove',
            'content': 'string',
            'desc': 'Folder prefix to remove',
        })
        self.expectedProperties.append({
            'key': 'folderAddValue',
            'label': 'Folder Prefix To Add',
            'content': 'string',
            'desc': 'Folder prefix to add',
        })

    def prepare_run(self):
        pass

    def transform(self, mailFolder, mail):
        if self.properties["changeMethod"] == 'Remove Prefix':
            if mailFolder.startswith(self.properties["folderRemoveValue"]):
                newMailFolder = mailFolder.replace(
                    self.properties["folderRemoveValue"],
                    '',
                    1  # Only the Prefix
                )
                return mailFolder, mail
        elif self.properties["changeMethod"] == 'Add Prefix':
            newMailFolder = self.properties["folderAddValue"] + mailFolder
            return newMailFolder, mail
        elif self.properties["changeMethod"] == 'Change Prefix':
            if mailFolder.startswith(self.properties["folderRemoveValue"]):
                newMailFolder = mailFolder.replace(
                    self.properties["folderRemoveValue"],
                    self.properties["folderAddValue"],
                    1  # Only the Prefix
                )
                return newMailFolder, mail
        else:
            raise Exception("Transformation Description is invalid")


RegisterTransformation(FolderPrefixChanger)
