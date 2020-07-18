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
            'key': 'folderValue',
            'label': 'Folder Value',
            'content': 'string',
            'desc': 'Folder prefix to remove',
        })
        self.expectedProperties.append({
            'key': 'pattern',
            'label': 'Pattern',
            'content': 'string',
            'desc': 'Folder prefix to add',
        })

    def transform(self, mailFolder, mail):
        if mailFolder.startswith(self.properties["folderValue"]):
            return None, None
        else:
            return mailFolder, mail


RegisterTransformation(FolderPrefixChanger)
