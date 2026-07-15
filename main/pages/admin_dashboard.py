import streamlit as st
import pandas as pd
import numpy as np
import pymysql
import matplotlib.pyplot as plt

st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

hide_menu = """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# Redirect if user is not admin
if st.session_state.get("user_type") != "admin":
    st.error("Unauthorized access. Redirecting to main page...")
    st.stop()

# Button Row Layout
col1, col2, col3 = st.columns([2, 6, 2])

with col1:
    refresh = st.button("🔄 Refresh", use_container_width=True)

with col3:
    logout = st.button("🚪 Logout", use_container_width=True)

if logout:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Logged out successfully.")
    st.switch_page('app.py')

# Streamlit admin dashboard
st.title("🛠️ Admin Dashboard - Customer Complaints")

def get_all_complaints():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="ai_complaint_responder"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    columns = ['Id','C_id', 'Complaint', 'Category','Response', 'Timestamp', 'Complaint_status','Urgency', 'Followup', 'Admin_note']
    return pd.DataFrame(rows, columns=columns)

if refresh:
    st.session_state["df"] = get_all_complaints()

# Load on first run
if "df" not in st.session_state:
    st.session_state["df"] = get_all_complaints()

def fetch_complaint_category_df():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="ai_complaint_responder"
    )
    query = "SELECT Predicted_category, Complaint_status FROM complaints"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

category_status_df = fetch_complaint_category_df()

# Create two columns for side-by-side display
col1, col2 = st.columns(2)

# Complaint status Pie chart in left column
with col1:
    st.subheader("📊 Complaint Status")
    status_counts = category_status_df["Complaint_status"].value_counts()

    color_map = {
        "Pending": "red",
        "In Progress": "gold",
        "Resolved": "green"
    }
    colors = [color_map.get(status, "gray") for status in status_counts.index]

    fig, ax = plt.subplots(figsize=(2, 2))  # Smaller size
    ax.pie(
        status_counts,
        labels=status_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        textprops={'fontsize': 5} 
    )
    ax.axis("equal")
    st.pyplot(fig)

# Complaint category Bar Chart in right column
with col2:
    st.subheader("📊 Complaint Categories")
    category_counts = category_status_df["Predicted_category"].value_counts()

    fig2, ax2 = plt.subplots(figsize=(8, 7))
    ax2.bar(category_counts.index, category_counts.values, color='skyblue')
    ax2.set_ylabel("Number of Complaints")
    ax2.set_xticklabels(category_counts.index, rotation=45, ha='right')
    st.pyplot(fig2)

st.subheader("📋Complaints Records" )

df = get_all_complaints()

def update_complaint_status(complaint_id, status, note):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="ai_complaint_responder"
    )
    cursor = conn.cursor()
    query = "UPDATE complaints SET Complaint_status = %s, Admin_note = %s WHERE Id = %s"
    cursor.execute(query, (status, note, complaint_id))
    conn.commit()
    conn.close()

if not df.empty:
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # st.markdown("Status")
        status_filter = st.multiselect("Status", options=df["Complaint_status"].unique(), default=["Pending", "In Progress"])

    with col2:
        # st.markdown("Category")
        category_filter = st.selectbox("Category", options=["All"] + list(df["Category"].unique()))

    with col3:
        # st.markdown("Urgency")
        urgency_filter = st.multiselect("Urgency", options=df["Urgency"].unique(), default=["High", "Medium", "Low"])

    # --- Apply filters ---
    filtered_df = df[
        df["Complaint_status"].isin(status_filter) &
        df["Urgency"].isin(urgency_filter)]

    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["Category"] == category_filter]

    # --- Priority sorting: High Urgency & Pending to top ---
    filtered_df['priority_sort'] = filtered_df.apply(
        lambda row: 0 if (row['Complaint_status'] == 'Pending' and row['Urgency'] == 'High' and row['Id']) or (row['Complaint_status'] == 'In Progress' and row['Urgency'] == 'High' and row['Id'])  else 1,
        axis=1
    )
    filtered_df = filtered_df.sort_values(by='priority_sort')
    filtered_df.drop(columns=['priority_sort'], inplace=True)

    # --- Styling ---
    def highlight_status(val):
        color = ""
        if val == "Pending":
            color = "red"
        elif val == "In Progress":
            color = "orange"
        elif val == "Resolved":
            color = "green"
        return f"background-color: {color}; color: white"

    def highlight_urgency(val):
        color = ""
        if val == "High":
            color = "#ff4d4d"
        elif val == "Medium":
            color = "#ffa64d"
        elif val == "Low":
            color = "#85e085"
        elif val == 'None':
            color = 'Yellow'
        return f"background-color: {color}"
    
    def highlight_high_priority(row):
        if row['Complaint_status'] == 'Pending' and row['Urgency'] == 'High':
            return ['background-color: lightcoral; color:white'] * len(row)
        elif row['Complaint_status'] == 'In Progress' and row['Urgency'] == 'High':
            return ['background-color: lightyellow; color: black'] * len(row)
        elif row['Complaint_status'] == 'In Progress':
            return ['background-color: lightblue; color: black'] * len(row)
        return [''] * len(row)

    if not filtered_df.empty:
        styled_df = filtered_df.style.applymap(highlight_status, subset=["Complaint_status"])
        styled_df = styled_df.applymap(highlight_urgency, subset=["Urgency"])
        styled_df = styled_df.apply(highlight_high_priority, axis=1)

        st.dataframe(styled_df, use_container_width=True)
    else:
        st.warning("No complaint records found for selected filters.")

    selected_row = st.selectbox("Select a complaint to manage", df["Id"])
    complaint = df[df["Id"] == selected_row].iloc[0]

    st.write(f"**ID :** {complaint[0]}")
    st.write(f"**Customer_Id :** {complaint[1]}")
    st.write(f"**Complaint Text :** {complaint[2]}")
    st.write(f"**Category :** {complaint[3]}")
    st.write(f"**Response :** {complaint[4]}")
    st.write(f"**Timestamp :** {complaint[5]}")
    st.write(f"**Status :** {complaint[6]}")
    st.write(f"**Urgency :** {complaint[7]}")
    st.write(f"**Followup :** {complaint[8]}")

    col1, col2, col3 = st.columns(3)

    with col1:
        new_status = st.selectbox("Update status", ["Pending", "In Progress", "Resolved"])
        admin_note = st.text_area("Admin Notes", complaint[9] or "")

    with col3:
        update = st.button("Update Complaint")

    if update:
        if new_status == 'Resolved':
            admin_note = " 😊 Your issue has been resolved. Thank you for your patience!"
        update_complaint_status(complaint[0], new_status, admin_note)
        st.success("Complaint updated successfully.")

else:
    st.info("No complaints found.")
