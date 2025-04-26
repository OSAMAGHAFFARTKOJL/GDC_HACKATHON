import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import threading
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize session state variables if they don't exist
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'command' not in st.session_state:
    st.session_state.command = ""
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = "line"
if 'data' not in st.session_state:
    # Generate some sample data
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

# Function to listen for voice commands
def voice_listener():
    r = sr.Recognizer()
    while st.session_state.listening:
        try:
            # Use the default microphone as the audio source
            with sr.Microphone() as source:
                st.session_state.status = "Listening..."
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source)
                # Listen for the first phrase and extract it into audio data
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                st.session_state.status = "Recognizing..."
                
                # Recognize speech using Google Speech Recognition
                command = r.recognize_google(audio)
                process_command(command)
                
        except sr.WaitTimeoutError:
            st.session_state.status = "Timeout. Listening again..."
        except sr.UnknownValueError:
            st.session_state.status = "Could not understand audio. Listening again..."
        except sr.RequestError as e:
            st.session_state.status = f"Could not request results; {e}. Listening again..."
        except Exception as e:
            st.session_state.status = f"Error: {e}. Listening again..."
            
        time.sleep(0.1)  # Short sleep to prevent CPU overload

# Function to convert text to speech
def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    
    # For Linux, use mpg321 or another audio player
    os.system("mpg321 output.mp3")  # This is for Linux systems. For Windows, you can use "start output.mp3".

# Start or stop voice listening
def toggle_listening():
    if st.session_state.listening:
        st.session_state.listening = False
        st.session_state.status = "Stopped listening."
        speak("Stopped listening.")
    else:
        st.session_state.listening = True
        st.session_state.status = "Starting to listen..."
        speak("Starting to listen...")
        threading.Thread(target=voice_listener, daemon=True).start()

# Streamlit app layout
st.title("Voice-Controlled Dashboard")

# Sidebar with controls
with st.sidebar:
    st.header("Voice Controls")
    
    # Button to start/stop listening
    if st.session_state.listening:
        button_text = "Stop Listening"
    else:
        button_text = "Start Listening"
    
    st.button(button_text, on_click=toggle_listening)
    
    # Display listening status
    if 'status' in st.session_state:
        st.write(f"Status: {st.session_state.status}")
    
    # Display last recognized command
    if st.session_state.command:
        st.write(f"Last command: {st.session_state.command}")
    
    st.divider()
    
    # Voice command instructions
    st.subheader("Voice Commands")
    st.write("Try saying:")
    st.write("- 'home' or 'main' to go to home page")
    st.write("- 'dashboard' or 'chart' to see visualizations")
    st.write("- 'data' or 'table' to see the data")
    st.write("- 'settings' to go to settings page")
    st.write("- 'line', 'bar', or 'scatter' to change chart type")
    st.write("- 'refresh' or 'update' to refresh the page")
    st.write("- 'stop listening' to stop voice recognition")

# Main content area
if st.session_state.page == "home":
    st.header("Home")
    st.write("Welcome to the voice-controlled dashboard! Use the voice commands to navigate and control the dashboard.")
    st.write("Click 'Start Listening' in the sidebar to begin voice control.")
    
    # Display current time
    now = datetime.now()
    st.write(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display a summary of the data
    st.subheader("Data Summary")
    st.write(f"Total records: {len(st.session_state.data)}")
    st.write(f"Date range: {st.session_state.data['Date'].min().strftime('%Y-%m-%d')} to {st.session_state.data['Date'].max().strftime('%Y-%m-%d')}")
    st.write(f"Average sales: {st.session_state.data['Sales'].mean():.2f}")
    st.write(f"Average revenue: ${st.session_state.data['Revenue'].mean():.2f}")

elif st.session_state.page == "dashboard":
    st.header("Dashboard")
    
    # Show current chart type
    st.write(f"Current chart type: {st.session_state.chart_type}")
    
    # Visualize the data based on chart type
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
    
    # Display some metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"{st.session_state.data['Sales'].sum()}")
    with col2:
        st.metric("Total Customers", f"{st.session_state.data['Customers'].sum()}")
    with col3:
        st.metric("Total Revenue", f"${st.session_state.data['Revenue'].sum()}")

elif st.session_state.page == "data":
    st.header("Data")
    st.write("Here's the raw data: ")
    st.dataframe(st.session_state.data)
    
    # Allow filtering data
    st.subheader("Filter Data")
    min_sales = st.slider("Minimum Sales", 
                         min_value=int(st.session_state.data['Sales'].min()),
                         max_value=int(st.session_state.data['Sales'].max()),
                         value=int(st.session_state.data['Sales'].min()))
    
    filtered_data = st.session_state.data[st.session_state.data['Sales'] >= min_sales]
    st.write(f"Filtered data ({len(filtered_data)} rows):")
    st.dataframe(filtered_data)

elif st.session_state.page == "settings":
    st.header("Settings")
    st.write("Voice recognition settings:")
    
    # Settings options
    st.checkbox("Enable notifications", value=True)
    st.checkbox("Dark mode", value=False)
    selected_language = st.selectbox("Recognition language", 
                                 options=["English", "Spanish", "French", "German", "Chinese"],
                                 index=0)
    st.write(f"Selected language: {selected_language}")
    
    # About section
    st.subheader("About")
    st.write("Voice-Controlled Dashboard - v1.0")
    st.write("Created with Streamlit and SpeechRecognition")
