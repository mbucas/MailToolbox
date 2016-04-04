#!/usr/bin/python
# coding:utf8

import xml.etree.ElementTree as ET
from xml.dom import minidom

from storage import storage
from transformations import transformations


def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def extractValues(elem, type):
    array = {}
    for valueElem in elem:
        if valueElem.tag == type:
            if "name" in valueElem.attrib:
                name = valueElem.attrib["name"]
            else:
                name = None
            if "value" in valueElem.attrib:
                value = valueElem.attrib["value"]
            else:
                value = None
            if name:
                array[name] = value
    return array


class Project(object):
    def __init__(self, source=None, target=None, transformations=None):
        if source:
            self.source = source
        else:
            self.source = storage.NoMailStorage({
                'name': "Source",
                'storagetype': "NoMailStorage",
                'path': "",
                'action': "",
            })
        if target:
            self.target = target
        else:
            self.target = storage.NoMailStorage({
                'name': "Target",
                'storagetype': "NoMailStorage",
                'path': "",
                'action': "add",
            })
        if not transformations:
            self.transformations = []
        else:
            self.transformations = transformations
        self.file = None
        self.changed = False

    def isValid(self):
        # Project may be created with no informations
        if not self.source:
            return False
        if not self.target:
            return False
        return True

    def serializeToXml(self):
        projectXml = ET.Element('project')
        # Source
        if self.source:
            source = ET.SubElement(projectXml, 'source')
            source.append(self.source.serializeToXml())
        # Target
        if self.target:
            target = ET.SubElement(projectXml, 'target')
            target.append(self.target.serializeToXml())
        # Transformations
        transformationsXml = ET.Element('transformations')
        for t in self.transformations:
            transformationsXml.append(t.serializeToXml())
        projectXml.append(transformationsXml)
        return prettify(projectXml)

    def deserializeFromXml(self, xmlString):
        project = ET.fromstring(xmlString)
        # Source
        sourceElem = project.find('source').find('storage')
        sourceProperties = extractValues(sourceElem, 'property')
        self.source = storage.MailStorageFactory(
            sourceElem.attrib['classname'],
            sourceProperties
        )
        # Target
        targetElem = project.find('target').find('storage')
        targetProperties = extractValues(targetElem, 'property')
        self.target = storage.MailStorageFactory(
            targetElem.attrib['classname'],
            targetProperties
        )
        # Transformations
        self.transformations = []
        for transElem in project.find('transformations'):
            transProperties = extractValues(transElem, 'property')
            self.transformations.append(
                transformations.TransformationFactory(
                    transElem.attrib['classname'],
                    transElem.attrib['instance'],
                    transProperties
                )
            )

    def saveToFile(self, filename=None):
        if filename:
            self.file = filename
        if self.file:
            self.changed = False
            with open(self.file, 'w') as f:
                f.write(self.serializeToXml())
        else:
            raise Exception('No file given')

    def loadFromFile(self, filename=None):
        if filename:
            self.file = filename
        if self.file:
            self.changed = False
            with open(self.file) as f:
                self.deserializeFromXml(f.read())
        else:
            raise Exception('No file given')
