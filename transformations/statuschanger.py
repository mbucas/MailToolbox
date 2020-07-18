#!/usr/bin/python
# coding:utf8

from .abstracttransformation import *


class StatusChanger(AbstractTransformation):
    """
    StatusChanger
    """

    def __init__(self, instance, properties):
        AbstractTransformation.__init__(self, instance, properties)
        self.expectedProperties.append({
            'key': 'changeMethod',
            'label': 'Method',
            'content': 'list',
            'desc': 'Filtering Method',
            # TODO : prepare translation : labels are used directly in
            # the next function !
            'values': [
                'Force All Read',
                'Force All Unread',
                'Invert Status',
            ],
        })

    def prepare_run(self):
        if self.properties["method"] == 'Force All Read':
            self.transform = transform_forceallread
        elif self.properties["method"] == 'Force All Unread':
            self.transform = transform_forceallunread
        elif self.properties["method"] == 'Invert Status':
            self.transform = transform_invertstatus
        else:
            raise NotImplementedError(
                "Method %s is not implemented" % self.properties["method"]
            )

    def transform_forceallread(self, mailFolder, mail):
        mail.status = 'read'
        return mailFolder, mail

    def transform_forceallunread(self, mailFolder, mail):
        mail.status = 'unread'
        return mailFolder, mail

    def transform_invertstatus(self, mailFolder, mail):
        mail.status = 'read' if mail.status == 'unread' else 'unread'
        return mailFolder, mail


RegisterTransformation(StatusChanger)
