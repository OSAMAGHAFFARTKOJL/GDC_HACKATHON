import streamlit as st
import speech_recognition as sr
import threading
import pyttsx3

# Initialize speech engine for feedback
engine = pyttsx3.init()

# Initialize session state variables if they don't exist
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'command' not in st.session_state:
    st.session_state.command = ""
if 'page' not in st.session_state:
    st.session_state.page = "home"

# Function to process voice commands
def process_command(command):
    command = command.lower()
    st.session_state.command = command

    # Navigation commands
    if "home" in command or "main" in command:
        st.session_state.page = "home"
    elif "about" in command:
        st.session_state.page = "about"
    elif "settings" in command:
        st.session_state.page = "settings"
    
    # Stop listening command
    if "stop listening" in command:
        st.session_state.listening = False

    # Provide feedback to the user
    engine.say(f"Command recognized: {command}")
    engine.runAndWait()

# Function to listen for voice commands
def voice_listener():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while st.session_state.listening:
            try:
                # Adjust for ambient noise and listen
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                st.session_state.status = "Recognizing..."
                
                # Recognize speech using Google Speech Recognition
                command = r.recognize_google(audio)
                process_command(command)
                
            except sr.UnknownValueError:
                st.session_state.status = "Could not understand audio."
            except sr.RequestError as e:
                st.session_state.status = f"Error: {e}."
            time.sleep(0.1)

# Start or stop voice listening
def toggle_listening():
    if st.session_state.listening:
        st.session_state.listening = False
        st.session_state.status = "Stopped listening."
    else:
        st.session_state.listening = True
        st.session_state.status = "Starting to listen..."
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
    st.write("- 'home' or 'main' to go to the home page")
    st.write("- 'about' to go to the about page")
    st.write("- 'settings' to go to the settings page")
    st.write("- 'stop listening' to stop voice recognition")

# Main content area
if st.session_state.page == "home":
    st.header("Home Page")
    st.write("Welcome to the Voice-Controlled Dashboard! Use the voice commands to navigate.")
    
elif st.session_state.page == "about":
    st.header("About Page")
    st.write("This is a simple dashboard that is controlled by your voice. Use the sidebar to control the voice recognition.")
    
elif st.session_state.page == "settings":
    st.header("Settings Page")
    st.write("This page can contain settings for the application.")
