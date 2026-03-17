import streamlit as st
import ollama
import base64
from gtts import gTTS
import speech_recognition as sr
from st_audiorec import st_audiorec


# ------------------------#
#  Page Setup & Background
# ------------------------#
st.set_page_config(page_title="Zenguard AI", layout="wide")


def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: 100vw 100vh;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .bg-box {{
            background: rgba(255,255,255,0.8);
            border-radius: 16px;
            padding: 24px;
        }}
        .big-mic {{
            font-size: 2.5em; color: #2196f3;
        }}
        .chat-role-user {{
            color: #009688; font-weight:bold;
        }}
        .chat-role-ai {{
            color: #1976d2; font-weight:bold;
        }}
        .bubble {{
            background: #f5f5f5; border-radius:1em; display:inline-block; padding:12px 18px; margin:1px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


set_background("zenguard_img_1.png")   # Your image filename


# ------------------------#
#  Session State
# ------------------------#
st.session_state.setdefault('conversation_history', [])


# ------------------------#
#  Functions
# ------------------------#
def generate_response(user_input):
    st.session_state['conversation_history'].append({"role": "user", "content": user_input})
    response = ollama.chat(model="llama3.1:8b", messages=st.session_state['conversation_history'])
    ai_response = response['message']['content']
    st.session_state['conversation_history'].append({"role": "assistant", "content": ai_response})
    return ai_response


def generate_affirmation():
    prompt = "Provide a positive affirmation to encourage someone who is feeling stressed or overwhelmed."
    response = ollama.chat(model="llama3.1:8b", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']


def generate_meditation_guide():
    prompt = "Provide a 5-minute guided meditation script to help someone relax and reduce stress."
    response = ollama.chat(model="llama3.1:8b", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']


def text_to_speech(text, lang='en'):
    tts = gTTS(text, lang=lang)
    tts.save("temp_output.mp3")
    audio_bytes = open("temp_output.mp3", "rb").read()
    return audio_bytes


def recognize_speech_from_bytes(wav_bytes):
    with open("temp_voice_input.wav", "wb") as f:
        f.write(wav_bytes)
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp_voice_input.wav") as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except Exception:
            text = ""
    return text


# ------------------------#
#  App Layout
# ------------------------#
st.title("🧘‍♀️ Zenguard AI")


st.markdown('<span class="bg-box">', unsafe_allow_html=True)


st.markdown("### 👇 Tap the mic & speak, or type below:")


# Microphone recording widget
wav_audio_data = st_audiorec()


user_message = ""
submitted = False


if wav_audio_data is not None:
    st.markdown("**Playback your message below before sending:**")
    st.audio(wav_audio_data, format='audio/wav')
    if st.button("🛫 Send voice"):
        user_message = recognize_speech_from_bytes(wav_audio_data)
        if not user_message:
            st.warning("⚠️ Sorry, couldn't understand your voice. Try again.")
        else:
            ai_response = generate_response(user_message)
            st.markdown(f'<span class="chat-role-ai">🤖 Zenguard AI:</span> <span class="bubble">{ai_response}</span>', unsafe_allow_html=True)
            st.audio(text_to_speech(ai_response), format='audio/mp3')


# Text input always available and allows continuous chat
typed_message = st.text_input("Type your message and hit enter…", key="text_input_chatbox")
if typed_message:
    ai_response = generate_response(typed_message)
    st.markdown(f'<span class="chat-role-ai">🤖 Zenguard AI:</span> <span class="bubble">{ai_response}</span>', unsafe_allow_html=True)
    st.audio(text_to_speech(ai_response), format='audio/mp3')
    st.session_state["text_input_chatbox"] = ""  # clears the box so user can type next message


# Display chat history
for msg in st.session_state['conversation_history']:
    if msg["role"] == "user":
        st.markdown(f'<span class="chat-role-user">🧑 You:</span> <span class="bubble">{msg["content"]}</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="chat-role-ai">🤖 Zenguard AI:</span> <span class="bubble">{msg["content"]}</span>', unsafe_allow_html=True)


st.markdown('</span>', unsafe_allow_html=True)


# Extra buttons
st.markdown("---")
col1, col2 = st.columns(2)


with col1:
    if st.button("💬 Give me a Positive Affirmation"):
        with st.spinner("Generating affirmation..."):
            affirmation = generate_affirmation()
            st.markdown(f"**🌿 Affirmation:** {affirmation}")


with col2:
    if st.button("🧘‍♂️ Give me a Guided Meditation"):
        with st.spinner("Preparing meditation..."):
            meditation_guide = generate_meditation_guide()
            st.markdown(f"**🕊️ Guided Meditation:** {meditation_guide}")
