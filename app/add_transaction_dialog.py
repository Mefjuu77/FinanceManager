from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QDate
from .ui.add_transaction_dialog_ui import Ui_AddTransactionDialog
from .database import database as db

class AddTransactionDialog(QDialog, Ui_AddTransactionDialog):
    def __init__(self, parent=None, transaction_data=None):
        super().__init__(parent)
        self.setupUi(self)

        self.load_categories()

        if transaction_data:
            self.date_edit.setDate(QDate.fromString(transaction_data['date'], "yyyy-MM-dd"))
            self.description_edit.setText(transaction_data['description'])
            self.amount_spinbox.setValue(transaction_data['amount'])
            self.category_combobox.setCurrentText(transaction_data['category'])

    def load_categories(self):
        """Loads categories from the database and populates the combobox with hierarchy."""
        self.category_combobox.clear()
        
        categories = db.get_all_categories()
        categories_by_parent = {None: []}
        has_children = set()

        for cat in categories:
            parent_id = cat['parent_id']
            if parent_id is not None:
                has_children.add(parent_id)
            if parent_id not in categories_by_parent:
                categories_by_parent[parent_id] = []
            categories_by_parent[parent_id].append(cat)

        def add_items_recursively(parent_id, indent_level=0):
            if parent_id in categories_by_parent:
                for cat in sorted(categories_by_parent[parent_id], key=lambda x: x['name']):
                    item_text = "  " * indent_level + cat['name']
                    self.category_combobox.addItem(item_text)
                    if cat['id'] in has_children:
                        # Disable parent categories
                        item_index = self.category_combobox.findText(item_text)
                        self.category_combobox.model().item(item_index).setEnabled(False)
                    
                    add_items_recursively(cat['id'], indent_level + 1)

        add_items_recursively(None)

    def get_transaction_data(self):
        """Returns the data entered by the user in a dictionary."""
        return {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "description": self.description_edit.text(),
            "amount": self.amount_spinbox.value(),
            "category": self.category_combobox.currentText().strip()
        }