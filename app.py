import streamlit as st
import whisper
import os
import threading
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from gtts import gTTS
import tempfile

# Initialize Whisper model
@st.cache_resource
def load_model():
    return whisper.load_model("base")  # You can also use "small", "medium", etc.

model = load_model()

# Initialize session state
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'command' not in st.session_state:
    st.session_state.command = ""
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = "line"
if 'data' not in st.session_state:
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
    st.session_state.data = pd.DataFrame({
        'Date': dates,
        'Sales': np.random.randint(100, 1000, size=30),
        'Customers': np.random.randint(10, 100, size=30),
        'Revenue': np.random.randint(1000, 10000, size=30)
    })

# Function to process voice commands
def process_command(command):
    command = command.lower()
    st.session_state.command = command
    
    # Navigation commands
    if "home" in command or "main" in command:
        st.session_state.page = "home"
        speak("Going to home page.")
    elif "dashboard" in command or "chart" in command or "graph" in command:
        st.session_state.page = "dashboard"
        speak("Going to dashboard.")
    elif "data" in command or "table" in command:
        st.session_state.page = "data"
        speak("Showing data table.")
    elif "setting" in command:
        st.session_state.page = "settings"
        speak("Going to settings page")
    
    # Chart type commands
    if "line" in command:
        st.session_state.chart_type = "line"
        speak("Changing chart to line.")
    elif "bar" in command:
        st.session_state.chart_type = "bar"
        speak("Changing chart to bar.")
    elif "scatter" in command:
        st.session_state.chart_type = "scatter"
        speak("Changing chart to scatter.")
    
    # Refresh commands
    if "refresh" in command or "update" in command:
        st.experimental_rerun()
        speak("Refreshing the page.")
    
    # Stop listening command
    if "stop listening" in command:
        st.session_state.listening = False
        speak("Stopped listening.")

# Function to convert text to speech
def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    os.system("mpg321 output.mp3")  # For Linux; on Windows, use "start output.mp3"

# Function to handle audio recording and transcription
def record_and_transcribe():
    st.session_state.status = "Waiting for audio recording..."
    
    # Streamlit's built-in audio recorder
    audio_bytes = st.audio_recorder("Record a command and click submit:", format="audio/wav")

    if audio_bytes is not None:
        st.session_state.status = "Processing audio..."
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
        
        # Transcribe using Whisper
        result = model.transcribe(temp_audio_path)
        command = result["text"]
        process_command(command)
        
        # Clean up temporary file
        os.remove(temp_audio_path)
        
        st.session_state.status = "Command recognized!"

# Streamlit App Layout
st.title("Voice-Controlled Dashboard (Whisper Version)")

# Sidebar
with st.sidebar:
    st.header("Voice Controls")
    
    if st.button("Record Command"):
        record_and_transcribe()
    
    if 'status' in st.session_state:
        st.write(f"Status: {st.session_state.status}")
    
    if st.session_state.command:
        st.write(f"Last command: {st.session_state.command}")
    
    st.divider()
    
    st.subheader("Voice Commands")
    st.write("Try saying:")
    st.write("- 'home' or 'main' to go to home page")
    st.write("- 'dashboard' or 'chart' to see visualizations")
    st.write("- 'data' or 'table' to see the data")
    st.write("- 'settings' to go to settings page")
    st.write("- 'line', 'bar', or 'scatter' to change chart type")
    st.write("- 'refresh' or 'update' to refresh the page")
    st.write("- 'stop listening' to stop voice recognition")

# Pages
if st.session_state.page == "home":
    st.header("Home")
    st.write("Welcome to the voice-controlled dashboard! Use the voice commands to navigate and control the dashboard.")
    st.write("Click 'Record Command' in the sidebar to start.")
    now = datetime.now()
    st.write(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.subheader("Data Summary")
    st.write(f"Total records: {len(st.session_state.data)}")
    st.write(f"Date range: {st.session_state.data['Date'].min().strftime('%Y-%m-%d')} to {st.session_state.data['Date'].max().strftime('%Y-%m-%d')}")
    st.write(f"Average sales: {st.session_state.data['Sales'].mean():.2f}")
    st.write(f"Average revenue: ${st.session_state.data['Revenue'].mean():.2f}")

elif st.session_state.page == "dashboard":
    st.header("Dashboard")
    st.write(f"Current chart type: {st.session_state.chart_type}")
    
    if st.session_state.chart_type == "line":
        st.line_chart(st.session_state.data.set_index('Date')[['Sales', 'Revenue']])
    elif st.session_state.chart_type == "bar":
        st.bar_chart(st.session_state.data.set_index('Date')[['Sales', 'Customers']])
    elif st.session_state.chart_type == "scatter":
        fig, ax = plt.subplots()
        ax.scatter(st.session_state.data['Sales'], st.session_state.data['Revenue'])
        ax.set_xlabel('Sales')
        ax.set_ylabel('Revenue')
        ax.set_title('Sales vs Revenue')
        st.pyplot(fig)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"{st.session_state.data['Sales'].sum()}")
    with col2:
        st.metric("Total Customers", f"{st.session_state.data['Customers'].sum()}")
    with col3:
        st.metric("Total Revenue", f"${st.session_state.data['Revenue'].sum()}")

elif st.session_state.page == "data":
    st.header("Data")
    st.dataframe(st.session_state.data)
    
    st.subheader("Filter Data")
    min_sales = st.slider("Minimum Sales", 
                         min_value=int(st.session_state.data['Sales'].min()),
                         max_value=int(st.session_state.data['Sales'].max()),
                         value=int(st.session_state.data['Sales'].min()))
    
    filtered_data = st.session_state.data[st.session_state.data['Sales'] >= min_sales]
    st.dataframe(filtered_data)

elif st.session_state.page == "settings":
    st.header("Settings")
    st.checkbox("Enable notifications", value=True)
    st.checkbox("Dark mode", value=False)
    selected_language = st.selectbox("Recognition language", 
                                 options=["English", "Spanish", "French", "German", "Chinese"],
                                 index=0)
    st.write(f"Selected language: {selected_language}")
    
    st.subheader("About")
    st.write("Voice-Controlled Dashboard - Whisper Version")
    st.write("Created with Streamlit and OpenAI Whisper")

