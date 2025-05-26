import streamlit as st
import pandas as pd
import pymysql
import re
from classifier import generate_llm_response, get_sentiment

st.set_page_config(layout="centered", initial_sidebar_state="collapsed")
if "show_resolved_popup" not in st.session_state:
    st.session_state["show_resolved_popup"] = True

# --- Hide sidebar ---
hide_menu = """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# --- Redirect if not customer ---
if st.session_state.get("user_type") != "customer":
    st.error("Unauthorized access. Redirecting to main page...")
    st.stop()

# --- State Initialization ---
for key in ["show_resolved_popup", "complaint_submitted", "response", "category", "chat_ready", "view_complaints"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "response" and key != "category" else ""

# --- Top Buttons ---
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    refresh = st.button("🔄 Refresh", use_container_width=True)
with col3:
    logout = st.button("🚪 Logout", use_container_width=True)
    if logout:
        st.session_state.clear()
        st.success("Logged out successfully.")
        st.switch_page('app.py')

# --- Page Title ---
st.title("📄AI Complaint Assistant")

customer_id = st.session_state.get("customer_id")
if customer_id is None:
    st.error("You must be logged in to submit a complaint.")
    st.stop()

st.markdown(f"🆔 Logged in as Customer ID: `{customer_id}`")
st.markdown("Type your complaint below and get a smart AI-powered response:")

# --- Insert Complaint to DB ---
def insert_complaint_mysql(customer_id, complaint, category, response, urgency, followup):
    conn = pymysql.connect(host="localhost", user="root", password="root", database="ai_complaint_responder")
    cursor = conn.cursor()
    query = """INSERT INTO complaints 
               (C_id, Complaint_text, Predicted_category, Auto_response, Urgency, Followup) 
               VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (customer_id, complaint, category, response, urgency, followup))
    conn.commit()
    conn.close()

# --- Complaint Form ---
with st.form("complaint_form"):
    complaint_text = st.text_area("Describe your issue")
    submitted = st.form_submit_button("Submit")    
    if submitted:
        response, category, urgency = generate_llm_response(complaint_text)

        st.session_state.complaint_submitted = True
        st.session_state.chat_ready = True  # ✅ Enable chat
        st.session_state.response = response
        st.session_state.category = category

        insert_complaint_mysql(customer_id, complaint_text, category, response, urgency, "")
        st.session_state["chat_complaint"] = {
            "customer_id": customer_id,
            "complaint_text": complaint_text,
            "category": category,
            "urgency": urgency,
            "response": response
        }

        st.markdown(f"**Predicted Category:** `{category}`")
        st.markdown(f"**Urgency Level:** {urgency}")
        st.markdown("**🧠 AI Response:**")
        st.success(response)

# --- Follow-up Input ---
if st.session_state.complaint_submitted:
    follow_up = st.text_input("Please provide your order number or add more details:")
    if follow_up:
        st.success("Thanks! We'll use this info to assist you better.")
        conn = pymysql.connect(host="localhost", user="root", password="root", database="ai_complaint_responder")
        cursor = conn.cursor()
        update_query = """UPDATE complaints 
                          SET Followup = %s 
                          WHERE C_id = %s 
                          ORDER BY id DESC LIMIT 1"""
        cursor.execute(update_query, (follow_up, customer_id))
        conn.commit()
        conn.close()

        # Only reset submission status to allow new complaint later
        st.session_state.complaint_submitted = False

# ✅ Always show Chat Button if chat_ready
if st.session_state.chat_ready:
    if st.button("💬 Chat with AI about this complaint"):
        st.switch_page("pages/chatbot.py")

# --- View Previous Complaints ---
if st.button("📋 View Previous Complaints"):
    st.session_state.view_complaints = True

if st.session_state.view_complaints or refresh:
    st.subheader("📌 Your Previous Complaints & Status")

    def get_customer_complaints(customer_id):
        conn = pymysql.connect(host="localhost", user="root", password="root", database="ai_complaint_responder")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id, Complaint_Text, Complaint_status, Timestamp, Admin_note
            FROM complaints
            WHERE C_id = %s
            ORDER BY Timestamp DESC
        """, (customer_id,))
        rows = cursor.fetchall()
        conn.close()
        return pd.DataFrame(rows, columns=["Complaint ID", "Complaint", "Status", "Submitted At", "Message from Admin"])

    df = get_customer_complaints(customer_id)
    if not df.empty:
        # Check if any complaints were resolved since last view
        if 'last_viewed_complaints' not in st.session_state:
            st.session_state.last_viewed_complaints = set()
        
        # Get current resolved complaints
        current_resolved = set(df[df['Status'] == 'Resolved']['Complaint ID'])
        
        # Find newly resolved complaints (weren't in last viewed set)
        newly_resolved = current_resolved - st.session_state.last_viewed_complaints
        
        # Show popup for each newly resolved complaint
        for complaint_id in newly_resolved:
            complaint_text = df[df['Complaint ID'] == complaint_id]['Complaint'].values[0]
            short_text = (complaint_text[:30] + '...') if len(complaint_text) > 30 else complaint_text
            st.toast(f"🎉 Complaint #{complaint_id} ('{short_text}') has been resolved!", icon="✅")
        
        # Update last viewed complaints
        st.session_state.last_viewed_complaints = current_resolved

        st.dataframe(df, use_container_width=True)
    else:
        st.info("You have not submitted any complaints yet.")