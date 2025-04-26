import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import whisper
import av
import numpy as np

# Whisper model loading
whisper_model = whisper.load_model("base")

# Streamlit settings
st.set_page_config(page_title="🎙️ Voice Command Dashboard", layout="wide")

# Initialize session
if 'last_command' not in st.session_state:
    st.session_state.last_command = "No command yet"
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"

# AudioProcessor class for recording microphone audio
class AudioProcessor:
    def __init__(self):
        self.frames = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame

# UI
st.title("🎯 Voice Controlled Dashboard (Live Mic)")
st.sidebar.title("🎙️ Controls")

# Start WebRTC audio streamer
webrtc_ctx = webrtc_streamer(
    key="voice-command",
    mode=WebRtcMode.SENDONLY,
    in_audio=True,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
    ),
    audio_receiver_size=256,
    async_processing=True
)

if webrtc_ctx.audio_receiver:
    audio_processor = AudioProcessor()

    # Collect some audio frames
    try:
        audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        for audio_frame in audio_frames:
            frame = av.AudioFrame.from_ndarray(audio_frame.to_ndarray(), layout="mono")
            audio_processor.recv(frame)

        # Process after enough frames
        if len(audio_processor.frames) > 20:
            audio_data = np.concatenate(audio_processor.frames)
            audio_data = audio_data.astype(np.float32) / 32768.0  # normalize 16-bit PCM

            # Run Whisper
            result = whisper_model.transcribe(audio_data, fp16=False)
            command = result['text'].strip().lower()
            st.session_state.last_command = command

            # Reset frames for next command
            audio_processor.frames = []

            st.success(f"Recognized Command: {command}")

            # Switching tabs based on recognized command
            if "dashboard" in command or "home" in command:
                st.session_state.active_tab = "Dashboard"
            elif "customer" in command:
                st.session_state.active_tab = "Customer Analytics"
            elif "product" in command or "products" in command:
                st.session_state.active_tab = "Product Analytics"
            elif "help" in command:
                st.session_state.active_tab = "Help"
            else:
                st.warning("Command not recognized. Try again!")

    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")

# Manual navigation buttons (backup)
st.sidebar.write("🔵 Manual Navigation")
if st.sidebar.button("Go to Dashboard"):
    st.session_state.active_tab = "Dashboard"
if st.sidebar.button("Go to Customer Analytics"):
    st.session_state.active_tab = "Customer Analytics"
if st.sidebar.button("Go to Product Analytics"):
    st.session_state.active_tab = "Product Analytics"
if st.sidebar.button("Go to Help"):
    st.session_state.active_tab = "Help"

# Display active page
st.subheader(f"📋 Current Page: {st.session_state.active_tab}")

if st.session_state.active_tab == "Dashboard":
    st.write("Welcome to the Dashboard! 📊")
elif st.session_state.active_tab == "Customer Analytics":
    st.write("Here is Customer Analytics 🧑‍🤝‍🧑")
elif st.session_state.active_tab == "Product Analytics":
    st.write("Product Analytics section 📦")
elif st.session_state.active_tab == "Help":
    st.write("""
    Voice Commands:
    - "Show dashboard"
    - "Go to customer analytics"
    - "Open product analytics"
    - "Help"
    """)

# Footer
st.markdown("---")
st.caption("Built using Streamlit, Streamlit WebRTC, and OpenAI Whisper 🔥")
