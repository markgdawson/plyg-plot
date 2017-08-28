# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './SimulationSelectionDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SimulationSelectionDialog(object):
    def setupUi(self, SimulationSelectionDialog):
        SimulationSelectionDialog.setObjectName("SimulationSelectionDialog")
        SimulationSelectionDialog.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(SimulationSelectionDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(SimulationSelectionDialog)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(SimulationSelectionDialog)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableView = QtWidgets.QTableView(SimulationSelectionDialog)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setObjectName("tableView")
        self.horizontalLayout.addWidget(self.tableView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadButton = QtWidgets.QPushButton(SimulationSelectionDialog)
        self.loadButton.setObjectName("loadButton")
        self.verticalLayout.addWidget(self.loadButton)
        self.deleteButton = QtWidgets.QPushButton(SimulationSelectionDialog)
        self.deleteButton.setObjectName("deleteButton")
        self.verticalLayout.addWidget(self.deleteButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.status = QtWidgets.QLabel(SimulationSelectionDialog)
        self.status.setObjectName("status")
        self.horizontalLayout_2.addWidget(self.status)
        self.buttonBox = QtWidgets.QDialogButtonBox(SimulationSelectionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(SimulationSelectionDialog)
        self.buttonBox.accepted.connect(SimulationSelectionDialog.accept)
        self.buttonBox.rejected.connect(SimulationSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SimulationSelectionDialog)

    def retranslateUi(self, SimulationSelectionDialog):
        _translate = QtCore.QCoreApplication.translate
        SimulationSelectionDialog.setWindowTitle(_translate("SimulationSelectionDialog", "Simulation Import"))
        self.label.setText(_translate("SimulationSelectionDialog", "Select from simulation list or load a new simulation."))
        self.label_2.setText(_translate("SimulationSelectionDialog", "hint: double click simulation name to rename"))
        self.loadButton.setText(_translate("SimulationSelectionDialog", "Load..."))
        self.deleteButton.setText(_translate("SimulationSelectionDialog", "Delete"))
        self.status.setText(_translate("SimulationSelectionDialog", "<Nothing Selected>"))

