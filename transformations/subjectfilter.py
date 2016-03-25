#!/usr/bin/python
# coding:utf8

from abstracttransformation import *


class SubjectFilter(AbstractTransformation):
    """
    SubjectFilter
    """

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method is not implemented yet')

RegisterTransformation(SubjectFilter)
