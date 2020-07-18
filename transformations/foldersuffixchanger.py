#!/usr/bin/python
# coding:utf8

from .abstracttransformation import *


class FolderSuffixChanger(AbstractTransformation):
    """
    FolderSuffixChanger
    """

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method is not implemented yet')


RegisterTransformation(FolderSuffixChanger)
