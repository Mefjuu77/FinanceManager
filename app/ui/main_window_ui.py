# -*- coding: utf-8 -*-
from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QHeaderView, QMainWindow, QMenu,
    QMenuBar, QPushButton, QStatusBar, QTableView, QVBoxLayout, QWidget, QSplitter)
from PySide6.QtCharts import QChartView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 800)

        # Actions
        self.action_add_transaction = QAction(MainWindow)
        self.action_add_transaction.setObjectName(u"action_add_transaction")
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")

        # Central Widget and Layout
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QVBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        # Splitter
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setObjectName(u"splitter")

        # Left side (transactions)
        self.left_widget = QWidget(self.splitter)
        self.verticalLayout = QVBoxLayout(self.left_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.transactions_table_view = QTableView(self.left_widget)
        self.transactions_table_view.setObjectName(u"transactions_table_view")
        self.verticalLayout.addWidget(self.transactions_table_view)
        self.splitter.addWidget(self.left_widget)

        # Right side (chart)
        self.right_widget = QWidget(self.splitter)
        self.chart_layout = QVBoxLayout(self.right_widget)
        self.chart_layout.setObjectName(u"chart_layout")
        self.chart_view = QChartView(self.right_widget)
        self.chart_view.setObjectName(u"chart_view")
        self.chart_layout.addWidget(self.chart_view)
        self.splitter.addWidget(self.right_widget)

        self.horizontalLayout.addWidget(self.splitter)

        # Add Transaction Button
        self.add_transaction_button = QPushButton(self.left_widget)
        self.add_transaction_button.setObjectName(u"add_transaction_button")
        self.add_transaction_button.setFixedSize(60, 60)
        self.add_transaction_button.setStyleSheet(u"QPushButton { "
                                                  "background-color: #2196F3; "
                                                  "color: white; "
                                                  "border-radius: 30px; "
                                                  "font-size: 30px; "
                                                  "} "
                                                  "QPushButton:hover { "
                                                  "background-color: #1976D2; "
                                                  "}")

        MainWindow.setCentralWidget(self.centralwidget)

        # Menu Bar
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 22))
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        MainWindow.setMenuBar(self.menubar)

        # Status Bar
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Populate Menu
        self.menubar.addAction(self.menu_file.menuAction())
        self.menu_file.addAction(self.action_exit)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Inteligentny Menedżer Finansów", None))
        self.action_add_transaction.setText(QCoreApplication.translate("MainWindow", u"Dodaj transakcję", None))
        self.add_transaction_button.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"Zakończ", None))
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"Plik", None))