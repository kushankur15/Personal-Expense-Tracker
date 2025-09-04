import streamlit as st
import mysql.connector
import base64

def sign_up(navigate, conn, c, user_id):
    st.header("Monthly Expense/Income tracker")
    budget = st.number_input("Budget", min_value=0.0, format="%.2f")

    if st.button("Submit Budget"):
        st.success("Budget submitted successfully!")

    st.write("Set your first income/expense")
    date = st.date_input("Date")
    type = st.selectbox("Type", ["income", "expense"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")

    if st.button("Submit Transaction"):
        st.success("Transaction submitted successfully!")
        table_name = f"income_manager.user_{user_id}"
        c.execute(
            f'INSERT INTO {table_name} (date, budget, type, amount) VALUES (%s, %s, %s, %s)',
            (date, budget, type, amount)
        )
        conn.commit()
        navigate("home")