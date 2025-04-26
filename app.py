import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
import io

# JavaScript for recording audio
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
    });
}

window.startRecording = startRecording;
window.stopRecording = stopRecording;
</script>
"""

st.title("🎤 Real-Time Voice Controlled Dashboard")

components.html(record_audio_js)

start = st.button("Start Recording")
stop = st.button("Stop Recording")

if start:
    components.html("<script>startRecording()</script>")

if stop:
    audio_base64 = components.html("<script>stopRecording().then(base64 => { window.parent.postMessage({type: 'audio', data: base64}, '*'); });</script>")
    # Then listen for the postMessage and decode the audio!

st.info("Press 'Start' to record and 'Stop' to send audio to the backend.")
