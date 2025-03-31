# -*- coding: utf-8 -*-
"""
Two-State Steam Calculator UI (PyQt5)

This module defines the graphical user interface (GUI) layout for a two-state steam
property calculator using PyQt5. It supports input of two thermodynamic properties
for each of two states, calculates properties using a steam table backend (e.g., pyXSteam),
and displays results for each state along with their differences.

Author: [Your Name]
Date: [Optional: YYYY-MM-DD]
"""

from PyQt5 import QtCore, QtWidgets

class Ui_frmTwoStateCalculator(object):
    def setupUi(self, frmTwoStateCalculator):
        # Configure main form
        frmTwoStateCalculator.setObjectName("frmTwoStateCalculator")
        frmTwoStateCalculator.resize(700, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(frmTwoStateCalculator)
        self.verticalLayout.setObjectName("verticalLayout")

        # ----------------- System of Units group box ------------------
        self.grpUnits = QtWidgets.QGroupBox(frmTwoStateCalculator)
        self.grpUnits.setObjectName("grpUnits")
        self.hLayoutUnits = QtWidgets.QHBoxLayout(self.grpUnits)
        self.hLayoutUnits.setObjectName("hLayoutUnits")

        # Radio button for SI units
        self.rdoSI = QtWidgets.QRadioButton(self.grpUnits)
        self.rdoSI.setChecked(True)
        self.rdoSI.setObjectName("rdoSI")
        self.hLayoutUnits.addWidget(self.rdoSI)

        # Radio button for English units
        self.rdoEnglish = QtWidgets.QRadioButton(self.grpUnits)
        self.rdoEnglish.setObjectName("rdoEnglish")
        self.hLayoutUnits.addWidget(self.rdoEnglish)

        self.verticalLayout.addWidget(self.grpUnits)

        # ----------------- Specified Properties group box -----------------
        self.grpSpecifiedProperties = QtWidgets.QGroupBox(frmTwoStateCalculator)
        self.grpSpecifiedProperties.setObjectName("grpSpecifiedProperties")
        self.hLayoutSpecified = QtWidgets.QHBoxLayout(self.grpSpecifiedProperties)

        # ----- State 1 Input Subgroup -----
        self.grpState1 = QtWidgets.QGroupBox(self.grpSpecifiedProperties)
        self.grpState1.setObjectName("grpState1")
        self.formLayoutS1 = QtWidgets.QFormLayout(self.grpState1)

        # Property 1 for State 1
        self.lblProp1S1 = QtWidgets.QLabel("Property 1", self.grpState1)
        self.cmbProp1S1 = QtWidgets.QComboBox(self.grpState1)
        self.cmbProp1S1.addItems([
            "Pressure (p)", "Temperature (T)", "Quality (x)",
            "Specific Internal Energy (u)", "Specific Enthalpy (h)",
            "Specific Volume (v)", "Specific Entropy (s)"
        ])
        self.lePropVal1S1 = QtWidgets.QLineEdit("1.0", self.grpState1)
        self.lblUnits1S1 = QtWidgets.QLabel("bar", self.grpState1)

        # Property 2 for State 1
        self.lblProp2S1 = QtWidgets.QLabel("Property 2", self.grpState1)
        self.cmbProp2S1 = QtWidgets.QComboBox(self.grpState1)
        self.cmbProp2S1.addItems([
            "Pressure (p)", "Temperature (T)", "Quality (x)",
            "Specific Internal Energy (u)", "Specific Enthalpy (h)",
            "Specific Volume (v)", "Specific Entropy (s)"
        ])
        self.cmbProp2S1.setCurrentIndex(1)
        self.lePropVal2S1 = QtWidgets.QLineEdit("100.0", self.grpState1)
        self.lblUnits2S1 = QtWidgets.QLabel("C", self.grpState1)

        # Layout input widgets for State 1
        self.formLayoutS1.addRow(self.lblProp1S1, self.cmbProp1S1)
        row1S1 = QtWidgets.QHBoxLayout()
        row1S1.addWidget(self.lePropVal1S1)
        row1S1.addWidget(self.lblUnits1S1)
        self.formLayoutS1.addRow("Value:", row1S1)

        self.formLayoutS1.addRow(self.lblProp2S1, self.cmbProp2S1)
        row2S1 = QtWidgets.QHBoxLayout()
        row2S1.addWidget(self.lePropVal2S1)
        row2S1.addWidget(self.lblUnits2S1)
        self.formLayoutS1.addRow("Value:", row2S1)

        self.hLayoutSpecified.addWidget(self.grpState1)

        # ----- State 2 Input Subgroup -----
        self.grpState2 = QtWidgets.QGroupBox(self.grpSpecifiedProperties)
        self.grpState2.setObjectName("grpState2")
        self.formLayoutS2 = QtWidgets.QFormLayout(self.grpState2)

        # Property 1 for State 2
        self.lblProp1S2 = QtWidgets.QLabel("Property 1", self.grpState2)
        self.cmbProp1S2 = QtWidgets.QComboBox(self.grpState2)
        self.cmbProp1S2.addItems([
            "Pressure (p)", "Temperature (T)", "Quality (x)",
            "Specific Internal Energy (u)", "Specific Enthalpy (h)",
            "Specific Volume (v)", "Specific Entropy (s)"
        ])
        self.lePropVal1S2 = QtWidgets.QLineEdit("1.0", self.grpState2)
        self.lblUnits1S2 = QtWidgets.QLabel("bar", self.grpState2)

        # Property 2 for State 2
        self.lblProp2S2 = QtWidgets.QLabel("Property 2", self.grpState2)
        self.cmbProp2S2 = QtWidgets.QComboBox(self.grpState2)
        self.cmbProp2S2.addItems([
            "Pressure (p)", "Temperature (T)", "Quality (x)",
            "Specific Internal Energy (u)", "Specific Enthalpy (h)",
            "Specific Volume (v)", "Specific Entropy (s)"
        ])
        self.cmbProp2S2.setCurrentIndex(1)
        self.lePropVal2S2 = QtWidgets.QLineEdit("200.0", self.grpState2)
        self.lblUnits2S2 = QtWidgets.QLabel("C", self.grpState2)

        # Layout input widgets for State 2
        self.formLayoutS2.addRow(self.lblProp1S2, self.cmbProp1S2)
        row1S2 = QtWidgets.QHBoxLayout()
        row1S2.addWidget(self.lePropVal1S2)
        row1S2.addWidget(self.lblUnits1S2)
        self.formLayoutS2.addRow("Value:", row1S2)

        self.formLayoutS2.addRow(self.lblProp2S2, self.cmbProp2S2)
        row2S2 = QtWidgets.QHBoxLayout()
        row2S2.addWidget(self.lePropVal2S2)
        row2S2.addWidget(self.lblUnits2S2)
        self.formLayoutS2.addRow("Value:", row2S2)

        self.hLayoutSpecified.addWidget(self.grpState2)

        self.verticalLayout.addWidget(self.grpSpecifiedProperties)

        # ----------------- Calculate Button -----------------
        self.pbCalculate = QtWidgets.QPushButton(frmTwoStateCalculator)
        self.pbCalculate.setObjectName("pbCalculate")
        self.verticalLayout.addWidget(self.pbCalculate)

        # ----------------- State Properties Output -----------------
        self.grpStateProperties = QtWidgets.QGroupBox(frmTwoStateCalculator)
        self.grpStateProperties.setObjectName("grpStateProperties")
        self.hLayoutStates = QtWidgets.QHBoxLayout(self.grpStateProperties)

        # Output for State 1
        self.grpResultsS1 = QtWidgets.QGroupBox(self.grpStateProperties)
        self.grpResultsS1.setObjectName("grpResultsS1")
        self.vLayoutS1 = QtWidgets.QVBoxLayout(self.grpResultsS1)
        self.lblResultsS1 = QtWidgets.QLabel("State 1 results here")
        self.vLayoutS1.addWidget(self.lblResultsS1)
        self.hLayoutStates.addWidget(self.grpResultsS1)

        # Output for State 2
        self.grpResultsS2 = QtWidgets.QGroupBox(self.grpStateProperties)
        self.grpResultsS2.setObjectName("grpResultsS2")
        self.vLayoutS2 = QtWidgets.QVBoxLayout(self.grpResultsS2)
        self.lblResultsS2 = QtWidgets.QLabel("State 2 results here")
        self.vLayoutS2.addWidget(self.lblResultsS2)
        self.hLayoutStates.addWidget(self.grpResultsS2)

        # Output for Differences
        self.grpResultsDelta = QtWidgets.QGroupBox(self.grpStateProperties)
        self.grpResultsDelta.setObjectName("grpResultsDelta")
        self.vLayoutDelta = QtWidgets.QVBoxLayout(self.grpResultsDelta)
        self.lblResultsDelta = QtWidgets.QLabel("Differences here")
        self.vLayoutDelta.addWidget(self.lblResultsDelta)
        self.hLayoutStates.addWidget(self.grpResultsDelta)

        self.verticalLayout.addWidget(self.grpStateProperties)

        # ----------------- Warning Label -----------------
        self.lblWarning = QtWidgets.QLabel(frmTwoStateCalculator)
        self.lblWarning.setStyleSheet("color: red")
        self.lblWarning.setText("")
        self.verticalLayout.addWidget(self.lblWarning)

        # Translate UI strings
        self.retranslateUi(frmTwoStateCalculator)
        QtCore.QMetaObject.connectSlotsByName(frmTwoStateCalculator)

    def retranslateUi(self, frmTwoStateCalculator):
        """Translate text for internationalization support."""
        _translate = QtCore.QCoreApplication.translate
        frmTwoStateCalculator.setWindowTitle(_translate("frmTwoStateCalculator", "Two-State Steam Calculator"))
        self.grpUnits.setTitle(_translate("frmTwoStateCalculator", "System of Units"))
        self.rdoSI.setText(_translate("frmTwoStateCalculator", "SI"))
        self.rdoEnglish.setText(_translate("frmTwoStateCalculator", "English"))

        self.grpSpecifiedProperties.setTitle(_translate("frmTwoStateCalculator", "Specified Properties"))
        self.grpState1.setTitle(_translate("frmTwoStateCalculator", "State 1"))
        self.grpState2.setTitle(_translate("frmTwoStateCalculator", "State 2"))
        self.pbCalculate.setText(_translate("frmTwoStateCalculator", "Calculate"))

        self.grpStateProperties.setTitle(_translate("frmTwoStateCalculator", "State Properties"))
        self.grpResultsS1.setTitle(_translate("frmTwoStateCalculator", "State 1"))
        self.grpResultsS2.setTitle(_translate("frmTwoStateCalculator", "State 2"))
        self.grpResultsDelta.setTitle(_translate("frmTwoStateCalculator", "State Change"))
