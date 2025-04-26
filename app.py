import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

# Create sample dataset
def create_sample_data():
    data = {
        'Date': pd.date_range(start='2025-01-01', periods=6, freq='M'),
        'Sales': [100, 150, 200, 250, 300, 350],
        'Region': ['East', 'West', 'North', 'South', 'East', 'West']
    }
    return pd.DataFrame(data)

# Plot data
def plot_data(df, chart_type):
    if chart_type == "line":
        fig = px.line(df, x='Date', y='Sales', color='Region', title="Sales Over Time")
    elif chart_type == "bar":
        fig = px.bar(df, x='Date', y='Sales', color='Region', title="Sales by Region")
    elif chart_type == "pie":
        fig = px.pie(df, values='Sales', names='Region', title="Sales Distribution")
    else:
        return None
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig

# Parse voice/text commands
def parse_command(command, df):
    if not command:
        return None, "Please provide a command."
    
    command = command.lower()
    if "line chart" in command:
        return "line", "Displaying line chart."
    elif "bar chart" in command:
        return "bar", "Displaying bar chart."
    elif "pie chart" in command:
        return "pie", "Displaying pie chart."
    else:
        return None, "Command not recognized. Try 'show line chart', 'show bar chart', or 'show pie chart'."

# JavaScript for Web Speech API
WEB_SPEECH_JS = """
<script>
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = true;
recognition.continuous = true;

let isRecognizing = false;

function startRecognition() {
    if (!isRecognizing) {
        recognition.start();
        isRecognizing = true;
        document.getElementById('status').innerText = 'Listening...';
    }
}

function stopRecognition() {
    if (isRecognizing) {
        recognition.stop();
        isRecognizing = false;
        document.getElementById('status').innerText = 'Stopped listening.';
    }
}

recognition.onresult = function(event) {
    let interimTranscript = '';
    let finalTranscript = '';
    
    for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
        } else {
            interimTranscript += event.results[i][0].transcript;
        }
    }
    
    if (finalTranscript) {
        window.parent.postMessage({type: 'SPEECH_RESULT', text: finalTranscript}, '*');
    }
    document.getElementById('interim').innerText = interimTranscript;
};

recognition.onerror = function(event) {
    document.getElementById('status').innerText = 'Error: ' + event.error;
    isRecognizing = false;
};

recognition.onend = function() {
    if (isRecognizing) {
        recognition.start(); // Restart for continuous recognition
    }
};

window.addEventListener('message', function(event) {
    if (event.data.type === 'START_SPEECH') {
        startRecognition();
    } else if (event.data.type === 'STOP_SPEECH') {
        stopRecognition();
    }
});
</script>
<div id="status">Click "Start Voice Command" to begin.</div>
<div id="interim" style="color: gray;"></div>
"""

# Main Streamlit app
def main():
    # Set page config
    st.set_page_config(page_title="Simple Voice-Controlled Dashboard", layout="wide")

    # Custom CSS
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
        font-size: 2em;
        color: #ff6f61;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #ff6f61;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
    }
    .stButton>button:hover {
        background-color: #e65a50;
    }
    .status-box {
        background-color: #2e2e3e;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize data
    df = create_sample_data()

    # Session state
    if 'chart_type' not in st.session_state:
        st.session_state.chart_type = "line"
    if 'speech_text' not in st.session_state:
        st.session_state.speech_text = ""

    # Title
    st.markdown('<h1 class="main-title">Voice-Controlled Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Say 'show line chart', 'show bar chart', or 'show pie chart' to control the dashboard.")

    # Layout
    col1, col gifts = st.columns([3, 1])

    with col1:
        # Chart display
        fig = plot_data(df, st.session_state.chart_type)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Voice control
        st.subheader("Voice Control")
        components.html(WEB_SPEECH_JS, height=80)

        if st.button("Start Voice Command"):
            st.session_state.speech_text = ""  # Reset
            components.html("<script>window.parent.postMessage({type: 'START_SPEECH'}, '*');</script>", height=0)

        if st.button("Stop Voice Command"):
            components.html("<script>window.parent.postMessage({type: 'STOP_SPEECH'}, '*');</script>", height=0)

        # Process speech input
        speech_input = st.text_input("Recognized Command", value=st.session_state.speech_text, key="speech_input")
        if speech_input != st.session_state.speech_text:
            st.session_state.speech_text = speech_input
            new_chart_type, response = parse_command(speech_input, df)
            if new_chart_type:
                st.session_state.chart_type = new_chart_type
            st.markdown(f'<div class="status-box">{response}</div>', unsafe_allow_html=True)

        # Manual input
        st.subheader("Manual Input")
        manual_input = st.text_input("Type a command:")
        if manual_input:
            new_chart_type, response = parse_command(manual_input.lower(), df)
            if new_chart_type:
                st.session_state.chart_type = new_chart_type
            st.markdown(f'<div class="status-box">{response}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
