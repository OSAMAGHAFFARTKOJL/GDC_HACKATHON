import streamlit as st
import streamlit.components.v1 as components
import base64
import tempfile
import speech_recognition as sr
import io

st.set_page_config(page_title="🎙️ Live Voice Recorder", layout="centered")

st.title("🎙️ Real-Time Voice Controlled Dashboard")
st.write("Press **Start Recording**, say something, then **Stop Recording**. Your speech will be shown below!")

# Inject JavaScript to record audio
record_audio_js = """
<script>
let mediaRecorder;
let audioChunks;

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", event => {
        audioChunks.push(event.data);
    });

    mediaRecorder.start();
    console.log("Recording started...");
    document.getElementById('status').innerText = '🎙️ Recording...';
}

async function stopRecording() {
    return new Promise(resolve => {
        mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks);
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result.split(',')[1];
                resolve(base64String);
            };
            reader.readAsDataURL(audioBlob);
        });

        mediaRecorder.stop();
        document.getElementById('status').innerText = '🛑 Recording stopped.';
    });
}

window.startRecording = startRecording;
window.stopRecording = stopRecording;
</script>
"""

# Display recording status
status_placeholder = st.empty()
status_placeholder.markdown("<div id='status'>⌛ Idle</div>", unsafe_allow_html=True)

# Inject JavaScript into the page
components.html(record_audio_js)

# Session states to keep track
if 'recording' not in st.session_state:
    st.session_state['recording'] = False
if 'audio_data' not in st.session_state:
    st.session_state['audio_data'] = None

# Start/Stop Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🎙️ Start Recording"):
        components.html("<script>startRecording()</script>")
        st.session_state['recording'] = True

with col2:
    if st.button("🛑 Stop Recording"):
        components.html("""
        <script>
        stopRecording().then(base64 => {
            const streamlitMsg = {
                isStreamlitMessage: true,
                type: "streamlit:recordedAudio",
                data: base64
            };
            window.parent.postMessage(streamlitMsg, "*");
        });
        </script>
        """)
        st.session_state['recording'] = False

# Handle the custom Streamlit event
audio_data = st.file_uploader("Upload Recorded Audio (Optional if auto doesn't work)", type=["wav", "mp3", "m4a"])

if audio_data is not None:
    st.audio(audio_data)

    # Recognize Speech
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        st.success(f"Recognized Speech: {text}")
    except Exception as e:
        st.error(f"Error recognizing speech: {e}")

# Just a little printing live status
if st.session_state['recording']:
    st.info("Recording... Speak into your microphone 🎤")
else:
    st.info("Click 'Start Recording' to begin.")
