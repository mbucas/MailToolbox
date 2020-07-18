#!/usr/bin/python
# coding:utf8

import sys
import os

from PyQt5 import Qt, QtCore, QtGui, QtWidgets, uic

from config import config
from project import project
from storage import storage
from transformations import transformations
from engine import engine


def showText(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf8'))


class DataDelegate(QtWidgets.QItemDelegate):

    def setPropertiesDescriptions(self, properties):
        self.properties = properties
        self.hidden = {}

    def getPropertyDesc(self, index):
        propertyLabelIndex = index.model().index(
            index.row(),
            0,
            QtCore.QModelIndex()
        )
        propertyLabel = index.model().data(
            propertyLabelIndex,
            QtCore.Qt.EditRole
        )
        return [p for p in self.properties if p['label'] == propertyLabel][0]

    def createEditor(self, parent, option, index):
        if index.column() != 1:
            return None
        propertyDesc = self.getPropertyDesc(index)
        if propertyDesc['content'] == 'string':
            return QtWidgets.QLineEdit(parent)
        elif propertyDesc['content'] == 'hidden':
            edit = QtWidgets.QLineEdit(parent)
            # As the Treeview doesn't hide data,
            # it's useless to hide it in the editor
            return edit
        elif propertyDesc['content'] == 'list':
            comboBox = QtWidgets.QComboBox(parent)
            for e in propertyDesc['values']:
                comboBox.addItem(e)
            return comboBox

    def setEditorData(self, widget, index):
        if index.column() != 1:
            return None
        value = index.model().data(index, QtCore.Qt.EditRole)
        propertyDesc = self.getPropertyDesc(index)
        if propertyDesc['content'] == 'string':
            # QLineEdit
            widget.setText(str(value))
        if propertyDesc['content'] == 'hidden':
            # QLineEdit
            # TODO : Hide data
            widget.setText(str(value))
        elif propertyDesc['content'] == 'list':
            # QComboBox
            widget.setCurrentIndex(widget.findText(str(value)))

    def setModelData(self, widget, model, index):
        if index.column() != 1:
            return None
        propertyDesc = self.getPropertyDesc(index)
        if propertyDesc['content'] == 'string':
            value = widget.text()  # QLineEdit
            model.setData(index, value, QtCore.Qt.EditRole)
        elif propertyDesc['content'] == 'hidden':
            value = widget.text()  # QLineEdit
            # TODO : Hide data
            model.setData(index, value, QtCore.Qt.EditRole)
        elif propertyDesc['content'] == 'list':
            value = widget.currentText()  # QComboBox
            model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, widget, option, index):
        widget.setGeometry(option.rect)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, appName, config, project):
        super(MainWindow, self).__init__()
        # Load interface
        self.ui = uic.loadUi("ui/mainwindow.ui", self)
        self.setWindowIcon(QtGui.QIcon("ui/icon.png"))

        # Project menu
        self.ui.actionNew.triggered.connect(self.newProject)
        self.ui.actionOpen.triggered.connect(self.openProject)
        self.ui.actionSave.triggered.connect(self.saveProject)
        self.ui.actionSave_as.triggered.connect(self.saveAsProject)

        # Execute menu
        self.ui.actionRun.triggered.connect(self.runProject)

        # Help menu
        self.ui.actionAbout.triggered.connect(self.about)

        # Model
        self.model = QtGui.QStandardItemModel(1, 3)
        # At last https://stackoverflow.com/questions/56603496/
        # qtreeview-data-changed-signal-slot-implementation
        self.model.dataChanged.connect(self.onDataChanged)

        # Prepare property editor
        self.ui.treeView.setModel(self.model)
        self.ui.treeView.setSelectionBehavior(self.ui.treeView.SelectRows)
        self.delegate = DataDelegate()
        self.ui.treeView.setItemDelegate(self.delegate)

        # Set internal values
        self.appName = appName
        self.config = config
        self.restoreConfig()
        self.transCounter = 0
        self.currentProject = project
        if self.currentProject.file:
            self.config.lastProject = self.currentProject.file
            self.setProjectNameInTitle()
        self.setProjectWidgets()

    def setProjectNameInTitle(self):
        if self.config.lastProject:
            title = (
                os.path.basename(self.config.lastProject)
                + ' - '
                + self.appName
            )
        else:
            title = self.appName
        self.setWindowTitle(title)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def clearProperties(self):
        model = self.ui.treeView.model()
        model.clear()
        model.setHorizontalHeaderLabels(("Property", "Value", "Description"))

    def insertArrowWidget(self, layout, pos):
        arrowFrame = QtWidgets.QFrame()
        arrowFrame.setMinimumSize(120, 120)
        arrowFrame.setMaximumSize(120, 120)
        arrowLayout = QtWidgets.QVBoxLayout()
        arrowLayout.setContentsMargins(0, 0, 0, 0)
        arrowFrame.setLayout(arrowLayout)

        label = QtWidgets.QLabel("->")
        label.setFont(Qt.QFont("Courier New", 26, Qt.QFont.Bold))
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setMinimumSize(119, 80)
        label.setMaximumSize(119, 80)
        arrowFrame.layout().addWidget(label)

        insertButton = QtWidgets.QPushButton("Insert\nTransformation")
        insertButton.clicked.connect(self.insertTransformation)
        insertButton.setMinimumSize(119, 0)
        insertButton.setMaximumSize(119, 16777215)
        arrowFrame.layout().addWidget(insertButton)

        layout.insertWidget(pos, arrowFrame)

    def insertStorageWidget(self, objectName, layout, pos):
        storageButton = QtWidgets.QPushButton(objectName)
        storageButton.setObjectName(objectName)
        storageButton.clicked.connect(self.showStorageProperties)
        font = storageButton.font()
        font.setPointSize(12)
        storageButton.setFont(font)
        storageButton.setMinimumSize(120, 120)
        storageButton.setMaximumSize(120, 120)

        layout.insertWidget(pos, storageButton)

    def insertTransformationWidget(self, insertIndex, transformation, objectName):
        layout = self.scrollAreaWidgetContents.layout()

        newFrame = QtWidgets.QFrame()
        newFrame.setMinimumSize(120, 120)
        newFrame.setMaximumSize(120, 120)
        newLayout = QtWidgets.QVBoxLayout()
        newLayout.setContentsMargins(0, 0, 0, 0)
        newFrame.setLayout(newLayout)

        transformationButton = QtWidgets.QPushButton("Transformation")
        transformationButton.setObjectName(objectName)
        transformation.buttonName = transformationButton.objectName()
        transformationButton.clicked.connect(
            self.showTransformationProperties
        )
        font = transformationButton.font()
        font.setPointSize(12)
        transformationButton.setFont(font)
        transformationButton.setMinimumSize(120, 100)
        transformationButton.setMaximumSize(120, 100)
        newFrame.layout().addWidget(transformationButton)

        delButton = QtWidgets.QPushButton("Delete")
        delButton.clicked.connect(self.deleteTransformation)
        delButton.setMinimumSize(120, 20)
        delButton.setMaximumSize(120, 20)
        newFrame.layout().addWidget(delButton)

        layout.insertWidget(insertIndex + 1, newFrame)

        self.insertArrowWidget(layout, insertIndex + 2)

    def deleteTransformationWidget(self, index):
        layout = self.scrollAreaWidgetContents.layout()
        # Arrow and insert button
        item = layout.takeAt(index + 1)
        item.widget().hide()
        item.widget().destroy()

        # The transformation itself
        item = layout.takeAt(index)
        item.widget().hide()
        item.widget().destroy()

    def setProjectWidgets(self):
        layout = self.scrollAreaWidgetContents.layout()
        self.clearLayout(layout)
        self.clearProperties()

        self.insertStorageWidget("Source", layout, 0)
        self.insertArrowWidget(layout, 1)
        self.insertStorageWidget("Target", layout, 2)

        for trans in reversed(self.currentProject.transformations):
            self.insertTransformationWidget(1, trans, trans.instance)

    def deleteTransformation(self):
        # Visual part
        frame = self.sender().parentWidget()
        layout = self.scrollAreaWidgetContents.layout()
        index = layout.indexOf(frame)

        self.deleteTransformationWidget(index)
        self.clearProperties()

        # Project
        self.currentProject.changed = True
        removePosition = int(((index + 1) / 2) - 1)
        self.currentProject.transformations.pop(removePosition)

    def insertTransformation(self):
        # Generate a unique name to insert
        objectName = "Transformation" + str(self.transCounter)
        self.transCounter += 1

        # Where to insert
        frame = self.sender().parentWidget()
        layout = self.scrollAreaWidgetContents.layout()
        index = layout.indexOf(frame)
        insertPosition = int(((index + 1) / 2) - 1)

        # Project part
        self.currentProject.changed = True

        transformation = transformations.NoTransformation(
            objectName,
            properties={
                'name': objectName,
                'transformationtype': "NoTransformation",
            }
        )
        self.currentProject.transformations.insert(
            insertPosition,
            transformation
        )

        # Visual part
        self.insertTransformationWidget(index, transformation, objectName)

    def addRow(self, model, name, value, description):
        items = []

        for data in (name, value, description):
            it = QtGui.QStandardItem()
            it.setData(data, QtCore.Qt.DisplayRole)
            items.append(it)

        model.appendRow(items)

    def onDataChanged(self, index1, index2):
        self.currentProject.changed = True
        prop = self.delegate.getPropertyDesc(index1)
        value = str(
            index1
            .model()
            .data(
                index1,
                QtCore.Qt.EditRole
            )
        )
        if prop['key'] == 'storagetype':
            # Replace current storage object by new one
            if self.currentElementName == 'Source':
                self.currentProject.source = storage.MailStorageFactory(
                    value,
                    self.currentElement.properties
                )
                self.currentElement = self.currentProject.source
            else:  # Target
                self.currentProject.target = storage.MailStorageFactory(
                    value,
                    self.currentElement.properties
                )
                self.currentElement = self.currentProject.target
            self.currentElement.properties['storagetype'] = value
            self.showCurrentElementProperties()
        elif prop['key'] == 'transformationtype':
            # Replace current transformation object by new one
            self.currentElement = transformations.TransformationFactory(
                value,
                self.currentElementName,
                self.currentElement.properties
            )
            # Replace in the transformation list of the project
            self.currentProject.transformations = [
                tr
                if tr.instance != self.currentElementName
                else self.currentElement
                for tr in self.currentProject.transformations
            ]
            self.currentElement.properties['transformationtype'] = value
            self.showCurrentElementProperties()
        else:
            # Simply update the property
            self.currentElement.properties[prop['key']] = value

    def showCurrentElementProperties(self):
        self.clearProperties()
        model = self.ui.treeView.model()
        self.delegate.setPropertiesDescriptions(
            self.currentElement.expectedProperties
        )
        for prop in self.currentElement.expectedProperties:
            if prop['key'] in self.currentElement.properties:
                val = self.currentElement.properties[prop['key']]
            else:
                val = ''
            self.addRow(
                model,
                prop['label'],
                val,
                prop['desc']
            )

    def showTransformationProperties(self):
        self.currentElementName = self.sender().objectName()
        for tr in self.currentProject.transformations:
            if tr.instance == self.currentElementName:
                self.currentElement = tr
                break
        self.showCurrentElementProperties()

    def showStorageProperties(self):
        self.currentElementName = self.sender().objectName()
        if self.currentElementName == 'Source':
            self.currentElement = self.currentProject.source
        else:  # Target
            self.currentElement = self.currentProject.target
        self.showCurrentElementProperties()

    def restoreConfig(self):
        # Position window as last time
        if self.config.windowState == 'Maximized':
            self.setWindowState(QtCore.Qt.WindowMaximized)
        else:
            if self.config.windowPos:
                (x, y) = [int(n) for n in self.config.windowPos.split('x')]
            else:
                (x, y) = (50, 50)
            if self.config.windowSize:
                (w, h) = [int(n) for n in self.config.windowSize.split('x')]
            else:
                (w, h) = (800, 600)
            self.setGeometry(x, y + 23, w, h)

    def saveConfig(self):
        # Window State
        if int(self.windowState()) & QtCore.Qt.WindowMaximized:
            self.config.windowState = 'Maximized'
        else:
            self.config.windowState = 'Normal'
        # Window position and size
        self.config.windowPos = (
            str(self.pos().x())
            + 'x'
            + str(self.pos().y())
        )
        self.config.windowSize = (
            str(self.size().width())
            + 'x'
            + str(self.size().height())
        )

    def newProject(self):
        self.currentProject = project.Project()
        self.setProjectWidgets()
        self.config.lastProject = None
        self.setProjectNameInTitle()

    def openProject(self):
        file, ext_type = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Project File",
            QtCore.QDir.currentPath(),
            "XML Files (*.xml)"
        )
        self.currentProject = project.Project()
        self.currentProject.loadFromFile(file)
        self.setProjectWidgets()
        self.config.lastProject = file
        self.setProjectNameInTitle()

    def saveProject(self):
        if self.currentProject.file:
            self.currentProject.saveToFile()
        else:
            self.saveAsProject()

    def saveAsProject(self):
        file, ext_type = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Project File",
            QtCore.QDir.currentPath(),
            "XML Files (*.xml)"
        )
        self.currentProject.saveToFile(file)
        self.config.lastProject = file
        self.setProjectNameInTitle()

    def runProject(self):
        self.saveProject()
        print("Starting")
        runnerEngine = engine.Engine(self.currentProject, showText)
        runnerEngine.run()
        print("Finished")

    def about(self, sender):
        box = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Information,
            "About " + self.appName,
            self.appName + u" © 2012 Mickaël Bucas",
            QtWidgets.QMessageBox.Ok
        )
        box.setWindowIcon(
            QtWidgets.QIcon(
                os.path.join(os.path.dirname(__file__), "icon.png")
            )
        )
        box.setInformativeText(self.appName + " is a toolbox to move mail")
        box.exec_()


def show(appName, config, project):
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow(appName, config, project)
    mainWindow.show()
    app.exec_()
    mainWindow.saveConfig()
