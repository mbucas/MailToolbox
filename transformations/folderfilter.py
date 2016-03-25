#!/usr/bin/python
# coding:utf8

import re

from abstracttransformation import *


class FolderFilter(AbstractTransformation):
    """
    FolderFilter
    """

    def __init__(self, instance, properties):
        AbstractTransformation.__init__(self, instance, properties)
        self.expectedProperties.append({
            'key': 'filterMethod',
            'label': 'Method',
            'content': 'list',
            'desc': 'Filtering Method',
            # TODO : prepare translation : labels are used directly in the next function !
            'values': ['Starts With', 'Ends With', 'Contains', 'Regular Expression',],
        })
        self.expectedProperties.append({
            'key': 'folderValue',
            'label': 'Folder Value',
            'content': 'string',
            'desc': 'Value used for filtering',
        })
        self.expectedProperties.append({
            'key': 'pattern',
            'label': 'Pattern',
            'content': 'string',
            'desc': 'Regular Expression Pattern',
        })

    def prepare_run(self):
        if self.properties["method"] == 'Starts With':
            self.transform = transform_startswith
        elif self.properties["method"] == 'Ends With':
            self.transform = transform_endswith
        elif self.properties["method"] == 'Contains':
            self.transform = transform_contains
        elif self.properties["method"] == 'Regular Expression':
            self.transform = transform_regexp
            self.regexp = re.compile(self.properties["pattern"])
        else:
            raise NotImplementedError("Method %s is not implemented" % self.properties["method"])

    def transform_startswith(self, mailFolder, mail):
        if mailFolder.startswith(self.properties["folderValue"]):
            return None, None
        else:
            return mailFolder, mail

    def transform_endswith(self, mailFolder, mail):
        if mailFolder.endswith(self.properties["folderValue"]):
            return None, None
        else:
            return mailFolder, mail

    def transform_contains(self, mailFolder, mail):
        if mailFolder.find(self.properties["folderValue"]) != -1:
            return None, None
        else:
            return mailFolder, mail

    def transform_regexp(self, mailFolder, mail):
        if self.regexp.match(mailFolder):
            return None, None
        else:
            return mailFolder, mail


RegisterTransformation(FolderFilter)
