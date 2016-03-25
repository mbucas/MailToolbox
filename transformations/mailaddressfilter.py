#!/usr/bin/python
# coding:utf8

from abstracttransformation import *


class MailAddressFilter(AbstractTransformation):
    """
    MailAddressFilter
    """

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method is not implemented yet')

RegisterTransformation(MailAddressFilter)
