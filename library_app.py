import tkinter as tk
from tkinter import ttk, messagebox
from database import (
    get_all_books, get_all_members, add_book, add_member,
    borrow_book, return_book, search_books, search_members,
    get_loan_history_for_member,
    export_books_to_csv, export_members_to_csv, export_loans_to_csv
)

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Biblioteczny")
        self.root.geometry("900x650")
        self.root.configure(bg="#f8fafc")  # nordycki jasny background

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=25)
        style.configure("TNotebook", background="#f1f5f9")
        style.map("TNotebook.Tab", background=[("selected", "#e2e8f0")])

        notebook = ttk.Notebook(root)
        notebook.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.books_frame = ttk.Frame(notebook)
        self.members_frame = ttk.Frame(notebook)
        self.loans_frame = ttk.Frame(notebook)

        notebook.add(self.books_frame, text="📚 Książki")
        notebook.add(self.members_frame, text="👤 Czytelnicy")
        notebook.add(self.loans_frame, text="🔁 Wypożyczenia")

        self.create_books_tab()
        self.create_members_tab()
        self.create_loans_tab()

        export_frame = ttk.Frame(root)
        export_frame.pack(pady=5, side=tk.BOTTOM, fill=tk.X)
        ttk.Button(export_frame, text="📥 Książki (CSV)", command=self.export_books).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📥 Czytelnicy (CSV)", command=self.export_members).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📥 Wypożyczenia (CSV)", command=self.export_loans).pack(side=tk.LEFT, padx=5)

    def create_books_tab(self):
        search_frame = ttk.Frame(self.books_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Label(search_frame, text="Szukaj (tytuł, autor, ISBN):").pack(side=tk.LEFT)
        self.search_book_entry = ttk.Entry(search_frame, width=30)
        self.search_book_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔍 Szukaj", command=self.search_books).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="↺ Wszystkie", command=self.refresh_books).pack(side=tk.LEFT, padx=5)

        
        columns = ("ID", "Tytuł", "Autor", "ISBN", "Rok", "Dostępne")
        self.books_tree = ttk.Treeview(self.books_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)
        self.books_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        form = ttk.Frame(self.books_frame)
        form.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(form, text="Tytuł:").grid(row=0, column=0, sticky=tk.W)
        self.book_title = ttk.Entry(form, width=20)
        self.book_title.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Autor:").grid(row=0, column=2, sticky=tk.W)
        self.book_author = ttk.Entry(form, width=20)
        self.book_author.grid(row=0, column=3, padx=5)

        ttk.Label(form, text="ISBN:").grid(row=0, column=4, sticky=tk.W)
        self.book_isbn = ttk.Entry(form, width=15)
        self.book_isbn.grid(row=0, column=5, padx=5)

        ttk.Label(form, text="Rok:").grid(row=0, column=6, sticky=tk.W)
        self.book_year = ttk.Entry(form, width=8)
        self.book_year.grid(row=0, column=7, padx=5)

        ttk.Button(form, text="➕ Dodaj książkę", command=self.add_book).grid(row=0, column=8, padx=10)

        self.refresh_books()

    def refresh_books(self):
        for row in self.books_tree.get_children():
            self.books_tree.delete(row)
        for book in get_all_books():
            self.books_tree.insert("", "end", values=(
                book["book_id"],
                book["title"],
                book["author"],
                book["isbn"] or "",
                book["publication_year"] or "",
                book["available_copies"]
            ))

    def search_books(self):
        query = self.search_book_entry.get().strip()
        books = search_books(query) if query else get_all_books()
        for row in self.books_tree.get_children():
            self.books_tree.delete(row)
        for book in books:
            self.books_tree.insert("", "end", values=(
                book["book_id"],
                book["title"],
                book["author"],
                book["isbn"] or "",
                book["publication_year"] or "",
                book["available_copies"]
            ))

    def add_book(self):
        title = self.book_title.get().strip()
        author = self.book_author.get().strip()
        isbn = self.book_isbn.get().strip() or None
        year_str = self.book_year.get().strip()
        if not title or not author:
            messagebox.showwarning("Błąd", "Tytuł i autor są wymagane!")
            return
        try:
            year = int(year_str) if year_str else None
        except ValueError:
            messagebox.showerror("Błąd", "Rok musi być liczbą!")
            return
        add_book(title, author, isbn=isbn, year=year)
        self.refresh_books()
        self.book_title.delete(0, tk.END)
        self.book_author.delete(0, tk.END)
        self.book_isbn.delete(0, tk.END)
        self.book_year.delete(0, tk.END)

    def create_members_tab(self):
        search_frame = ttk.Frame(self.members_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Label(search_frame, text="Szukaj (imię, nazwisko, email, telefon):").pack(side=tk.LEFT)
        self.search_member_entry = ttk.Entry(search_frame, width=30)
        self.search_member_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔍 Szukaj", command=self.search_members).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="↺ Wszyscy", command=self.refresh_members).pack(side=tk.LEFT, padx=5)

        columns = ("ID", "Imię", "Nazwisko", "Email", "Telefon")
        self.members_tree = ttk.Treeview(self.members_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=120)
        self.members_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        form = ttk.Frame(self.members_frame)
        form.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(form, text="Imię:").grid(row=0, column=0, sticky=tk.W)
        self.mem_first = ttk.Entry(form, width=15)
        self.mem_first.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Nazwisko:").grid(row=0, column=2, sticky=tk.W)
        self.mem_last = ttk.Entry(form, width=15)
        self.mem_last.grid(row=0, column=3, padx=5)

        ttk.Button(form, text="➕ Dodaj czytelnika", command=self.add_member).grid(row=0, column=4, padx=10)

        self.refresh_members()

    def refresh_members(self):
        for row in self.members_tree.get_children():
            self.members_tree.delete(row)
        for mem in get_all_members():
            self.members_tree.insert("", "end", values=(
                mem["member_id"],
                mem["first_name"],
                mem["last_name"],
                mem["email"] or "",
                mem["phone"] or ""
            ))

    def search_members(self):
        query = self.search_member_entry.get().strip()
        members = search_members(query) if query else get_all_members()
        for row in self.members_tree.get_children():
            self.members_tree.delete(row)
        for mem in members:
            self.members_tree.insert("", "end", values=(
                mem["member_id"],
                mem["first_name"],
                mem["last_name"],
                mem["email"] or "",
                mem["phone"] or ""
            ))

    def add_member(self):
        first = self.mem_first.get().strip()
        last = self.mem_last.get().strip()
        if not first or not last:
            messagebox.showwarning("Błąd", "Imię i nazwisko są wymagane!")
            return
        add_member(first, last)
        self.refresh_members()
        self.mem_first.delete(0, tk.END)
        self.mem_last.delete(0, tk.END)

    def create_loans_tab(self):
        top = ttk.Frame(self.loans_frame)
        top.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(top, text="ID książki:").grid(row=0, column=0, sticky=tk.W)
        self.loan_book_id = ttk.Entry(top, width=10)
        self.loan_book_id.grid(row=0, column=1, padx=5)

        ttk.Label(top, text="ID czytelnika:").grid(row=0, column=2, sticky=tk.W)
        self.loan_member_id = ttk.Entry(top, width=10)
        self.loan_member_id.grid(row=0, column=3, padx=5)

        ttk.Button(top, text="➡️ Wypożycz", command=self.do_borrow).grid(row=0, column=4, padx=10)
        ttk.Button(top, text="↩️ Zwróć", command=self.do_return).grid(row=0, column=5, padx=10)

        # Historia
        hist_frame = ttk.LabelFrame(self.loans_frame, text="Historia wypożyczeń (podaj ID czytelnika)")
        hist_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.hist_member_id = ttk.Entry(hist_frame, width=15)
        self.hist_member_id.pack(anchor=tk.W, padx=10, pady=5)
        ttk.Button(hist_frame, text=" Pokaż historię ", command=self.show_history).pack(anchor=tk.W, padx=10, pady=5)

        columns = ("ID", "Książka", "Autor", "Wypożyczona", "Termin", "Zwrócona")
        self.history_tree = ttk.Treeview(hist_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def do_borrow(self):
        try:
            book_id = int(self.loan_book_id.get())
            member_id = int(self.loan_member_id.get())
        except ValueError:
            messagebox.showerror("Błąd", "ID muszą być liczbami!")
            return
        if borrow_book(book_id, member_id):
            messagebox.showinfo("Sukces", "książka została wypożyczona")
            # Odśwież listy
            self.refresh_books()
            self.refresh_members()
        else:
            messagebox.showerror("Błąd", "Brak dostępnych egzemplarzy!")

    def do_return(self):
        try:
            book_id = int(self.loan_book_id.get())
            member_id = int(self.loan_member_id.get())
        except ValueError:
            messagebox.showerror("Błąd", "ID muszą być liczbami!")
            return
        return_book(book_id, member_id)
        messagebox.showinfo("Sukces", "książka została zwrócona")
        self.refresh_books()
        self.refresh_members()

    def show_history(self):
        mid = self.hist_member_id.get().strip()
        if not mid.isdigit():
            messagebox.showerror("Błąd", "Podaj poprawne ID czytelnika!")
            return
        loans = get_loan_history_for_member(int(mid))
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for loan in loans:
            self.history_tree.insert("", "end", values=(
                loan["loan_id"],
                loan["title"],
                loan["author"],
                loan["loan_date"],
                loan["due_date"],
                loan["return_date"] or "–"
            ))

    def export_books(self):
        try:
            export_books_to_csv()
            messagebox.showinfo("Sukces", "Zapisano książki do books.csv")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def export_members(self):
        try:
            export_members_to_csv()
            messagebox.showinfo("Sukces", "Zapisano czytelników do members.csv")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def export_loans(self):
        try:
            export_loans_to_csv()
            messagebox.showinfo("Sukces", "Zapisano wypożyczenia do loans.csv")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)

    root.mainloop()

