import sqlite3
import os

# Define the path for the database in the 'data' directory
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'finance.db')

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = lambda b: b.decode('utf-8') # Set text factory to decode using UTF-8
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL
        );
    ''')

    # Create settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    ''')

    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES categories (id)
        );
    ''')

    # Create budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            UNIQUE(month, year)
        );
    ''')

    # Check if onboarding is complete
    cursor.execute("SELECT value FROM settings WHERE key = 'onboarding_complete'")
    result = cursor.fetchone()

    if result is None:
        # First-time setup
        cursor.execute("INSERT INTO settings (key, value) VALUES ('onboarding_complete', '0')")
        
        # Add default categories
        default_categories = [
            ('Żywność', None),
            ('Transport', None),
            ('Mieszkanie', None),
            ('Rozrywka', None),
            ('Zdrowie', None),
            ('Hobby', None)
        ]
        cursor.executemany("INSERT INTO categories (name, parent_id) VALUES (?, ?)", default_categories)

        # Add subcategories
        categories_with_subcategories = {
            "Żywność": ["Artykuły spożywcze", "Restauracje", "Kawa"],
            "Transport": ["Paliwo", "Bilety", "Części samochodowe"],
            "Mieszkanie": ["Czynsz", "Rachunki", "Naprawy"],
            "Rozrywka": ["Kino", "Koncerty", "Gry", "Książki"],
            "Zdrowie": ["Lekarz", "Apteka", "Siłownia"],
            "Hobby": ["Sport", "Muzyka", "Podróże"]
        }

        for parent_name, sub_names in categories_with_subcategories.items():
            cursor.execute("SELECT id FROM categories WHERE name = ?", (parent_name,))
            parent_id_result = cursor.fetchone()
            if parent_id_result:
                parent_id = parent_id_result[0]
                subcategories_to_add = [(name, parent_id) for name in sub_names]
                cursor.executemany("INSERT INTO categories (name, parent_id) VALUES (?, ?)", subcategories_to_add)

    conn.commit()
    conn.close()

def is_onboarding_complete():
    """Checks if the onboarding process has been completed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'onboarding_complete'")
    result = cursor.fetchone()
    conn.close()
    return result is not None and result['value'] == '1'

def set_onboarding_complete():
    """Marks the onboarding process as complete."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET value = '1' WHERE key = 'onboarding_complete'")
    conn.commit()
    conn.close()

def set_main_currency(currency):
    """Sets the main currency."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('main_currency', ?)", (currency,))
    conn.commit()
    conn.close()

def get_all_categories():
    """Fetches all categories from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, parent_id FROM categories ORDER BY name")
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_transaction(data):
    """Adds a new transaction to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
        (data['date'], data['description'], abs(float(data['amount'])), data['category'])
    )
    conn.commit()
    conn.close()

def get_all_transactions():
    """Fetches all transactions from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, description, amount, category FROM transactions ORDER BY date DESC")
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def update_transaction(transaction_id, data):
    """Updates an existing transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transactions SET date = ?, description = ?, amount = ?, category = ? WHERE id = ?",
        (data['date'], data['description'], abs(float(data['amount'])), data['category'], transaction_id)
    )
    conn.commit()
    conn.close()

def delete_transaction(transaction_id):
    """Deletes a transaction from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()

def set_budget_for_month(amount, month, year):
    """Sets the budget for a specific month and year."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO budgets (amount, month, year) VALUES (?, ?, ?)",
        (amount, month, year)
    )
    conn.commit()
    conn.close()

def get_budget_for_month(month, year):
    """Gets the budget for a specific month and year."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM budgets WHERE month = ? AND year = ?", (month, year))
    result = cursor.fetchone()
    conn.close()
    return result['amount'] if result else None

def add_category(name, parent_id):
    """Adds a new category to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categories (name, parent_id) VALUES (?, ?)",
        (name, parent_id)
    )
    conn.commit()
    conn.close()

def delete_category(category_id):
    """Deletes a category from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # First, update transactions that use this category
    cursor.execute("UPDATE transactions SET category = 'Uncategorized' WHERE category = (SELECT name FROM categories WHERE id = ?)", (category_id,))
    # Second, update subcategories to have no parent
    cursor.execute("UPDATE categories SET parent_id = NULL WHERE parent_id = ?", (category_id,))
    # Finally, delete the category
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
