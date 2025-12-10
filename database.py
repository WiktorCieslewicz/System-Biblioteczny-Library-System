# database.py
import sqlite3
import csv
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            publication_year INTEGER,
            available_copies INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            loan_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY(book_id) REFERENCES books(book_id) ON DELETE CASCADE,
            FOREIGN KEY(member_id) REFERENCES members(member_id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def get_all_books():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_members():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    data = cursor.fetchall()
    conn.close()
    return data

def search_books(query):
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    data = cursor.fetchall()
    conn.close()
    return data

def search_members(query):
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM members
        WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR phone LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    data = cursor.fetchall()
    conn.close()
    return data

def add_book(title, author, isbn=None, year=None, copies=1):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, author, isbn, publication_year, available_copies)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, author, isbn, year, copies))
    conn.commit()
    conn.close()

def add_member(first_name, last_name, email=None, phone=None):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO members (first_name, last_name, email, phone)
        VALUES (?, ?, ?, ?)
    ''', (first_name, last_name, email, phone))
    conn.commit()
    conn.close()

def borrow_book(book_id, member_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT available_copies FROM books WHERE book_id = ?", (book_id,))
    row = cursor.fetchone()
    if not row or row[0] <= 0:
        conn.close()
        return False
    loan_date = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO loans (book_id, member_id, loan_date, due_date)
        VALUES (?, ?, ?, ?)
    ''', (book_id, member_id, loan_date, due_date))
    cursor.execute('UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?', (book_id,))
    conn.commit()
    conn.close()
    return True

def return_book(book_id, member_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE loans
        SET return_date = ?
        WHERE book_id = ? AND member_id = ? AND return_date IS NULL
    ''', (datetime.now().strftime('%Y-%m-%d'), book_id, member_id))
    cursor.execute('UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?', (book_id,))
    conn.commit()
    conn.close()
    return True

def get_loan_history_for_member(member_id):
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.loan_id, b.title, b.author, l.loan_date, l.due_date, l.return_date
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        WHERE l.member_id = ?
        ORDER BY l.loan_date DESC
    ''', (member_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def export_books_to_csv(filename="books.csv"):
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT book_id, title, author, isbn, publication_year, available_copies FROM books")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Tytuł", "Autor", "ISBN", "Rok wydania", "Dostępne egzemplarze"])
            writer.writerows(cursor.fetchall())

def export_members_to_csv(filename="members.csv"):
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT member_id, first_name, last_name, email, phone FROM members")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Imię", "Nazwisko", "Email", "Telefon"])
            writer.writerows(cursor.fetchall())

def export_loans_to_csv(filename="loans.csv"):
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.loan_id, b.title, m.first_name || ' ' || m.last_name,
                   l.loan_date, l.due_date, l.return_date
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
        """)
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID wypożyczenia", "Książka", "Czytelnik", "Data wypożyczenia", "Termin zwrotu", "Data zwrotu"])
            writer.writerows(cursor.fetchall())


init_db()
