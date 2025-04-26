# === IMPORTS ===
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import whisper

# === LOAD WHISPER MODEL ===
whisper_model = whisper.load_model("base")  # you can also use "tiny", "small" for faster

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Voice Controlled Dashboard",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === SESSION STATE INITIALIZATION ===
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if 'last_command' not in st.session_state:
    st.session_state.last_command = "No command yet"

# === FUNCTION TO PROCESS UPLOADED AUDIO ===
def recognize_uploaded_audio(uploaded_file):
    if uploaded_file is not None:
        # Save the uploaded audio temporarily
        with open("temp_audio.wav", "wb") as f:
            f.write(uploaded_file.read())
        
        # Transcribe using Whisper
        result = whisper_model.transcribe("temp_audio.wav")
        command = result['text'].strip().lower()
        return command
    else:
        return "No audio uploaded"

# === DUMMY DATA CREATION ===
if 'data' not in st.session_state:
    dates = pd.date_range(start=pd.Timestamp.today() - pd.Timedelta(days=30), periods=30)
    sales = np.random.randint(100, 1000, size=30)
    customers = np.random.randint(10, 100, size=30)
    st.session_state.data = pd.DataFrame({'Date': dates, 'Sales': sales, 'Customers': customers})

# === SIDEBAR ===
st.sidebar.title("🎙️ Voice Control")

# Upload Audio
uploaded_audio = st.sidebar.file_uploader("Upload your voice (WAV/MP3)", type=["wav", "mp3", "m4a"])

# Process the uploaded audio
if st.sidebar.button("Process Voice Command"):
    if uploaded_audio:
        command = recognize_uploaded_audio(uploaded_audio)
        st.session_state.last_command = command
        st.sidebar.success(f"Recognized: {command}")

        # Match command to tabs
        if "dashboard" in command or "home" in command:
            st.session_state.active_tab = "Dashboard"
        elif "customer" in command:
            st.session_state.active_tab = "Customer Analytics"
        elif "product" in command or "products" in command:
            st.session_state.active_tab = "Product Analytics"
        elif "help" in command:
            st.session_state.active_tab = "Help"
        else:
            st.sidebar.warning("Unknown command. Try again!")

# Show current state
st.sidebar.markdown(f"**Current Tab:** {st.session_state.active_tab}")
st.sidebar.markdown(f"**Last Command:** {st.session_state.last_command}")

# Manual Navigation (optional)
st.sidebar.title("🔵 Manual Navigation")
if st.sidebar.button("Go to Dashboard"):
    st.session_state.active_tab = "Dashboard"
if st.sidebar.button("Go to Customer Analytics"):
    st.session_state.active_tab = "Customer Analytics"
if st.sidebar.button("Go to Product Analytics"):
    st.session_state.active_tab = "Product Analytics"
if st.sidebar.button("Go to Help"):
    st.session_state.active_tab = "Help"

# === MAIN AREA ===
st.title("🎯 Voice-Controlled Analytics Dashboard")

# === ACTIVE TAB CONTENT ===
if st.session_state.active_tab == "Dashboard":
    st.header("📊 Business Overview")
    st.line_chart(st.session_state.data.set_index('Date')[['Sales']])
    st.bar_chart(st.session_state.data.set_index('Date')[['Customers']])

elif st.session_state.active_tab == "Customer Analytics":
    st.header("🧑‍🤝‍🧑 Customer Analytics")
    st.dataframe(st.session_state.data[['Date', 'Customers']])

elif st.session_state.active_tab == "Product Analytics":
    st.header("📦 Product Analytics")
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
    - **Dashboard** or **Home** → To see business overview
    - **Customer Analytics** → To see customer statistics
    - **Product Analytics** → To view product-related data
    - **Help** → To show help instructions
    """)

# === FOOTER ===
st.markdown("---")
st.caption("Built using Streamlit and OpenAI Whisper | No Mic Required 🚀")
