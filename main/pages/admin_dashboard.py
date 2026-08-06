import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

DB_NAME = "complaints.db"

# --- Hide Sidebar ---
hide_menu = """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# --- Redirect if not admin ---
if st.session_state.get("user_type") != "admin":
    st.error("Unauthorized access. Redirecting to main page...")
    st.stop()

# --- Top Header & Logout ---
col1, col2 = st.columns([8, 2])
with col1:
    st.title("🛠️ Admin Dashboard - Complaint Resolution System")
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.success("Logged out successfully.")
        st.switch_page('app.py')

# --- Fetch Complaints Data from Database ---
def fetch_complaints_sqlite():
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT Id, C_id, Complaint_text, Predicted_category, Urgency, 
               Complaint_status, Timestamp, Followup, Admin_note 
        FROM complaints 
        ORDER BY Timestamp DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = fetch_complaints_sqlite()

# --- Summary Metrics ---
st.subheader("📊 Key Metrics")
m1, m2, m3, m4 = st.columns(4)

total_complaints = len(df)
pending_complaints = len(df[df['Complaint_status'] == 'Pending']) if not df.empty else 0
in_progress_complaints = len(df[df['Complaint_status'] == 'In Progress']) if not df.empty else 0
resolved_complaints = len(df[df['Complaint_status'] == 'Resolved']) if not df.empty else 0

m1.metric("Total Complaints", total_complaints)
m2.metric("Pending", pending_complaints)
m3.metric("In Progress", in_progress_complaints)
m4.metric("Resolved", resolved_complaints)

st.divider()

# --- Complaints Table & Management ---
st.subheader("📋 Manage Customer Complaints")

if not df.empty:
    # Filter options
    filter_status = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Resolved"])
    
    filtered_df = df.copy()
    if filter_status != "All":
        filtered_df = filtered_df[filtered_df['Complaint_status'] == filter_status]
    
    st.dataframe(filtered_df, use_container_width=True)

    st.divider()
    st.subheader("✏️ Update Complaint Status & Admin Notes")
    
    complaint_ids = filtered_df["Id"].tolist()
    if complaint_ids:
        selected_id = st.selectbox("Select Complaint ID to Update:", complaint_ids)
        
        # Get current details of selected complaint
        selected_row = filtered_df[filtered_df["Id"] == selected_id].iloc[0]
        
        col_a, col_b = st.columns(2)
        with col_a:
            current_status = selected_row["Complaint_status"]
            status_options = ["Pending", "In Progress", "Resolved"]
            default_index = status_options.index(current_status) if current_status in status_options else 0
            
            new_status = st.selectbox("Update Status:", status_options, index=default_index)
            
        with col_b:
            admin_note = st.text_area("Add/Edit Admin Note:", value=selected_row["Admin_note"] or "")

        if st.button("💾 Save Changes", type="primary"):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            update_query = """
                UPDATE complaints 
                SET Complaint_status = ?, Admin_note = ? 
                WHERE Id = ?
            """
            cursor.execute(update_query, (new_status, admin_note, selected_id))
            conn.commit()
            conn.close()
            
            st.success(f"Complaint #{selected_id} updated successfully!")
            st.rerun()
    else:
        st.info("No complaints found for the selected filter.")

else:
    st.info("No complaints registered in the system yet.")
