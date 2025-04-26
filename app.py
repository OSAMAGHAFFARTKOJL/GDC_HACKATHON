import streamlit as st
import speech_recognition as sr
import pyttsx3
import pandas as pd
import plotly.express as px
from transformers import pipeline
import time
import uuid

# Initialize text-to-speech engine
def init_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    return engine

# Speak text
def speak_text(engine, text):
    engine.say(text)
    engine.runAndWait()

# Initialize speech recognizer
def init_speech_recognizer():
    return sr.Recognizer()

# Listen for voice input
def listen(recognizer):
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()
            st.write(f"Recognized: {text}")
            return text
        except sr.WaitTimeoutError:
            st.write("No speech detected.")
            return None
        except sr.UnknownValueError:
            st.write("Could not understand the audio.")
            return None
        except sr.RequestError as e:
            st.write(f"Speech recognition error: {e}")
            return None

# Initialize AI models (Hugging Face)
@st.cache_resource
def load_ai_models():
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased")
    text_generator = pipeline("text-generation", model="gpt2", max_length=50)
    return sentiment_analyzer, text_generator

# Parse voice commands
def parse_command(command, df, sentiment_analyzer, text_generator):
    if not command:
        return None, None, "Please try again."
    
    # Sample commands
    if "show sales" in command:
        return df, "line", "Displaying sales data as a line chart."
    elif "bar chart" in command:
        return df, "bar", "Switching to bar chart."
    elif "pie chart" in command:
        return df, "pie", "Displaying pie chart."
    elif "filter by" in command:
        # Example: "filter by region east"
        try:
            region = command.split("filter by region")[1].strip()
            filtered_df = df[df['Region'].str.lower() == region]
            if filtered_df.empty:
                return None, None, f"No data for region {region}."
            return filtered_df, "line", f"Filtered data for region {region}."
        except:
            return None, None, "Invalid filter command."
    elif "analyze sentiment" in command:
        # Example: "analyze sentiment of sales are great"
        try:
            text = command.split("analyze sentiment")[1].strip()
            result = sentiment_analyzer(text)[0]
            sentiment = f"Sentiment: {result['label']} (Confidence: {result['score']:.2f})"
            return None, None, sentiment
        except:
            return None, None, "Please provide text for sentiment analysis."
    elif "generate text" in command:
        # Example: "generate text about sales"
        try:
            prompt = command.split("generate text")[1].strip()
            result = text_generator(prompt)[0]['generated_text']
            return None, None, f"Generated: {result}"
        except:
            return None, None, "Please provide a prompt for text generation."
    else:
        return None, None, "Command not recognized."

# Create sample dataset
def create_sample_data():
    data = {
        'Date': pd.date_range(start='2025-01-01', periods=12, freq='M'),
        'Sales': [200, 220, 250, 270, 300, 320, 350, 370, 400, 420, 450, 470],
        'Region': ['East', 'West', 'North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 'North', 'South']
    }
    return pd.DataFrame(data)

# Plot data
def plot_data(df, chart_type):
    if chart_type == "line":
        fig = px.line(df, x='Date', y='Sales', color='Region', title="Sales Over Time")
    elif chart_type == "bar":
        fig = px.bar(df, x='Date', y='Sales', color='Region', title="Sales by Region")
    elif chart_type == "pie":
        fig = px.pie(df, values='Sales', names='Region', title="Sales Distribution by Region")
    else:
        return None
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig

# Main Streamlit app
def main():
    # Set page config
    st.set_page_config(page_title="Voice-Controlled AI Dashboard", layout="wide")

    # Custom CSS for modern design
    st.markdown("""
    <style>
    body {
        background-color: #1e1e2e;
        color: white;
    }
    .stApp {
        background-color: #1e1e2e;
    }
    .main-title {
        text-align: center;
        font-size: 2.5em;
        color: #ff6f61;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #ff6f61;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 1.2em;
    }
    .stButton>button:hover {
        background-color: #e65a50;
    }
    .status-box {
        background-color: #2e2e3e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize components
    engine = init_tts()
    recognizer = init_speech_recognizer()
    sentiment_analyzer, text_generator = load_ai_models()
    df = create_sample_data()

    # Session state for chart type and data
    if 'chart_type' not in st.session_state:
        st.session_state.chart_type = "line"
    if 'current_df' not in st.session_state:
        st.session_state.current_df = df

    # Title
    st.markdown('<h1 class="main-title">Voice-Controlled AI Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Control the dashboard using voice commands like 'show sales', 'bar chart', 'filter by region east', 'analyze sentiment of [text]', or 'generate text about [topic]'.")

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Chart display
        fig = plot_data(st.session_state.current_df, st.session_state.chart_type)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Voice control button
        if st.button("Speak Command"):
            command = listen(recognizer)
            new_df, new_chart_type, response = parse_command(command, df, sentiment_analyzer, text_generator)
            if new_df is not None:
                st.session_state.current_df = new_df
            if new_chart_type:
                st.session_state.chart_type = new_chart_type
            st.markdown(f'<div class="status-box">{response}</div>', unsafe_allow_html=True)
            speak_text(engine, response)

        # Manual input for testing
        manual_input = st.text_input("Or type a command:")
        if manual_input:
            new_df, new_chart_type, response = parse_command(manual_input.lower(), df, sentiment_analyzer, text_generator)
            if new_df is not None:
                st.session_state.current_df = new_df
            if new_chart_type:
                st.session_state.chart_type = new_chart_type
            st.markdown(f'<div class="status-box">{response}</div>', unsafe_allow_html=True)
            speak_text(engine, response)

        # Data table
        st.subheader("Current Data")
        st.dataframe(st.session_state.current_df)

    # Footer
    st.markdown("""
    <div style='text-align: center; margin-top: 20px; color: #888;'>
        Powered by Streamlit, Hugging Face, and Python. Created for innovative data exploration.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
