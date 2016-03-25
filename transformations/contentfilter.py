#!/usr/bin/python
# coding:utf8

from abstracttransformation import *


class ContentFilter(AbstractTransformation):
    """
    ContentFilter
    """

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method is not implemented yet')

RegisterTransformation(ContentFilter)
