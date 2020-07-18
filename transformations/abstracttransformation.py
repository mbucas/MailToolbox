#!/usr/bin/python
# coding:utf8

import xml.etree.ElementTree as ET


class AbstractTransformation(object):
    """
    AbstractTransformation
    """

    def __init__(self, instance, properties=None):
        self.instance = instance
        self.properties = properties
        self.expectedProperties = []
        self.expectedProperties.append({
            'key': 'name',
            'label': 'Name',
            'content': 'string',
            'desc': 'Transformation name',
        })
        self.expectedProperties.append({
            'key': 'transformationtype',
            'label': 'Transformation Type',
            'content': 'list',
            'desc': 'Transformation Type',
            'values': [s for s in TransformationRegistry],
        })

    def prepare_run(self):
        raise NotImplementedError('Method must be implemented by subclass')

    def transform(self, mailFolder, mail):
        raise NotImplementedError('Method must be implemented by subclass')

    def serializeToXml(self):
        transformation = ET.Element(
            'transformation',
            classname=self.__class__.__name__,
            instance=self.instance
        )
        for p in self.properties:
            ET.SubElement(
                transformation,
                'property',
                name=p,
                value=self.properties[p]
            )
        return transformation


TransformationRegistry = {}


def RegisterTransformation(transformationclass):
    TransformationRegistry[transformationclass.__name__] = transformationclass


def TransformationFactory(name, instance, properties):
    """
        Create apropriate Transformation for transformation description
    """
    if name:
        if name not in TransformationRegistry:
            raise NotImplementedError(
                "Transformation %s is not implemented" % name
            )
        else:
            return TransformationRegistry[name](instance, properties)
    else:
        raise Exception("Transformation Description is invalid")
