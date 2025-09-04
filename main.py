import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64
import random
import plotly.express as px

conn = sqlite3.connect("income_manager.db")
c = conn.cursor()


c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, full_name TEXT, phone_number TEXT, email_id TEXT, password TEXT)")
conn.commit()
#background image adding css injection
def add_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: 
                linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), /* dark overlay */
                url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def navigate(page):
    st.session_state.page = page

if "page" not in st.session_state:
    st.session_state.page = "home"
    add_bg_from_local("background_img.jpg")

st.markdown("""
    <style>
    div.stButton > button {
        height: 60px;
        width: 220px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 12px;
        border: 2px solid #4CAF50;
        color: white;
        background-color: transparent !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: white;
        color: #eeeeee;
        border: 2px solid #eeeeee;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Expense Tracker")

col1,col2,col3 = st.columns([1,2,1])
with col2:
    with st.container():
        st.markdown('<div class = "big button">', unsafe_allow_html=True)
        login_clicked = st.button("Login")
        st.markdown('</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class = "big button">', unsafe_allow_html=True)
        signup_clicked = st.button("Sign Up")
        st.markdown('</div>', unsafe_allow_html=True)

def view_expenses(navigate, conn, c, user_id):
    st.title("Your Expenses")
    expenses = c.execute(f"SELECT * FROM user_{user_id} WHERE type = 'expense'")
    expenses = expenses.fetchall()
    if expenses:
        for expense in expenses:
            st.write(f"Date: {expense[0]}    Amount: {expense[2]}")
    else:
        st.write("No expenses found.")

def add_expenses(navigate, conn, c, user_id):
    st.title("Add Expense")
    date = st.date_input("Date", datetime.now().date())
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    if st.button("Add Expense"):
        c.execute(f"INSERT INTO user_{user_id} (date,type,amount) VALUES (?, 'expense', ?)", (date, amount))
        conn.commit()
        st.success("Expense added successfully.")

def view_income(navigate, conn, c, user_id):
    st.title("Your income")
    income = c.execute(f"SELECT * FROM user_{user_id} WHERE type = 'income'")
    income = income.fetchall()
    if income:
        for inc in income:
            st.write(f"Date: {inc[0]}    Amount: {inc[2]}")
    else:
        st.write("No income found.")

def add_income(navigate, conn, c, user_id):
    st.title("Add Income")
    date = st.date_input("Date", datetime.now().date())
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    if st.button("Add Income"):
        c.execute(f"INSERT INTO user_{user_id} (date,type,amount) VALUES (?, 'income', ?)", (date, amount))
        conn.commit()
        st.success("Income added successfully.")

def view_charts(navigate, conn, c, user_id):
    st.title("Your Income Expense Analysis Report")

    # Fetch data
    dates = c.execute(f"SELECT date FROM user_{user_id}")
    dates = [d[0] for d in dates.fetchall()]

    expenses = c.execute(f"SELECT date, amount FROM user_{user_id} WHERE type = 'expense'")
    expenses = expenses.fetchall()

    incomes = c.execute(f"SELECT date, amount FROM user_{user_id} WHERE type = 'income'")
    incomes = incomes.fetchall()

    # Convert to dictionary for easy lookup
    income_dict = {d: amt for d, amt in incomes}
    expense_dict = {d: amt for d, amt in expenses}

    incomes_2 = []
    expenses_2 = []

    # Align by dates
    for d in dates:
        incomes_2.append(income_dict.get(d, 0))   # 0 if no income that day
        expenses_2.append(expense_dict.get(d, 0)) # 0 if no expense that day

    # Prepare dataframe
    charts_data = {
        "dates": dates,
        "incomes": incomes_2,
        "expenses": expenses_2
    }
    df = pd.DataFrame(charts_data)

    # Chart selection
    buttons = st.radio("Select analysis type", 
                       ['Income vs Expenses (Line)', 'Income vs Expenses (Bar)', 'Income vs Expenses (Pie)'])

    if buttons == 'Income vs Expenses (Line)':
        fig = px.line(df, x="dates", y=["incomes", "expenses"], title="Income vs Expenses")
        st.plotly_chart(fig)

    elif buttons == 'Income vs Expenses (Bar)':
        fig = px.bar(df, x="dates", y=["incomes", "expenses"], barmode="group", title="Income vs Expenses")
        st.plotly_chart(fig)

    elif buttons == 'Income vs Expenses (Pie)':
        total_income = sum(incomes_2)
        total_expense = sum(expenses_2)
        fig = px.pie(names=["Income", "Expenses"], values=[total_income, total_expense], title="Income vs Expenses")
        st.plotly_chart(fig)

def dashboard(navigate, conn, c):
    st.title("Dashboard")
    # Add your dashboard content here
    choice = st.radio("Select Option", ["View Expenses", "Add Expense", "View Income", "Add Income", "View Charts"])
    if choice == "View Expenses":
        view_expenses(navigate, conn, c, st.session_state.user_id)
    elif choice == "Add Expense":
        add_expenses(navigate, conn, c, st.session_state.user_id)
    elif choice == "View Income":
        view_income(navigate, conn, c, st.session_state.user_id)
    elif choice == "Add Income":
        add_income(navigate, conn, c, st.session_state.user_id)
    elif choice == "View Charts":
        view_charts(navigate, conn, c, st.session_state.user_id)

# defining login page
def login(navigate, conn, c):
    add_bg_from_local("background_img.jpg")
    st.title("Login")
    user_id = st.text_input("User_Id")
    password = st.text_input("Password", type="password")
    user = c.execute("SELECT * FROM users WHERE id = ? AND password = ?", (user_id, password))
    user = user.fetchone()
    if user:
        st.success("Login Successful")
        st.session_state.user_id = user_id
        dashboard(navigate, conn, c)
    else:
        st.error("Invalid User ID or Password")
        st.session_state.user_id = None
        st.session_state.page = "login"
        forgot_password = st.button("Forgot Password")
        if forgot_password:
            st.session_state.page = "forgot_password"
            email = st.text_input("Email")
            new_password = st.text_input("Enter New password")
            st.success("Password reset successful")
            if st.button("Reset Password"):
                c.execute("UPDATE users SET password = ? WHERE email_id = ?", (new_password, email))
                conn.commit()
                st.success("Password reset successful! Please login with your new password.")
                st.session_state.page = "login"

def sign_up(navigate, conn, c):
    add_bg_from_local("background_img.jpg")
    st.title("Sign Up")
    id = random.randint(1,99999)
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Submit"):
        c.execute("INSERT INTO users (id, full_name, phone_number, email_id, password) VALUES (?, ?, ?, ?, ?)", (id, name, phone, email, password))
        conn.commit()
        c.execute(F"CREATE TABLE IF NOT EXISTS user_{id} (date DATE, type VARCHAR(255), amount DECIMAL(10, 2))")
        conn.commit()
        st.success("Account Created Successfully")
        st.info(f"Your User id: {id} and password: {password} remeber this and go to login")
        st.session_state.page = "login"

if login_clicked:
    st.session_state.page = "login"
if signup_clicked:
    st.session_state.page = "signup"

if st.session_state.page == "login":
    login(navigate, conn, c)
if st.session_state.page == "signup":
    sign_up(navigate, conn, c)