import os
import sqlite3
import flet as ft
import webbrowser
from datetime import datetime

from flet.core.icons import icons

# إنشاء مجلد لتخزين البيانات إن لم يكن موجودًا
data_folder = "lab_data"
os.makedirs(data_folder, exist_ok=True)
db_path = os.path.join(data_folder, "lab_results.db")

# إنشاء قاعدة البيانات
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lab_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        stool_result TEXT,
        urine_result TEXT,
        malaria_result TEXT,
        date TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')
conn.commit()
conn.close()

def login_page(page: ft.Page):
    def handle_login(e):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username_input.value, password_input.value))
        user = cursor.fetchone()
        conn.close()
        if user:
            main(page)
        else:
            error_text.value = "Invalid username or password"
            page.update()

    page.title = "Login"
    user_icon=ft.Image(src='icon.png',width=200)
    username_input = ft.TextField(label="Username",width=300)
    password_input = ft.TextField(label="Password", password=True,width=300)
    login_button = ft.ElevatedButton("Login", on_click=handle_login,width=100,height=50,bgcolor="green",color='white')
    error_text = ft.Text("", color="red")
    
    page.clean()
    # وضع جميع العناصر داخل عمود في المنتصف
    content = ft.Column(
        [
            user_icon,
            username_input,
            password_input,
            login_button,
            error_text
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # محاذاة العناصر عمودياً في المنتصف
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # محاذاة العناصر أفقياً في المنتصف
    )

    # وضع العمود داخل `Container` في المنتصف
    page.add(ft.Container(content, alignment=ft.alignment.center))
    #page.add(username_input, password_input, login_button, error_text)

def main(page: ft.Page):
    page.title = "Lab Test System"
    page.window_width = 800
    page.window_height = 600
    

    name_input = ft.TextField(label="Patient Name")
    stool_input = ft.TextField(label="Routine Stool Examination Result", multiline=True)
    urine_input = ft.TextField(label="Urine Exam Result", multiline=True)
    malaria_input = ft.TextField(label="BFFM for Malaria Result", multiline=True)
    date_input = ft.TextField(label="Date", value=datetime.today().strftime('%Y-%m-%d'), read_only=True)

    save_and_print_button = ft.ElevatedButton("Save & Print", on_click=lambda e: save_and_print(e, page, name_input, stool_input, urine_input, malaria_input, date_input))
    patients_button = ft.ElevatedButton("View Patients", on_click=lambda e: patients_page(page))
    users_button = ft.ElevatedButton("Manage Users", on_click=lambda e: users_page(page))
    
    page.clean()
    page.add(name_input, stool_input, urine_input, malaria_input, date_input, save_and_print_button, patients_button, users_button)

def users_page(page: ft.Page):
    def add_user(e):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username_input.value, password_input.value))
        conn.commit()
        conn.close()
        load_users(page)
    
    def delete_user(user_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        load_users(page)
    
    def load_users(page):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        results = cursor.fetchall()
        conn.close()
        
        user_rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row[0]))),
                ft.DataCell(ft.Text(row[1])),
                ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, user_id=row[0]: delete_user(user_id)))
            ]) for row in results
        ]
        users_table.rows = user_rows
        page.update()
    
    page.title = "Manage Users"
    username_input = ft.TextField(label="New Username")
    password_input = ft.TextField(label="New Password", password=True)
    add_user_button = ft.ElevatedButton("Add User", on_click=add_user)
    back_button = ft.ElevatedButton("Back", on_click=lambda e: main(page))
    
    global users_table
    users_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")),
        ft.DataColumn(ft.Text("Username")),
        ft.DataColumn(ft.Text("Actions"))
    ], rows=[])
    
    page.clean()
    page.add(username_input, password_input, add_user_button, users_table, back_button)
    load_users(page)

def patients_page(page: ft.Page):
    page.title = "Patients List"
    global results_table
    results_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")),
        ft.DataColumn(ft.Text("Patient Name"))
    ], rows=[])
    
    back_button = ft.ElevatedButton("Back", on_click=lambda e: main(page))
    page.clean()
    page.add(results_table, back_button)
    load_results(page)

def load_results(page):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, patient_name FROM lab_tests")
    results = cursor.fetchall()
    conn.close()
    
    table_rows = [
        ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(row[0]))),
            ft.DataCell(ft.Text(row[1]))
        ]) for row in results
    ]
    results_table.rows = table_rows
    page.update()

ft.app(target=login_page,assets_dir='lab_data')
