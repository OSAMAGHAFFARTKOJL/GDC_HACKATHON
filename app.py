# === IMPORTS ===
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import whisper

# === WHISPER SETUP ===
whisper_model = whisper.load_model("base")  # you can use "tiny", "small" for faster

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Voice Controlled Dashboard",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === INITIALIZE SESSION STATE ===
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if 'last_command' not in st.session_state:
    st.session_state.last_command = "No command yet"

# === FUNCTIONS ===

# Function to process uploaded voice
def recognize_uploaded_audio(uploaded_file):
    if uploaded_file is not None:
        with open("temp_audio.wav", "wb") as f:
            f.write(uploaded_file.read())
        
        result = whisper_model.transcribe("temp_audio.wav")
        command = result['text'].strip().lower()
        return command
    else:
        return "No audio uploaded"

# Dummy Data Creation
if 'data' not in st.session_state:
    dates = pd.date_range(start=pd.Timestamp.today() - pd.Timedelta(days=30), periods=30)
    sales = np.random.randint(100, 1000, size=30)
    customers = np.random.randint(10, 100, size=30)
    st.session_state.data = pd.DataFrame({'Date': dates, 'Sales': sales, 'Customers': customers})

# === SIDEBAR ===
st.sidebar.title("🎙️ Voice Control")

# Upload an audio file
uploaded_audio = st.sidebar.file_uploader("Upload your voice (WAV/MP3)", type=["wav", "mp3", "m4a"])

# Button to process voice
if st.sidebar.button("Process Voice Command"):
    if uploaded_audio:
        command = recognize_uploaded_audio(uploaded_audio)
        st.session_state.last_command = command
        st.sidebar.success(f"Recognized: {command}")

        # Switch tabs based on command
        if "dashboard" in command or "home" in command:
            st.session_state.active_tab = "Dashboard"
        elif "customer" in command:
            st.session_state.active_tab = "Customer Analytics"
        elif "product" in command or "products" in command:
            st.session_state.active_tab = "Product Analytics"
        elif "help" in command:
            st.session_state.active_tab = "Help"
        else:
            st.sidebar.warning("Command not recognized. Try again!")

# Show current tab
st.sidebar.markdown(f"**Current Tab:** {st.session_state.active_tab}")
st.sidebar.markdown(f"**Last Command:** {st.session_state.last_command}")

# Manual Navigation
st.sidebar.title("Manual Navigation")
if st.sidebar.button("Go to Dashboard"):
    st.session_state.active_tab = "Dashboard"
if st.sidebar.button("Go to Customer Analytics"):
    st.session_state.active_tab = "Customer Analytics"
if st.sidebar.button("Go to Product Analytics"):
    st.session_state.active_tab = "Product Analytics"
if st.sidebar.button("Go to Help"):
    st.session_state.active_tab = "Help"

# === MAIN CONTENT ===
st.title("🎯 Voice-Controlled Analytics Dashboard")

if st.session_state.active_tab == "Dashboard":
    st.header("📊 Business Overview")
    st.line_chart(st.session_state.data.set_index('Date')[['Sales']])
    st.bar_chart(st.session_state.data.set_index('Date')[['Customers']])

elif st.session_state.active_tab == "Customer Analytics":
    st.header("🧑‍🤝‍🧑 Customer Analytics")
    st.write("This is where customer data would go.")
    st.dataframe(st.session_state.data[['Date', 'Customers']])

elif st.session_state.active_tab == "Product Analytics":
    st.header("📦 Product Analytics")
    st.write("This is where product data would go.")
    sample_products = pd.DataFrame({
        "Product": ["Product A", "Product B", "Product C"],
        "Sales": [1200, 850, 640],
        "Stock Left": [30, 45, 20]
    })
    st.dataframe(sample_products)

elif st.session_state.active_tab == "Help":
    st.header("❓ Help - Voice Commands")
    st.markdown("""
    You can say:
    - **Dashboard** or **Home** → Main Overview
    - **Customer Analytics** → See customer stats
    - **Product Analytics** → See product stats
    - **Help** → Show help instructions
    """)

# === FOOTER ===
st.markdown("---")
st.caption("Built using Streamlit and OpenAI Whisper 🔥")
