#!/usr/bin/python
# coding:utf8

from abstracttransformation import *


class FolderPrefixChanger(AbstractTransformation):
    """
    FolderPrefixChanger
    """

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method is not implemented yet')

RegisterTransformation(FolderPrefixChanger)
