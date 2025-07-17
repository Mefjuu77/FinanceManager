
# -*- coding: utf-8 -*-
from PySide6.QtCore import QCoreApplication, QDate, QMetaObject, QRect, Qt
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFormLayout, QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QWidget)

class Ui_AddTransactionDialog(object):
    def setupUi(self, AddTransactionDialog):
        if not AddTransactionDialog.objectName():
            AddTransactionDialog.setObjectName(u"AddTransactionDialog")
        AddTransactionDialog.resize(400, 250)
        self.formLayout = QFormLayout(AddTransactionDialog)
        self.formLayout.setObjectName(u"formLayout")

        # Date Field
        self.label_date = QLabel(AddTransactionDialog)
        self.label_date.setObjectName(u"label_date")
        self.date_edit = QDateEdit(AddTransactionDialog)
        self.date_edit.setObjectName(u"date_edit")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_date)
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.date_edit)

        # Description Field
        self.label_description = QLabel(AddTransactionDialog)
        self.label_description.setObjectName(u"label_description")
        self.description_edit = QLineEdit(AddTransactionDialog)
        self.description_edit.setObjectName(u"description_edit")
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_description)
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.description_edit)

        # Amount Field
        self.label_amount = QLabel(AddTransactionDialog)
        self.label_amount.setObjectName(u"label_amount")
        self.amount_spinbox = QDoubleSpinBox(AddTransactionDialog)
        self.amount_spinbox.setObjectName(u"amount_spinbox")
        self.amount_spinbox.setDecimals(2)
        self.amount_spinbox.setMaximum(9999999.99)
        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_amount)
        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.amount_spinbox)

        # Category Field
        self.label_category = QLabel(AddTransactionDialog)
        self.label_category.setObjectName(u"label_category")
        self.category_combobox = QComboBox(AddTransactionDialog)
        self.category_combobox.setObjectName(u"category_combobox")
        self.category_combobox.setEditable(True)
        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_category)
        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.category_combobox)

        # OK and Cancel Buttons
        self.button_box = QDialogButtonBox(AddTransactionDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.formLayout.setWidget(4, QFormLayout.SpanningRole, self.button_box)

        self.retranslateUi(AddTransactionDialog)
        self.button_box.accepted.connect(AddTransactionDialog.accept)
        self.button_box.rejected.connect(AddTransactionDialog.reject)

        QMetaObject.connectSlotsByName(AddTransactionDialog)

    def retranslateUi(self, AddTransactionDialog):
        AddTransactionDialog.setWindowTitle(QCoreApplication.translate("AddTransactionDialog", u"Dodaj transakcję", None))
        self.label_date.setText(QCoreApplication.translate("AddTransactionDialog", u"Data", None))
        self.label_description.setText(QCoreApplication.translate("AddTransactionDialog", u"Opis", None))
        self.label_amount.setText(QCoreApplication.translate("AddTransactionDialog", u"Kwota", None))
        self.label_category.setText(QCoreApplication.translate("AddTransactionDialog", u"Kategoria", None))
