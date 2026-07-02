import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

DB_NAME = "finance.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and creates tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    """)
    
    # 2. Income Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        source TEXT NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    # 3. Expenses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    # 4. Budgets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        UNIQUE(user_id, category),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    # 5. Savings Goals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS savings_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        goal_name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL NOT NULL DEFAULT 0.0,
        target_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_income_user ON income(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_user ON expenses(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_budgets_user ON budgets(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_savings_user ON savings_goals(user_id);")
    
    conn.commit()
    conn.close()

# --- USER OPERATIONS ---

def add_user(username, password_hash):
    """Inserts a new user. Returns the user ID, or None if the username already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?);", 
            (username.lower().strip(), password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_username(username):
    """Fetches user details by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?;", (username.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

# --- INCOME OPERATIONS ---

def add_income(user_id, amount, source, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?);",
        (user_id, amount, source.strip(), date)
    )
    conn.commit()
    conn.close()

def get_incomes(user_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, amount, source, date FROM income WHERE user_id = ? ORDER BY date DESC;",
        conn,
        params=(user_id,)
    )
    conn.close()
    return df

def delete_income(income_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id = ? AND user_id = ?;", (income_id, user_id))
    conn.commit()
    conn.close()

# --- EXPENSE OPERATIONS ---

def add_expense(user_id, amount, category, description, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?);",
        (user_id, amount, category.strip(), description.strip(), date)
    )
    conn.commit()
    conn.close()

def get_expenses(user_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, amount, category, description, date FROM expenses WHERE user_id = ? ORDER BY date DESC;",
        conn,
        params=(user_id,)
    )
    conn.close()
    return df

def delete_expense(expense_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?;", (expense_id, user_id))
    conn.commit()
    conn.close()

# --- BUDGET OPERATIONS ---

def set_budget(user_id, category, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (user_id, category, amount) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, category) 
        DO UPDATE SET amount = excluded.amount;
    """, (user_id, category.strip(), amount))
    conn.commit()
    conn.close()

def get_budgets(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, amount FROM budgets WHERE user_id = ?;", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row['category']: row['amount'] for row in rows}

def get_expenses_vs_budget(user_id):
    """
    Returns a dataframe comparing current month expenses with set budgets.
    """
    conn = get_connection()
    current_month = datetime.now().strftime("%Y-%m")
    
    # Query to fetch categories, budgets, and actual spent for the current month
    query = """
    SELECT 
        b.category,
        b.amount AS budget_amount,
        COALESCE(SUM(e.amount), 0) AS spent_amount
    FROM budgets b
    LEFT JOIN expenses e ON b.user_id = e.user_id 
        AND b.category = e.category 
        AND strftime('%Y-%m', e.date) = ?
    WHERE b.user_id = ?
    GROUP BY b.category;
    """
    df = pd.read_sql_query(query, conn, params=(current_month, user_id))
    conn.close()
    return df

# --- SAVINGS GOAL OPERATIONS ---

def add_savings_goal(user_id, goal_name, target_amount, current_amount, target_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
        VALUES (?, ?, ?, ?, ?);
    """, (user_id, goal_name.strip(), target_amount, current_amount, target_date))
    conn.commit()
    conn.close()

def update_savings_goal(goal_id, user_id, current_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE savings_goals 
        SET current_amount = ? 
        WHERE id = ? AND user_id = ?;
    """, (current_amount, goal_id, user_id))
    conn.commit()
    conn.close()

def delete_savings_goal(goal_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM savings_goals WHERE id = ? AND user_id = ?;", (goal_id, user_id))
    conn.commit()
    conn.close()

def get_savings_goals(user_id):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT id, goal_name, target_amount, current_amount, target_date 
        FROM savings_goals 
        WHERE user_id = ? 
        ORDER BY target_date ASC;
    """, conn, params=(user_id,))
    conn.close()
    return df

# --- MOCK DATA GENERATOR ---

def generate_mock_data(user_id):
    """
    Generates 6 months of historical finance data for the user.
    Clears out the user's existing records first to avoid duplicates.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Clear existing data for this user
        cursor.execute("DELETE FROM income WHERE user_id = ?;", (user_id,))
        cursor.execute("DELETE FROM expenses WHERE user_id = ?;", (user_id,))
        cursor.execute("DELETE FROM budgets WHERE user_id = ?;", (user_id,))
        cursor.execute("DELETE FROM savings_goals WHERE user_id = ?;", (user_id,))
        
        # Define categories
        categories = ["Food", "Entertainment", "Education", "Shopping", "Bills & Utilities", "Other"]
        
        # Set Budgets
        budgets = {
            "Food": 500.0,
            "Entertainment": 250.0,
            "Education": 300.0,
            "Shopping": 400.0,
            "Bills & Utilities": 350.0,
            "Other": 200.0
        }
        for cat, amt in budgets.items():
            cursor.execute(
                "INSERT INTO budgets (user_id, category, amount) VALUES (?, ?, ?);",
                (user_id, cat, amt)
            )
            
        # Get start date (6 months ago, beginning of month)
        today = datetime.now()
        start_date = today - timedelta(days=180)
        
        # Generate monthly incomes and expenses
        current_date = datetime(start_date.year, start_date.month, 1)
        
        sources = ["Salary", "Freelance", "Investment Dividend"]
        
        while current_date <= today:
            month_str = current_date.strftime("%Y-%m")
            
            # Monthly Incomes
            # Salary on 1st of month
            salary_date = current_date.strftime("%Y-%m-01")
            cursor.execute(
                "INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?);",
                (user_id, 4500.0, "Salary", salary_date)
            )
            # Freelance on 15th (sometimes)
            if random.random() > 0.3:
                freelance_date = current_date.strftime("%Y-%m-15")
                freelance_amt = round(random.uniform(500.0, 1200.0), 2)
                cursor.execute(
                    "INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?);",
                    (user_id, freelance_amt, "Freelance", freelance_date)
                )
            # Dividend (every 3 months)
            if current_date.month in [1, 4, 7, 10]:
                div_date = current_date.strftime("%Y-%m-20")
                cursor.execute(
                    "INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?);",
                    (user_id, 150.0, "Investment Dividend", div_date)
                )
                
            # Monthly Expenses (Categorized)
            for cat, budget_limit in budgets.items():
                # Make some months overspend slightly and others underspend
                # Food: stable
                # Entertainment: variable
                if cat == "Food":
                    spent_factor = random.uniform(0.8, 1.1)  # $400 - $550
                elif cat == "Entertainment":
                    spent_factor = random.uniform(0.4, 1.3)  # Overspends sometimes
                elif cat == "Shopping":
                    spent_factor = random.uniform(0.6, 1.4)  # High variance
                elif cat == "Bills & Utilities":
                    spent_factor = random.uniform(0.9, 1.05) # Fixed bills mostly
                else:
                    spent_factor = random.uniform(0.3, 1.0)
                    
                total_spent = round(budget_limit * spent_factor, 2)
                
                # Split this total spent into 2-4 transactions spread across the month
                num_transactions = random.randint(2, 5)
                remaining_spent = total_spent
                
                for idx in range(num_transactions):
                    day = random.randint(1, 28)
                    date_val = datetime(current_date.year, current_date.month, day)
                    if date_val > today:
                        continue # Don't record future transactions
                    
                    if idx == num_transactions - 1:
                        tx_amt = round(remaining_spent, 2)
                    else:
                        tx_amt = round(random.uniform(10.0, remaining_spent / (num_transactions - idx)), 2)
                        
                    if tx_amt <= 0:
                        continue
                        
                    remaining_spent -= tx_amt
                    
                    desc = f"Monthly {cat} item {idx + 1}"
                    cursor.execute(
                        "INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?);",
                        (user_id, tx_amt, cat, desc, date_val.strftime("%Y-%m-%d"))
                    )
            
            # Move to next month
            # Get next month's 1st day
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
                
        # Insert Savings Goals
        cursor.execute("""
            INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
            VALUES (?, 'Emergency Fund', 10000.0, 6500.0, ?);
        """, (user_id, (today + timedelta(days=365)).strftime("%Y-%m-%d")))
        
        cursor.execute("""
            INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
            VALUES (?, 'MacBook Pro', 2500.0, 1800.0, ?);
        """, (user_id, (today + timedelta(days=120)).strftime("%Y-%m-%d")))
        
        cursor.execute("""
            INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
            VALUES (?, 'European Vacation', 5000.0, 1200.0, ?);
        """, (user_id, (today + timedelta(days=270)).strftime("%Y-%m-%d")))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
