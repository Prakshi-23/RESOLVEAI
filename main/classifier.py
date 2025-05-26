import string
import pandas as pd
import pickle
import re
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch
import joblib

# Load HuggingFace sentiment model
sentiment_tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
sentiment_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

def get_sentiment(text):
    inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = sentiment_model(**inputs).logits
    scores = softmax(logits.numpy()[0])
    labels = ['negative', 'neutral', 'positive']
    sentiment_score = dict(zip(labels, scores))

    # Convert sentiment to urgency
    if sentiment_score['negative'] > 0.7:  # Higher threshold for complaints
        urgency = "High"
    elif sentiment_score['negative'] > 0.4:
        urgency = "Medium"
    else:
        urgency = "Low"

    return urgency, sentiment_score

# Read CSV
df = pd.read_csv(r'data\realistic_complaints_dataset_9990_cleaned.csv')
df.to_csv('data.txt', index=False)

with open("data.txt", "r") as file:
    content = file.read()

doc = Document(page_content=content)
print("doc collected")

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents([doc])
print("spliting docs")

# Initialize embeddings and vector store
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
print("1")
# vector_store = FAISS.from_documents(splits, embedding_model)
# print("2")
# retriever = vector_store.as_retriever()
# print("Initialize embeddings and vector store")

# Load the saved FAISS vector store
vector_store = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

# Get retriever
retriever = vector_store.as_retriever()

# Load classifier (trained on HuggingFace embeddings)
classifier = joblib.load(r"main\complaint_classifier.pkl")
print("3")

# Load LLM
model = ChatGroq(
    groq_api_key="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",
    model_name="gemma2-9b-it")
print("loading model")

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text
print("4")

def predict_category(complaint):
    cleaned = clean_text(complaint)
    vector = embedding_model.embed_documents([cleaned])
    predicted_category = classifier.predict(vector)[0]
    return predicted_category
print("5")

def generate_llm_response(complaint_text):
    category = predict_category(complaint_text)
    urgency, sentiment_score = get_sentiment(complaint_text)

    retrieved_docs = retriever.invoke(complaint_text)
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)

    prompt_template = PromptTemplate(
        input_variables=["complaint", "category", "context", "urgency"],
        template="""
        You are an AI assistant for customer support.

        Customer Complaint:
        "{complaint}"

        Detected Category:
        "{category}"

        Urgency Level:
        "{urgency}"

        Relevant Company Policies or Past Cases:
        {context}

        Based on the above, provide a clear and helpful response to the customer.
        Be polite and professional and make sure to respond like a human.
        """
    )

    prompt = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate(prompt=prompt_template)
    ])

    chain = (
        prompt.partial(category=category, urgency=urgency)
        | model
        | StrOutputParser()
    )

    response = chain.invoke({
        "complaint": complaint_text,
        "context": context_text
    })

    return response, category, urgency



print("6")

# # Save vector store to folder
# vector_store.save_local("faiss_index")







