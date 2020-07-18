#!/usr/bin/python
# coding:utf8

from .abstracttransformation import *


class NoTransformation(AbstractTransformation):
    """
    NoTransformation
    """

    def transform(self, mailFolder, mail):
        return mailFolder, mail


RegisterTransformation(NoTransformation)
