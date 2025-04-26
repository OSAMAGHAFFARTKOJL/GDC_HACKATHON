import streamlit as st
import streamlit.components.v1 as components
import base64
import tempfile
import speech_recognition as sr
import io

st.set_page_config(page_title="🎙️ Live Voice Recorder", layout="centered")

st.title("🎙️ Real-Time Voice Controlled Dashboard")
st.write("Press **Start Recording**, say something, then **Stop Recording**. Your speech will be recognized and shown automatically!")

# Inject JavaScript to record audio
record_audio_js = """
<script>
let mediaRecorder;
let audioChunks;
let isRecording = false;

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", event => {
        audioChunks.push(event.data);
    });

    mediaRecorder.start();
    isRecording = true;
    console.log("Recording started...");
    document.getElementById('status').innerText = '🎙️ Recording...';
}

async function stopRecording() {
    if (!isRecording) return;
    return new Promise(resolve => {
        mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result.split(',')[1];
                const streamlitMsg = {
                    isStreamlitMessage: true,
                    type: "streamlit:recordedAudio",
                    data: base64String
                };
                window.parent.postMessage(streamlitMsg, "*");
                resolve(base64String);
            };
            reader.readAsDataURL(audioBlob);
        });

        mediaRecorder.stop();
        isRecording = false;
        document.getElementById('status').innerText = '🛑 Recording stopped.';
    });
}

window.startRecording = startRecording;
window.stopRecording = stopRecording;
</script>
"""

# Display status
status_placeholder = st.empty()
status_placeholder.markdown("<div id='status'>⌛ Idle</div>", unsafe_allow_html=True)

# Inject JS
components.html(record_audio_js)

# Streamlit states
if 'audio_base64' not in st.session_state:
    st.session_state['audio_base64'] = None
if 'recording' not in st.session_state:
    st.session_state['recording'] = False

# Start/Stop Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🎙️ Start Recording"):
        components.html("<script>startRecording()</script>")
        st.session_state['recording'] = True

with col2:
    if st.button("🛑 Stop Recording"):
        components.html("<script>stopRecording()</script>")
        st.session_state['recording'] = False

# Custom event listener
def save_audio_from_streamlit():
    from streamlit_javascript import st_javascript
    base64_audio = st_javascript("""
    new Promise((resolve) => {
        window.addEventListener("message", (event) => {
            if (event.data?.type === "streamlit:recordedAudio") {
                resolve(event.data.data);
            }
        });
    });
    """, key="audio_listener")
    return base64_audio

# Try to capture audio
audio_base64 = save_audio_from_streamlit()

if audio_base64:
    st.session_state['audio_base64'] = audio_base64

if st.session_state['audio_base64']:
    # Decode the audio
    audio_bytes = base64.b64decode(st.session_state['audio_base64'])

    # Play audio in Streamlit
    st.audio(audio_bytes, format="audio/wav")

    # Recognize speech
    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_bytes)

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        st.success(f"✅ Recognized Speech: {text}")
    except Exception as e:
        st.error(f"❌ Error recognizing speech: {e}")

# Show recording status
if st.session_state['recording']:
    st.info("🎤 Recording... Speak now!")
else:
    st.info("ℹ️ Click 'Start Recording' to record your voice.")
