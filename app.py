# === IMPORTS ===
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import threading
import time
import random
import pyttsx3
import requests
import json
from PIL import Image
import io
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import whisper
import sounddevice as sd

# === WHISPER SETUP ===
whisper_model = whisper.load_model("base")  # Options: tiny, base, small, medium, large

# === PAGE CONFIG ===
st.set_page_config(
    page_title="AI Voice-Controlled Dashboard",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === INITIALIZE SESSION STATE ===
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'last_command' not in st.session_state:
    st.session_state.last_command = "No command received yet"
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if 'tts_enabled' not in st.session_state:
    st.session_state.tts_enabled = True
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# === FUNCTIONS ===

# Text to Speech
def text_to_speech(text):
    if st.session_state.tts_enabled:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# Record + Transcribe using Whisper
def recognize_speech():
    samplerate = 16000  # Whisper expects 16kHz
    duration = 5  # seconds
    st.info("🎙️ Listening... Speak now!")
    try:
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.float32)
        sd.wait()
        audio_data = np.squeeze(recording)
        result = whisper_model.transcribe(audio_data, fp16=False)
        command = result['text'].strip().lower()
        return command
    except Exception as e:
        return f"Error occurred: {str(e)}"

# Voice Control Listening Loop
def listening_thread():
    while st.session_state.listening:
        command = recognize_speech()
        if command and "error" not in command.lower():
            st.session_state.last_command = command

            # Commands
            if "dashboard" in command or "home" in command:
                st.session_state.active_tab = "Dashboard"
                text_to_speech("Showing dashboard view")
            elif "customer" in command or "customers" in command:
                st.session_state.active_tab = "Customer Analytics"
                text_to_speech("Showing customer analytics")
            elif "product" in command or "products" in command or "inventory" in command:
                st.session_state.active_tab = "Product Analytics"
                text_to_speech("Showing product analytics")
            elif "prediction" in command or "predict" in command or "forecast" in command:
                st.session_state.active_tab = "Predictive Analytics"
                text_to_speech("Showing predictive analytics")
            elif "setting" in command or "settings" in command or "configuration" in command:
                st.session_state.active_tab = "Settings"
                text_to_speech("Opening settings")
            elif "help" in command:
                st.session_state.active_tab = "Help"
                text_to_speech("Showing help information")
            elif "stop listening" in command or "stop" in command:
                st.session_state.listening = False
                text_to_speech("Voice control deactivated")
        time.sleep(0.1)

# Toggle Button for Listening
def toggle_listening():
    st.session_state.listening = not st.session_state.listening
    if st.session_state.listening:
        text_to_speech("Voice control activated. What would you like to see?")
        threading.Thread(target=listening_thread, daemon=True).start()
    else:
        text_to_speech("Voice control deactivated.")

# Dummy Data Creation
if 'data' not in st.session_state:
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    sales = np.random.randint(100, 1000, size=len(dates))
    traffic = np.random.randint(1000, 5000, size=len(dates))
    conversion = np.random.uniform(0.01, 0.05, size=len(dates))
    st.session_state.data = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'traffic': traffic,
        'conversion_rate': conversion
    })

    # Customer Data
    regions = ['North', 'South', 'East', 'West', 'Central']
    categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home Goods']
    n_customers = 100
    customer_data = {
        'customer_id': range(1, n_customers + 1),
        'age': np.random.randint(18, 70, size=n_customers),
        'total_spent': np.random.uniform(100, 5000, size=n_customers),
        'purchases': np.random.randint(1, 50, size=n_customers),
        'loyalty_score': np.random.uniform(0, 100, size=n_customers),
        'days_since_last_purchase': np.random.randint(1, 365, size=n_customers),
        'region': np.random.choice(regions, size=n_customers),
        'preferred_category': np.random.choice(categories, size=n_customers)
    }
    st.session_state.customer_data = pd.DataFrame(customer_data)

# === SIDEBAR ===
with st.sidebar:
    st.header("Navigation")
    st.button("🎙️ Toggle Voice Control", on_click=toggle_listening, key="voice_control_button")

    st.markdown(f"**Listening:** {'🟢 Active' if st.session_state.listening else '🔴 Inactive'}")
    st.markdown(f"**Last Command:** {st.session_state.last_command}")

    st.markdown("---")
    if st.button("Dashboard"):
        st.session_state.active_tab = "Dashboard"
    if st.button("Customer Analytics"):
        st.session_state.active_tab = "Customer Analytics"
    if st.button("Product Analytics"):
        st.session_state.active_tab = "Product Analytics"
    if st.button("Predictive Analytics"):
        st.session_state.active_tab = "Predictive Analytics"
    if st.button("Settings"):
        st.session_state.active_tab = "Settings"
    if st.button("Help"):
        st.session_state.active_tab = "Help"

# === MAIN CONTENT ===

# Title
st.title("🎙️ AI Voice-Controlled Dashboard")

# Different Tabs Content
if st.session_state.active_tab == "Dashboard":
    st.subheader("📊 Business Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${st.session_state.data['sales'].sum():,.2f}")
    col2.metric("Total Traffic", f"{st.session_state.data['traffic'].sum():,}")
    col3.metric("Avg Conversion", f"{st.session_state.data['conversion_rate'].mean() * 100:.2f}%")

    st.line_chart(st.session_state.data.set_index('date')[['sales', 'traffic']])

elif st.session_state.active_tab == "Customer Analytics":
    st.subheader("🧑‍🤝‍🧑 Customer Analytics")
    st.dataframe(st.session_state.customer_data)

elif st.session_state.active_tab == "Product Analytics":
    st.subheader("📦 Product Analytics")
    # Simulate products if needed
    st.write("No product data available (Placeholder)")

elif st.session_state.active_tab == "Predictive Analytics":
    st.subheader("📈 Predictive Analytics")
    # Very basic forecast
    forecast = st.session_state.data.copy()
    forecast['forecast'] = forecast['sales'].rolling(7).mean()
    st.line_chart(forecast.set_index('date')[['sales', 'forecast']])

elif st.session_state.active_tab == "Settings":
    st.subheader("⚙️ Settings")
    tts_enabled = st.toggle("Enable Text-to-Speech", value=st.session_state.tts_enabled)
    if tts_enabled != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_enabled
        if tts_enabled:
            text_to_speech("Text-to-Speech enabled")

elif st.session_state.active_tab == "Help":
    st.subheader("❓ Help")
    st.markdown("""
    **Voice Commands Supported**:
    - "Show dashboard" or "Home"
    - "Show customers" or "Customer analytics"
    - "Show products" or "Product analytics"
    - "Show predictions" or "Forecast"
    - "Open settings" or "Settings"
    - "Help"
    - "Stop listening"
    """)

# === FOOTER ===
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Whisper AI, and Python")
