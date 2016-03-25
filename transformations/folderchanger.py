#!/usr/bin/python
# coding:utf8

from abstracttransformation import *


class FolderChanger(AbstractTransformation):
    """
    FolderChanger
    """

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method is not implemented yet')

RegisterTransformation(FolderChanger)
