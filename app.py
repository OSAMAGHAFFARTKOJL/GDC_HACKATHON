import streamlit as st
from transformers import pipeline
import random

# Load models
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
translator = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr")

# Define agent behavior
def classify_input(text):
    keywords_task = ['summarize', 'translate', 'analyze', 'calculate']
    keywords_question = ['what', 'how', 'why', 'who', 'where', 'when']
    text_lower = text.lower()
    
    if any(word in text_lower for word in keywords_task):
        return "Task"
    elif any(word in text_lower for word in keywords_question):
        return "Question"
    else:
        return "Chat"

def perform_task(text):
    if "summarize" in text.lower():
        summary = summarizer(text, max_length=50, min_length=25, do_sample=False)
        return summary[0]['summary_text']
    elif "translate" in text.lower():
        translation = translator(text)
        return translation[0]['translation_text']
    else:
        return "Task recognized, but specific action not implemented yet."

def answer_question(text, context="Streamlit is an awesome tool for building web apps with Python."):
    answer = qa_pipeline(question=text, context=context)
    return answer['answer']

def chat_reply(text):
    replies = [
        "That's interesting!",
        "Tell me more!",
        "I love talking with you!",
        "Sounds fun!",
        "Can you explain a bit more?"
    ]
    return random.choice(replies)

# Streamlit App
st.title("🤖 AI Multi-Task Agent")

user_input = st.text_input("Enter something...")

if st.button("Submit"):
    if user_input:
        task_type = classify_input(user_input)
        st.write(f"**Type Detected:** {task_type}")
        
        if task_type == "Task":
            output = perform_task(user_input)
        elif task_type == "Question":
            output = answer_question(user_input)
        else:
            output = chat_reply(user_input)
        
        st.success(output)
    else:
        st.warning("Please enter some text!")
