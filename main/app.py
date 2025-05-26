import streamlit as st
import pandas as pd
import pymysql

# ----------------- Streamlit Page Config -----------------
st.set_page_config(page_title="RESOLVEAI   - AI Complaint Manager", layout="centered", initial_sidebar_state="collapsed")
hide_menu = """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)
st.title("💡RESOLVEAI\n ")
st.markdown("### AI-Powered Complaint Management System")

with st.expander("ℹ️ Trial Mode Info", expanded=True):
    st.markdown("""
    - This is a demo version of the RESOLVEAI app.
    - We assume you're an existing user (customer or admin).
    - Use the pre-filled credentials to log in and test the functionality.
    """)

# ----------------- Role Selection -----------------
st.markdown("### Who are you?")

if "user_type" not in st.session_state:
    st.session_state.user_type = None

col1, col2 = st.columns(2)
with col1:
    if st.button("🧍 Customer"):
        st.session_state.user_type = "customer"

with col2:
    if st.button("🧑‍💼 Admin"):
        st.session_state.user_type = "admin"

# ----------------- MySQL Utilities -----------------
# def get_all_customers():
#     conn = pymysql.connect(
#         host="localhost", user="root", password="root", database="ai_complaint_responder"
#     )
#     cursor = conn.cursor()
#     cursor.execute("SELECT Customer_ID, Email FROM customers")
#     rows = cursor.fetchall()
#     conn.close()
#     return pd.DataFrame(rows, columns=["Customer_ID", "Email"])

# def get_all_admin():
#     conn = pymysql.connect(
#         host="localhost", user="root", password="root", database="ai_complaint_responder"
#     )
#     cursor = conn.cursor()
#     cursor.execute("SELECT Admin_ID, Email FROM admin")
#     rows = cursor.fetchall()
#     conn.close()
#     return pd.DataFrame(rows, columns=["Admin_ID", "Email"])

# ----------------- Credential Dictionaries -----------------
# customer_dict = get_all_customers().set_index("Email")["Customer_ID"].to_dict()
# admin_dict = get_all_admin().set_index("Email")["Admin_ID"].to_dict()

# # Fixed credentials for demo purposes
customer_dict = {"demo@example.com": "1001"}
admin_dict = {"admin@example.com": "1201"}

# ----------------- Login Logic -----------------
if st.session_state.user_type == "customer":
    st.subheader("🔐 Customer Login")
    email = st.text_input("Customer Email", value="demo@example.com")
    password = st.text_input("Customer Password (Customer ID)", type="password", value=1001)
    if st.button("Login as Customer"):
        if email in customer_dict and password == str(customer_dict[email]):
            st.success("✅ Logged in as Customer")
            st.session_state["customer_id"] = customer_dict[email]
            st.session_state["user_type"] = "customer"
            st.switch_page("pages/customer_form.py")
        else:
            st.error("❌ Invalid Customer credentials.")

elif st.session_state.user_type == "admin":
    st.subheader("🔐 Admin Login")
    email = st.text_input("Admin Email", value="admin@example.com")
    password = st.text_input("Admin Password", type="password", value=1201)
    if st.button("Login as Admin"):
        if email in admin_dict and password == str(admin_dict[email]):
            st.success("✅ Logged in as Admin")
            st.session_state["admin_id"] = admin_dict[email]
            st.session_state["user_type"] = "admin"
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.error("❌ Invalid Admin credentials.")

