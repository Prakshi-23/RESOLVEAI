import streamlit as st
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, AIMessage

# --- Page Setup ---
st.set_page_config(page_title="Chat with AI", layout="centered", initial_sidebar_state="collapsed")
hide_menu = """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# --- 1. Groq Model Initialization ---
model = ChatGroq(
    groq_api_key="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",
    model_name="gemma2-9b-it"
)

# --- 2. Validate Required Info ---
if "chat_complaint" not in st.session_state:
    st.error("No complaint data found. Please submit a complaint first.")
    st.stop()

complaint_data = st.session_state["chat_complaint"]
complaint_text = complaint_data["complaint_text"]
customer_id = complaint_data["customer_id"]
category = complaint_data["category"]
urgency = complaint_data["urgency"]
response = complaint_data["response"]

# --- 3. Initialize Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 4. Page Layout ---
st.title("💬 AI Complaint Chatbot")
st.markdown(f"🆔 **Customer ID:** `{customer_id}`")
st.markdown(f"📂 **Complaint Category:** `{category}` | 🚨 **Urgency:** `{urgency}`")
st.info(f'''📝 **Your Complaint:**\n\n{complaint_text}\n\n
**AI Response:** \n\n{response}''')

# --- 5. Display Previous Messages Conditionally ---

# Add toggle flag if not present
if "show_history" not in st.session_state:
    st.session_state.show_history = False

# Show toggle button
if st.button("📜 Show Previous Chat History" if not st.session_state.show_history else "🙈 Hide Chat History"):
    st.session_state.show_history = not st.session_state.show_history

# Conditionally display chat history
if st.session_state.show_history:
    for msg in st.session_state.chat_history:
        if isinstance(msg, dict) and msg.get("role") == "user":
            st.chat_message("user").write(msg["content"])
        elif isinstance(msg, dict) and msg.get("role") == "ai":
            st.chat_message("ai").write(msg["content"])


# --- 6. Handle New User Input ---
user_input = st.chat_input("Ask something about this complaint...")

if user_input:
    # Save user input
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Build message context
    messages = [HumanMessage(content=f"Customer Complaint: {complaint_text}. Give a 3–4 line response about this complaint. The company is a telecommunications or internet service provider.")]
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            messages.append(AIMessage(content=msg["content"]))

    # Call LLM
    ai_response = model.invoke(messages)

    # Save and show response
    st.session_state.chat_history.append({"role": "ai", "content": ai_response.content})
    st.chat_message("ai").write(ai_response.content)

# --- 7. Back Button ---
if st.button("⬅️ Back to Complaints"):
    st.switch_page("pages/customer_form.py")
