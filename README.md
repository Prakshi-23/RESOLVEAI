
# RESOLVEAI - AI Complaint Classifier and Responder

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)

RESOLVEAI is an AI-powered customer complaint management system built using Streamlit. It intelligently classifies complaints by category and urgency, generates AI-based responses, and provides separate interfaces for customers and administrators to manage and resolve issues effectively.

---

## 🚀 Features

### 🧑‍💻 Customer Interface
- Submit new complaints with auto-tagging of **category** and **urgency**
- AI-generated response using **Groq LLM (Gemma2 9B IT)**
- View history of past complaints
- Submit follow-up messages

### 🛠️ Admin Interface
- Secure login for admins
- View, search, and filter all customer complaints
- Update complaint **status** and **resolution messages**
- Track urgency and categorize complaints

### 🤖 Under the Hood
- **Machine Learning** model for category prediction
- **Sentiment model** for urgency prediction
- **Urgency detection** using a custom classifier
- **Vector Search** with FAISS for semantic understanding
- **LLM response generation** using HuggingFace embeddings + Groq’s Gemma 2B
---

## 🗂️ Project Structure

```
Final AI CCR/
│
├──main/
│   ├── pages/
│      ├── admin_dashboard.py         # Admin dashboard and functionality
│      ├── chatbot.py                 # Standalone chatbot interface
│      └── customer_form.py           # Customer UI for complaint submission & history
│   ├── app.py                      # Entry point (Login & routing logic)
│   ├── complaint_classifier.pkl      # Classification model
│   ├── classifier.py              # Complaint classification, FAISS vector search, LLM response
│   └── improved_complaint_classifier_training.ipynb  # ML training model
│
├── data/
│   └── realistic_complaints_dataset_9990_cleaned.csv
│
├── faiss_index/
│   ├── index.faiss
│   └── index.pkl              # FAISS vector store for semantic search
│
├── .gitignore
├── complaint_responder.sql    # SQL schema and initialization
├── data.txt
├── venv/                      # Virtual environment
└── improved_complaint_classifier_training.ipynb
```


## Database Schema

The system uses a MySQL database with the following structure:

```sql
-- Create the complaints table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS complaints (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    C_id INT NOT NULL,
    Complaint_text TEXT,
    Predicted_category VARCHAR(100),
    Auto_response TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    Complaint_status VARCHAR(50) DEFAULT 'None',
    Urgency VARCHAR(10),
    Followup TEXT,
    Admin_note TEXT

);

-- Simplified Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- Simplified Admins Table
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);


```

---

## 🧠 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python, Hugging Face Transformers, Groq API
- **ML Models**: BERT classifier (sklearn), Urgency classifier
- **Vector Store**: FAISS
- **Database**: MySQL (via complaint_responder.sql)
- **Embeddings**: Hugging Face sentence transformer

---

## 🛠️ Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/RESOLVEAI.git
   cd RESOLVEAI
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Unix
   .\venv\Scripts\activate   # on Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Groq API key**  
   In `classifier.py`, set your API key:
   ```python
   os.environ["GROQ_API_KEY"] = "your-api-key"
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## 📄 License

MIT License. Feel free to use and modify for educational and commercial use.
---

## 🙋‍♂️ Author

**Prakshi**  
AI & Python Developer  
[LinkedIn](https://www.linkedin.com/in/prakshi-karkera/) | [GitHub](https://github.com/Prakshi-23)
