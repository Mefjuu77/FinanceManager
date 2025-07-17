import re
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QStackedWidget, QWidget, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTreeWidget, QTreeWidgetItem, QMessageBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QDate
from app.database import database as db

class OnboardingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Witaj w FinanceManager!")
        self.setMinimumSize(400, 300)

        self.layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()

        self.init_step1()
        self.init_step2()
        self.init_step3()

        self.layout.addWidget(self.stacked_widget)

    def init_step1(self):
        step1_widget = QWidget()
        layout = QVBoxLayout(step1_widget)
        layout.setAlignment(Qt.AlignCenter)

        welcome_label = QLabel("Witaj w FinanceManager!\n\nSkonfigurujmy Twoją aplikację.")
        welcome_label.setAlignment(Qt.AlignCenter)

        next_button = QPushButton("Dalej")
        next_button.clicked.connect(self.next_step)

        layout.addWidget(welcome_label)
        layout.addWidget(next_button)

        self.stacked_widget.addWidget(step1_widget)

    def init_step2(self):
        step2_widget = QWidget()
        layout = QVBoxLayout(step2_widget)

        categories_label = QLabel("Zarządzaj kategoriami wydatków:")
        self.categories_tree = QTreeWidget()
        self.categories_tree.setHeaderLabels(["Kategoria", "ID"])
        self.categories_tree.setColumnHidden(1, True)

        self.populate_categories()

        add_category_button = QPushButton("Dodaj kategorię")
        add_category_button.clicked.connect(self.add_category)

        delete_category_button = QPushButton("Usuń kategorię")
        delete_category_button.clicked.connect(self.delete_category)

        next_button = QPushButton("Dalej")
        next_button.clicked.connect(self.next_step)

        layout.addWidget(categories_label)
        layout.addWidget(self.categories_tree)
        layout.addWidget(add_category_button)
        layout.addWidget(delete_category_button)
        layout.addWidget(next_button)

        self.stacked_widget.addWidget(step2_widget)

    def init_step3(self):
        step3_widget = QWidget()
        layout = QVBoxLayout(step3_widget)
        layout.setAlignment(Qt.AlignCenter)

        budget_label = QLabel("Podaj swój miesięczny budżet:")
        self.budget_spinbox = QDoubleSpinBox()
        self.budget_spinbox.setRange(0, 1000000)
        self.budget_spinbox.setValue(1000)

        finish_button = QPushButton("Zakończ")
        finish_button.clicked.connect(self.finish_onboarding)

        layout.addWidget(budget_label)
        layout.addWidget(self.budget_spinbox)
        layout.addWidget(finish_button)

        self.stacked_widget.addWidget(step3_widget)

    def populate_categories(self):
        self.categories_tree.clear()
        categories = db.get_all_categories()
        
        category_items = {}
        for category in categories:
            if category['parent_id'] is None:
                item = QTreeWidgetItem(self.categories_tree, [category['name'], str(category['id'])])
                category_items[category['id']] = item

        for category in categories:
            if category['parent_id'] is not None:
                parent_item = category_items.get(category['parent_id'])
                if parent_item:
                    QTreeWidgetItem(parent_item, [category['name'], str(category['id'])])

    def add_category(self):
        # Simple dialog to add a category
        dialog = QDialog(self)
        dialog.setWindowTitle("Dodaj kategorię")
        layout = QVBoxLayout(dialog)
        
        name_label = QLabel("Nazwa kategorii:")
        name_input = QLineEdit()
        parent_label = QLabel("Kategoria nadrzędna (opcjonalnie):")
        parent_combo = QComboBox()
        parent_combo.addItem("Brak", None)

        for item in db.get_all_categories():
            if item['parent_id'] is None:
                parent_combo.addItem(item['name'], item['id'])

        add_button = QPushButton("Dodaj")

        layout.addWidget(name_label)
        layout.addWidget(name_input)
        layout.addWidget(parent_label)
        layout.addWidget(parent_combo)
        layout.addWidget(add_button)

        def do_add():
            name = name_input.text().strip()
            parent_id = parent_combo.currentData()

            # Validation rules
            if not name:
                QMessageBox.warning(dialog, "Błąd walidacji", "Nazwa kategorii nie może być pusta.")
                return
            if len(name) > 50:
                QMessageBox.warning(dialog, "Błąd walidacji", "Nazwa kategorii nie może przekraczać 50 znaków.")
                return
            if not re.match(r'^[a-zA-Z0-9 ]+$', name):
                QMessageBox.warning(dialog, "Błąd walidacji", "Nazwa kategorii może zawierać tylko litery, cyfry i spacje.")
                return

            # Check for uniqueness
            existing_categories = [cat['name'].lower() for cat in db.get_all_categories()]
            if name.lower() in existing_categories:
                QMessageBox.warning(dialog, "Błąd walidacji", "Kategoria o tej nazwie już istnieje.")
                return

            db.add_category(name, parent_id)
            self.populate_categories()
            dialog.accept()

        add_button.clicked.connect(do_add)
        dialog.exec()

    def delete_category(self):
        selected_item = self.categories_tree.currentItem()
        if selected_item:
            category_id = int(selected_item.text(1))
            db.delete_category(category_id)
            self.populate_categories()
        else:
            QMessageBox.warning(self, "Błąd", "Wybierz kategorię do usunięcia.")

    def next_step(self):
        current_index = self.stacked_widget.currentIndex()
        self.stacked_widget.setCurrentIndex(current_index + 1)

    def finish_onboarding(self):
        budget = self.budget_spinbox.value()
        today = QDate.currentDate()
        db.set_budget_for_month(budget, today.month(), today.year())
        db.set_main_currency("PLN")
        db.set_onboarding_complete()
        self.accept()