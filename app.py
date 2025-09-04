import streamlit as st
import mysql.connector
import random
import base64
from sign_in import sign_up
import pandas as pd
# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="kush@guha15",
    database="income_manager"
)

c = conn.cursor()

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
        color: #4CAF50;
        border: 2px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Income Manager")

# Big centered buttons (now they navigate)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    with st.container():
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        login_clicked = st.button("Login")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        signup_clicked = st.button("Sign Up")
        st.markdown('</div>', unsafe_allow_html=True)

def login(navigate, conn, c, user_id):
    st.header("Monthly Expense/Income tracker")
    options = ["View Expenses", "Add Expense", "View Income", "Add Income"]
    choice = st.selectbox("Select an option", options)

    if choice == "View Expenses":
        c.execute(f"SELECT * FROM income_manager.user_{user_id} WHERE type='expense'")
        expenses = c.fetchall()
        # displaying the expenses in a proper table
        df = pd.DataFrame(expenses, columns=["date", "budget","type", "amount"])
        st.write(df)
        st.download_button("Download Expenses as CSV", df.to_csv(index=False).encode('utf-8'), "expenses.csv", "text/csv")

    elif choice == "Add Expense":
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        if st.button("Okay"):
            c.execute(f"INSERT INTO income_manager.user_{user_id} (date, type, amount) VALUES (%s,'expense',%s)", (date, amount))
            conn.commit()
            st.success("Expense added!")
            df = pd.DataFrame(columns=["date", "type", "amount"])
            c.execute(f"SELECT * FROM income_manager.user_{user_id} WHERE type='expense'")
            rows = c.fetchall()
            for row in rows:
                df.loc[len(df)] = row
            df.to_csv(f"income_manager.user_{user_id}_expenses.csv", index=False)
            st.success("Expense added!")

    elif choice == "View Income":
        c.execute(f"SELECT * FROM income_manager.user_{user_id} WHERE type='income'")
        income = c.fetchall()
        # displaying the income in a proper table
        df = pd.DataFrame(income, columns=["date", "type", "amount"])
        st.write(df)
        st.download_button("Download Income as CSV", df.to_csv(index=False).encode('utf-8'), "income.csv", "text/csv")

    elif choice == "Add Income":
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        if st.button("Okay"):
            c.execute(f"INSERT INTO income_manager.user_{user_id} (date, amount, type) VALUES (%s, %s, 'income')", (date, amount))
            conn.commit()
            st.success("Income added!")

if login_clicked:
    st.session_state.page = "login"
if signup_clicked:
    st.session_state.page = "sign_up"
if st.session_state.page == "dashboard":
    login(navigate, conn, c, st.session_state.user_id)

#if st.session_state.page == "sign_up":
#    add_bg_from_local("yuri-krupenin-S2FVm0tOv1w-unsplash.jpg")
#    sign_up(navigate, conn, c, st.session_state.new_user_id)


if st.session_state.page == "login":
    add_bg_from_local("background_img.jpg")
    id = st.text_input("User Id: ")
    password = st.text_input("Password: ", type="password")
    c.execute('SELECT * FROM users WHERE id = %s AND password = %s', (id, password))
    user = c.fetchone()
    if user:
        st.success("Login successful!") 
        st.session_state.user_id = id
        st.session_state.page = "dashboard"
    if st.session_state.page == "dashboard":
        login(navigate, conn, c, st.session_state.user_id)  # pass user id to login function       
    else:
        st.error("Invalid credentials")
    if "forgot_mode" not in st.session_state:
        st.session_state.forgot_mode = False

    if st.button("Forgot Password"):
        st.session_state.forgot_mode = True  # switch mode

    if st.session_state.forgot_mode:
        email = st.text_input("Enter your email ID: ")
        if st.button("Verify Email"):
            c.execute('SELECT * FROM users WHERE email_id = %s', (email,))
            user = c.fetchone()
            if user:
                st.session_state.email_verified = True
                st.success("Email verified. Enter a new password below.")
            else:
                st.error("Email ID not found.")

        # If email verified, allow reset
        if st.session_state.get("email_verified", False):
            new_password = st.text_input("Enter new password: ", type="password")
            if st.button("Reset Password"):
                c.execute('UPDATE users SET password = %s WHERE email_id = %s',
                          (new_password, email))
                conn.commit()
                st.success("Password reset successful!")
                st.session_state.forgot_mode = False
                st.session_state.email_verified = False


if st.session_state.page == "sign_up":
    add_bg_from_local("background_img.jpg")
    id = random.randint(1000, 9999)
    full_name = st.text_input("Full Name: ")
    phone_number = st.text_input("Phone Number: ")
    email_id = st.text_input("Email ID: ")
    password = st.text_input("Password: ", type="password")
    table_name = f"income_manager.user_{id}"

    if st.button("Submit"):
        c.execute(
            'INSERT INTO users (id, full_name, phone_number, email_id, password) VALUES (%s, %s, %s, %s, %s)',
            (id, full_name, phone_number, email_id, password)
        )
        conn.commit()
        c.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
        date DATE,
        type ENUM("income", "expense"),
        amount DECIMAL(10, 2)
            )
        ''')
        conn.commit()
        st.success("Sign up successful!")
        st.info(f"Your User ID is: {id}. Please remember it for login.")

        #writing this data into a csv file with same file name as the separate sql tables
        df = pd.DataFrame(columns=["date", "type", "amount"])
        c.execute(f"SELECT * FROM {table_name}")
        rows = c.fetchall()
        for row in rows:
            df.loc[len(df)] = row
        df.to_csv(f"{table_name}.csv", index=False)

        # 👉 redirect to signup page for budget & first transaction
        st.session_state.page = "after_signup"
        st.session_state.new_user_id = id  # store id for next step

    if st.button("Back"):
        st.session_state.page = "home"

# Handle the extra page after signup
if st.session_state.page == "after_signup":
    from sign_in import sign_up
    sign_up(navigate, conn, c, st.session_state.new_user_id)
