#!/usr/bin/python
# coding:utf8

from abstracttransformation import *


class MailAddressChanger(AbstractTransformation):
    """
    MailAddressChanger
    """

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method is not implemented yet')

RegisterTransformation(MailAddressChanger)
