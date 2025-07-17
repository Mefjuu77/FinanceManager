import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenu, QMessageBox, 
    QLineEdit, QComboBox, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QDoubleSpinBox, QToolTip, QProgressBar, QInputDialog, QPushButton, QAbstractItemView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPainter, QCursor, QAction
from PySide6.QtCore import Qt, QSortFilterProxyModel, QDate, QSize, QTimer, QCoreApplication
from PySide6.QtCharts import QChart, QPieSeries
from app.ui.main_window_ui import Ui_MainWindow
from app.add_transaction_dialog import AddTransactionDialog
from app.database import database as db
from app.ui.onboarding_window import OnboardingWindow

class TransactionFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_description = ""
        self.filter_categories = []

    def set_filter_description(self, description):
        self.filter_description = description.lower()
        self.invalidateFilter()

    def set_filter_categories(self, categories):
        self.filter_categories = categories
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        description_index = self.sourceModel().index(source_row, 2, source_parent)
        category_index = self.sourceModel().index(source_row, 4, source_parent)

        description = self.sourceModel().data(description_index).lower()
        category = self.sourceModel().data(category_index)

        description_match = self.filter_description in description
        
        if not self.filter_categories:
            category_match = True
        else:
            category_match = category in self.filter_categories

        return description_match and category_match

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.chart_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]

        # Add summary widgets
        summary_layout = QHBoxLayout()
        # self.total_expenses_label = QLabel("Suma wydatków: 0.00")
        # summary_layout.addWidget(self.total_expenses_label)

        # Add budget widgets
        budget_layout = QVBoxLayout()
        self.budget_label = QLabel("Budżet miesięczny: 0.00 / 0.00 PLN")
        self.budget_progress_bar = QProgressBar()
        self.budget_progress_bar.setRange(0, 100)
        self.budget_progress_bar.setValue(0)
        budget_layout.addWidget(self.budget_label)
        budget_layout.addWidget(self.budget_progress_bar)

        # Add filter widgets
        filter_layout = QVBoxLayout()
        self.description_filter = QLineEdit()
        self.description_filter.setPlaceholderText("Filtruj po opisie...")
        self.category_filter = QComboBox()

        filter_layout.addWidget(QLabel("Filtrowanie:"))
        filter_layout.addWidget(self.description_filter)
        filter_layout.addWidget(self.category_filter)

        # Add the layouts to the main layout
        self.verticalLayout.insertLayout(0, summary_layout)
        self.verticalLayout.insertLayout(1, budget_layout)
        self.verticalLayout.insertLayout(2, filter_layout)

        # Add a back button for the chart
        self.chart_back_button = QPushButton("Wróć")
        self.chart_back_button.setVisible(False)
        self.chart_layout.insertWidget(0, self.chart_back_button)

        self.action_exit.triggered.connect(self.close)
        self.action_factory_reset = QAction("Przywróć ustawienia fabryczne", self)
        self.action_factory_reset.triggered.connect(self.factory_reset)
        self.menu_file.addAction(self.action_factory_reset)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)

        self.add_transaction_button.clicked.connect(self.show_add_transaction_dialog)
        self.description_filter.textChanged.connect(self.apply_filters)
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        self.chart_back_button.clicked.connect(self.show_main_chart)

        # Enable context menu
        self.transactions_table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.transactions_table_view.customContextMenuRequested.connect(self.show_context_menu)
        self.transactions_table_view.setSortingEnabled(True)

        # Apply styling to the transactions table
        self.transactions_table_view.setStyleSheet("""
            QTableView {
                background-color: #424242;
                alternate-background-color: #505050;
                color: white;
                selection-background-color: #1a75ff;
                gridline-color: #5a5a5a;
            }
            QHeaderView::section {
                background-color: #303030;
                color: white;
                padding: 4px;
                border: 1px solid #5a5a5a;
                font-weight: bold;
            }
        """)
        self.transactions_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.current_chart_category = None
        self.chart_filter_categories = []
        self.load_transactions()
        self.apply_filters()
        QTimer.singleShot(0, self.update_button_position)

    def update_button_position(self):
        button_size = int(self.left_widget.width() * 0.10)
        button_size = max(40, min(button_size, 70))
        
        # Pozycjonowanie przycisku dodawania transakcji
        self.add_transaction_button.setFixedSize(button_size, button_size)
        border_radius = button_size // 2
        font_size = button_size // 2
        self.add_transaction_button.setStyleSheet(f"""QPushButton {{
                                                  background-color: #2196F3; color: white;
                                                  border-radius: {border_radius}px; font-size: {font_size}px;
                                                  }}
                                                  QPushButton:hover {{ background-color: #1976D2; }}""")
        self.add_transaction_button.move(self.left_widget.width() - button_size - 20, self.left_widget.height() - button_size - 20)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_button_position()

    def load_transactions(self):
        """Loads transactions and categories."""
        transactions = db.get_all_transactions()
        self.model = QStandardItemModel(len(transactions), 5)
        self.model.setHorizontalHeaderLabels(['ID', 'Data', 'Opis', 'Kwota', 'Kategoria'])

        for row, transaction in enumerate(transactions):
            id_item = QStandardItem(str(transaction['id']))
            date_item = QStandardItem(transaction['date'])
            description_item = QStandardItem(transaction['description'])
            amount_item = QStandardItem(f"{transaction['amount']:.2f}")
            category_item = QStandardItem(transaction['category'])
            self.model.setItem(row, 0, id_item)
            self.model.setItem(row, 1, date_item)
            self.model.setItem(row, 2, description_item)
            self.model.setItem(row, 3, amount_item)
            self.model.setItem(row, 4, category_item)

        self.proxy_model = TransactionFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.transactions_table_view.setModel(self.proxy_model)
        self.transactions_table_view.hideColumn(0)

        # Right-align the amount column and resize columns
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 3) # Column 3 is 'Kwota'
            if item:
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.transactions_table_view.resizeColumnsToContents()

        # Populate category filter with hierarchy
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("Wszystkie kategorie")
        categories = db.get_all_categories()
        categories_by_parent = {None: []}
        for cat in categories:
            parent_id = cat['parent_id']
            if parent_id not in categories_by_parent:
                categories_by_parent[parent_id] = []
            categories_by_parent[parent_id].append(cat)

        def add_items_recursively(parent_id, indent_level=0):
            if parent_id in categories_by_parent:
                for cat in sorted(categories_by_parent[parent_id], key=lambda x: x['name']):
                    self.category_filter.addItem("  " * indent_level + cat['name'])
                    add_items_recursively(cat['id'], indent_level + 1)
        add_items_recursively(None)
        self.category_filter.blockSignals(False)

    def get_categories_from_combobox(self):
        """Gets the category filter list from the combobox selection."""
        selected_index = self.category_filter.currentIndex()
        if selected_index <= 0:
            return []
        
        selected_category_name = self.category_filter.currentText().strip()
        categories_to_filter = [selected_category_name]
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = ?", (selected_category_name,))
        result = cursor.fetchone()
        if result is None:
            conn.close()
            return categories_to_filter
        
        category_id = result[0]
        cursor.execute("SELECT name FROM categories WHERE parent_id = ?", (category_id,))
        subcategories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories_to_filter + subcategories

    def apply_filters(self):
        """Applies all active filters to the transaction view."""
        self.proxy_model.set_filter_description(self.description_filter.text())

        # Get categories for table filter from the combobox selection
        categories_for_table = self.get_categories_from_combobox()
        self.proxy_model.set_filter_categories(categories_for_table)

        # Check if the selected category is a parent to set the chart state
        selected_category_name = self.category_filter.currentText().strip()
        
        # A parent category will have its subcategories in the list.
        # A child category will only have itself. "All categories" is an empty list.
        if len(categories_for_table) > 1:
            self.current_chart_category = selected_category_name
        else:
            self.current_chart_category = None

        self.update_chart()
        self.update_budget_display()

    def show_context_menu(self, pos):
        proxy_index = self.transactions_table_view.indexAt(pos)
        if not proxy_index.isValid():
            return
        source_index = self.proxy_model.mapToSource(proxy_index)
        menu = QMenu(self)
        edit_action = menu.addAction("Edytuj")
        delete_action = menu.addAction("Usuń")
        action = menu.exec(self.transactions_table_view.viewport().mapToGlobal(pos))
        if action == edit_action:
            self.edit_transaction(source_index)
        elif action == delete_action:
            self.delete_transaction(source_index)

    def edit_transaction(self, index):
        model = self.model
        transaction_id = int(model.item(index.row(), 0).text())
        transaction_data = {
            'date': model.item(index.row(), 1).text(),
            'description': model.item(index.row(), 2).text(),
            'amount': float(model.item(index.row(), 3).text()),
            'category': model.item(index.row(), 4).text()
        }
        dialog = AddTransactionDialog(self, transaction_data)
        if dialog.exec():
            new_data = dialog.get_transaction_data()
            db.update_transaction(transaction_id, new_data)
            self.load_transactions()
            self.apply_filters()

    def delete_transaction(self, index):
        model = self.model
        transaction_id = int(model.item(index.row(), 0).text())
        reply = QMessageBox.question(self, "Potwierdzenie", 
                                     "Czy na pewno chcesz usunąć tę transakcję?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            db.delete_transaction(transaction_id)
            self.load_transactions()
            self.apply_filters()

    def show_add_transaction_dialog(self):
        dialog = AddTransactionDialog(self)
        if dialog.exec():
            data = dialog.get_transaction_data()
            db.add_transaction(data)
            self.load_transactions()
            self.apply_filters()

    def update_budget_display(self):
        today = QDate.currentDate()
        current_month = today.month()
        current_year = today.year()
        budget = db.get_budget_for_month(current_month, current_year)
        total_expenses_this_month = 0
        for row in range(self.proxy_model.rowCount()):
            date_index = self.proxy_model.index(row, 1)
            amount_index = self.proxy_model.index(row, 3)
            transaction_date_str = self.proxy_model.data(date_index)
            transaction_date = QDate.fromString(transaction_date_str, "yyyy-MM-dd")
            if transaction_date.month() == current_month and transaction_date.year() == current_year:
                total_expenses_this_month += float(self.proxy_model.data(amount_index))
        if budget is not None:
            self.budget_label.setText(f"Budżet miesięczny: {total_expenses_this_month:.2f} / {budget:.2f} PLN")
            progress = int((total_expenses_this_month / budget) * 100) if budget > 0 else 0
            self.budget_progress_bar.setValue(progress)
            self.budget_progress_bar.setFormat(f"{progress}%")
            color = "#4CAF50"
            if progress <= 75: color = "#4CAF50"
            elif progress <= 100: color = "#FBC02D"
            else: color = "#D32F2F"
            self.budget_progress_bar.setStyleSheet(f"""QProgressBar {{ border: 1px solid #A0A0A0; border-radius: 5px; text-align: center; background-color: #E8E8E8; font-weight: bold; font-size: 10pt; color: black; }} QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}""")
        else:
            self.budget_label.setText("Budżet miesięczny: Brak budżetu na ten miesiąc")
            self.budget_progress_bar.setValue(0)
            self.budget_progress_bar.setFormat("Brak budżetu")
            self.budget_progress_bar.setStyleSheet("")

    def on_slice_clicked(self, slice):
        category_name = slice.property("original_category")
        if category_name == "Inne":
            return

        # Find the category in the combobox and select it.
        # This will trigger apply_filters and update the chart correctly.
        for i in range(self.category_filter.count()):
            if self.category_filter.itemText(i).strip() == category_name:
                self.category_filter.setCurrentIndex(i)
                return

    def show_main_chart(self):
        self.category_filter.setCurrentIndex(0)

    def update_chart(self):
        expenses_by_category = {}
        if self.current_chart_category is None:
            self.chart_back_button.setVisible(False)
            chart_title = "Wydatki według kategorii"
            conn = db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT c.name, p.name FROM categories c JOIN categories p ON c.parent_id = p.id")
            sub_to_parent = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()
            for row in range(self.proxy_model.rowCount()):
                amount_index = self.proxy_model.index(row, 3)
                category_index = self.proxy_model.index(row, 4)
                amount = float(self.proxy_model.data(amount_index))
                category = self.proxy_model.data(category_index)
                main_category = sub_to_parent.get(category, category)
                if main_category not in expenses_by_category:
                    expenses_by_category[main_category] = 0
                expenses_by_category[main_category] += amount
        else:
            self.chart_back_button.setVisible(True)
            chart_title = f"Wydatki: {self.current_chart_category}"
            conn = db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM categories WHERE name = ?", (self.current_chart_category,))
            parent_id_result = cursor.fetchone()
            if parent_id_result:
                parent_id = parent_id_result[0]
                cursor.execute("SELECT name FROM categories WHERE parent_id = ?", (parent_id,))
                sub_categories = [row[0] for row in cursor.fetchall()]
                for row in range(self.proxy_model.rowCount()):
                    category_index = self.proxy_model.index(row, 4)
                    category = self.proxy_model.data(category_index)
                    if category in sub_categories:
                        amount_index = self.proxy_model.index(row, 3)
                        amount = float(self.proxy_model.data(amount_index))
                        if category not in expenses_by_category:
                            expenses_by_category[category] = 0
                        expenses_by_category[category] += amount
            conn.close()

        series = QPieSeries()
        series.setHoleSize(0.35)
        total_expenses = sum(expenses_by_category.values())
        if total_expenses > 0:
            other_amount = 0
            color_index = 0
            for category, amount in expenses_by_category.items():
                percentage = 100 * amount / total_expenses
                if percentage < 2 and self.current_chart_category is None:
                    other_amount += amount
                else:
                    slice_ = series.append(category, amount)
                    slice_.setProperty("original_category", category)
                    slice_.setColor(self.chart_colors[color_index % len(self.chart_colors)])
                    color_index += 1
            if other_amount > 0:
                slice_ = series.append("Inne", other_amount)
                slice_.setProperty("original_category", "Inne")
                slice_.setColor(self.chart_colors[color_index % len(self.chart_colors)])

        series.hovered.connect(self.on_series_hovered)
        series.clicked.connect(self.on_slice_clicked)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(chart_title)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        font = chart.legend().font()
        font.setPointSize(8)
        chart.legend().setFont(font)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view.setChart(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

    def on_series_hovered(self, slice, state):
        if state:
            category_name = slice.property("original_category")
            tooltip_text = f"{category_name}: {slice.value():.2f} zł"
            QToolTip.showText(QCursor.pos(), tooltip_text)
        else:
            QToolTip.hideText()

    def factory_reset(self):
        reply = QMessageBox.question(self, "Potwierdzenie",
                                     "Czy na pewno chcesz przywrócić ustawienia fabryczne?\n"
                                     "Wszystkie dane zostaną usunięte.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            db_path = os.path.join(os.path.dirname(__file__), 'data', 'finance.db')
            if os.path.exists(db_path):
                os.remove(db_path)
            QCoreApplication.quit()
            os.execl(sys.executable, sys.executable, *sys.argv)

def main():
    db.initialize_database()
    app = QApplication(sys.argv)

    if not db.is_onboarding_complete():
        onboarding_window = OnboardingWindow()
        if onboarding_window.exec():
            window = MainWindow()
            window.show()
            sys.exit(app.exec())
        else:
            sys.exit(0)
    else:
        today = QDate.currentDate()
        current_month = today.month()
        current_year = today.year()
        budget = db.get_budget_for_month(current_month, current_year)
        if budget is None:
            budget_amount, ok = QInputDialog.getDouble(
                None, 
                "Ustaw budżet miesięczny", 
                f"Nie ustawiono jeszcze budżetu na {current_month}/{current_year}.\nCzy chcesz go teraz zdefiniować?",
                1000.00, 0.00, 1000000.00, 2
            )
            if ok:
                db.set_budget_for_month(budget_amount, current_month, current_year)

        window = MainWindow()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()