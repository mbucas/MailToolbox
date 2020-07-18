#!/usr/bin/python
# coding:utf8

from .abstracttransformation import *


class SubjectChanger(AbstractTransformation):
    """
    SubjectChanger
    """

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method is not implemented yet')


RegisterTransformation(SubjectChanger)
