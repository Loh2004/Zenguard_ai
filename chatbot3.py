import os
import io
import base64
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import speech_recognition as sr
from st_audiorec import st_audiorec

# ---------------------------------------------------------
# Page Configuration & Metadata
# ---------------------------------------------------------
st.set_page_config(
    page_title="Zenbot - Mindful Stress Relief Companion",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# In-Memory Speech & Audio Processing (STT & TTS)
# ---------------------------------------------------------
def text_to_speech(text, lang="en"):
    try:
        clean_text = (
            text.replace("*", "")
            .replace("#", "")
            .replace("🤖", "")
            .replace("🧘", "")
            .replace("🌿", "")
            .replace("👋", "")
            .strip()
        )
        if len(clean_text) > 280:
            clean_text = clean_text[:280] + "..."
        fp = io.BytesIO()
        tts = gTTS(text=clean_text, lang=lang)
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        return None


def recognize_speech_from_bytes(wav_bytes):
    try:
        wav_io = io.BytesIO(wav_bytes)
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return text
    except Exception:
        return ""


# ---------------------------------------------------------
# Custom Styling: Authentic Realistic Chatbot UI
# ---------------------------------------------------------
def apply_custom_styles():
    candidates = ["zenguardimg.jpg", "zenguard_img_1.png", "zenguardimg.png"]
    current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
    
    found_img = None
    for name in candidates:
        p = os.path.join(current_dir, name)
        if os.path.exists(p):
            found_img = p
            break
        elif os.path.exists(name):
            found_img = name
            break

    bg_css = ""
    if found_img and os.path.exists(found_img):
        try:
            mime = "image/jpeg" if found_img.lower().endswith((".jpg", ".jpeg")) else "image/png"
            with open(found_img, "rb") as img:
                encoded = base64.b64encode(img.read()).decode()
            bg_css = f"""
            .stApp, [data-testid="stAppViewContainer"] {{
                background-image: linear-gradient(rgba(240, 246, 255, 0.40), rgba(230, 244, 255, 0.50)),
                                  url("data:{mime};base64,{encoded}") !important;
                background-size: cover !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
                background-attachment: fixed !important;
            }}
            [data-testid="stHeader"] {{
                background: transparent !important;
            }}
            """
        except Exception:
            pass

    if not bg_css:
        bg_css = """
        .stApp, [data-testid="stAppViewContainer"] {{
            background: linear-gradient(135deg, #d8ebf9 0%, #edf4fa 50%, #f6effb 100%) !important;
            background-attachment: fixed !important;
        }}
        """

    st.markdown(
        f"""
        <style>
        {bg_css}

        /* Hide default Streamlit header/footer */
        #MainMenu, header, footer {{visibility: hidden;}}
        .block-container {{
            padding-top: 1.2rem !important;
            padding-bottom: 5.5rem !important;
            max-width: 800px !important;
        }}

        /* Global Typography */
        html, body, [class*="css"] {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
            color: #0f172a;
        }}

        /* App Chat Header Card */
        .chat-app-header {{
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: 22px;
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 10px 30px rgba(0, 45, 90, 0.06);
            margin-bottom: 16px;
            position: sticky;
            top: 8px;
            z-index: 99;
        }}

        .header-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .bot-avatar-badge {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
        }}

        .header-text {{
            display: flex;
            flex-direction: column;
        }}

        .header-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.2px;
            line-height: 1.2;
        }}

        .header-subtitle {{
            font-size: 0.78rem;
            color: #0284c7;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .online-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #22c55e;
            box-shadow: 0 0 6px #22c55e;
        }}

        .creator-tag {{
            font-size: 0.75rem;
            background: rgba(2, 132, 199, 0.1);
            color: #0369a1;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
        }}

        /* Realistic Chat Message Bubbles */
        .stChatMessage {{
            background: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.95) !important;
            border-radius: 20px !important;
            box-shadow: 0 4px 20px rgba(0, 30, 70, 0.04) !important;
            padding: 14px 18px !important;
            margin-bottom: 12px !important;
            line-height: 1.55 !important;
        }}

        /* User Chat Message Bubble Distinction */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
        [data-testid="stChatMessage"]:has(.stChatMessageAvatarUser) {{
            background: linear-gradient(135deg, rgba(235, 245, 255, 0.92) 0%, rgba(220, 240, 255, 0.95) 100%) !important;
            border: 1px solid rgba(186, 230, 253, 0.9) !important;
        }}

        /* Pill Buttons & Quick Chips */
        .stButton>button {{
            background: rgba(255, 255, 255, 0.82) !important;
            border: 1px solid rgba(255, 255, 255, 0.95) !important;
            border-radius: 20px !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
            color: #0f172a !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
            padding: 4px 14px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}

        .stButton>button:hover {{
            background: #ffffff !important;
            border-color: #38bdf8 !important;
            color: #0284c7 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.15) !important;
        }}

        /* Compact Audio Recording Box */
        .voice-drawer {{
            background: rgba(255, 255, 255, 0.88);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(255, 255, 255, 0.95);
            border-radius: 18px;
            padding: 12px 18px;
            margin-bottom: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        }}

        /* Breathing Circle Pulsing Widget */
        .breathe-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 16px 8px;
        }}

        .breathe-circle {{
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: radial-gradient(circle, #38bdf8 0%, #0284c7 100%);
            box-shadow: 0 0 24px rgba(56, 189, 248, 0.45);
            animation: breathePulse 19s infinite ease-in-out;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 0.85rem;
            text-align: center;
        }}

        @keyframes breathePulse {{
            0%, 100% {{ transform: scale(0.85); opacity: 0.8; }}
            21% {{ transform: scale(1.3); opacity: 1; }}
            58% {{ transform: scale(1.3); opacity: 1; }}
            100% {{ transform: scale(0.85); opacity: 0.8; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_custom_styles()

# ---------------------------------------------------------
# Session State & Audio Engine Initialization
# ---------------------------------------------------------
if "conversation_history" not in st.session_state:
    intro_spoken = (
        "Hi, I am Zenbot. I was developed by Loh2004 to provide you with optimal, personalized remedies to overcome stress, "
        "calm your thoughts, and restore mental clarity. How are you feeling right now?"
    )
    intro_audio = text_to_speech(intro_spoken)
    st.session_state["conversation_history"] = [
        {
            "role": "assistant",
            "content": (
                "👋 **Hi, I am Zenbot!**\n\n"
                "I was developed by **Loh2004** to give you optimal, personalized remedies to overcome stress, calm your thoughts, and restore mental clarity.\n\n"
                "How are you feeling right now? Tap your current mood or share what's on your mind below (typing or 🎙️ voice)!"
            ),
            "audio": intro_audio,
        }
    ]

if "user_mood" not in st.session_state:
    st.session_state["user_mood"] = "🌱 Balanced"

if "show_voice_box" not in st.session_state:
    st.session_state["show_voice_box"] = False

if "selected_quick_prompt" not in st.session_state:
    st.session_state["selected_quick_prompt"] = None

# ---------------------------------------------------------
# Sidebar: Compact Controls & Settings
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🤖 **Zenbot**")
    st.caption("Crafted with 💚 by **Loh2004** • Mindful Remedy Guide")

    st.markdown("---")
    st.markdown("#### 🎭 **Companion Tone**")
    persona_tone = st.radio(
        "Tone Mode:",
        [
            "💡 Optimal Stress Remedies (Actionable relief)",
            "🌸 Warm & Nurturing (Gentle comfort)",
            "🌿 Mindful & Grounding (Presence & breath)",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("#### 🌬️ **4-7-8 Breathing Circle**")
    with st.expander("Open Breathing Pacer", expanded=False):
        st.markdown(
            """
            <div class="breathe-wrapper">
                <div class="breathe-circle">Breathe</div>
                <p style="margin-top:12px; font-size:0.8rem; color:#0369a1; text-align:center;">
                    <b>Inhale</b> (4s) &nbsp;•&nbsp; <b>Hold</b> (7s) &nbsp;•&nbsp; <b>Exhale</b> (8s)
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    auto_tts = st.toggle("🔊 AI Voice Narration", value=True)

    if st.button("🧹 Clear Chat", use_container_width=True):
        intro_spoken = (
            "Hi, I am Zenbot. Developed by Loh2004 to give you optimal remedies for stress relief and mental clarity. "
            "What can I help soothe for you today?"
        )
        intro_audio = text_to_speech(intro_spoken)
        st.session_state["conversation_history"] = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Hi, I am Zenbot!**\n\n"
                    "Developed by **Loh2004** to give you optimal remedies for stress relief and mental clarity.\n\n"
                    "What can I help soothe for you today?"
                ),
                "audio": intro_audio,
            }
        ]
        st.session_state["show_voice_box"] = False
        st.session_state["selected_quick_prompt"] = None
        st.rerun()

    # Discreet Settings
    with st.expander("⚙️ Advanced Settings", expanded=False):
        default_key = os.environ.get("GEMINI_API_KEY", "")
        if not default_key and "GEMINI_API_KEY" in st.secrets:
            default_key = st.secrets["GEMINI_API_KEY"]

        api_key_input = st.text_input(
            "Gemini API Key",
            value=default_key,
            type="password",
            help="Loaded automatically from secrets.toml",
        )
        selected_model = st.selectbox(
            "Intelligence Engine",
            ["gemini-3.5-flash-lite", "gemini-3.5-flash"],
            index=0,
            help="Powered by Gemini 3.5",
        )

# ---------------------------------------------------------
# Gemini API Engine
# ---------------------------------------------------------
def get_gemini_client():
    key = api_key_input.strip() or os.environ.get("GEMINI_API_KEY", "")
    if not key and "GEMINI_API_KEY" in st.secrets:
        key = st.secrets["GEMINI_API_KEY"]
    if not key:
        return None
    return genai.Client(api_key=key)


def build_system_instruction(tone_choice, mood):
    base_instruction = (
        "You are Zenbot, a mindful wellness companion developed by Loh2004. "
        "Your core mission is to provide OPTIMAL, ACTIONABLE, and SOOTHING REMEDIES for users to overcome stress, anxiety, overwhelm, and fatigue. "
        "CRITICAL INSTRUCTION: Do NOT introduce yourself or say 'Hi, I am Zenbot developed by Loh2004' in standard conversation turns. The user already knows who you are from the initial greeting. "
        "Only state your name/developer if the user specifically asks 'Who are you?' or 'Who developed you?'. "
        "In regular responses, jump straight into providing compassionate, structured, and practical remedies: "
        "1. Instant relief technique (e.g., physiological sigh, 4-7-8 breathing, tension release, or cold water scan). "
        "2. Gentle cognitive reframe (unburdening thoughts, self-compassion). "
        "3. Practical somatic/lifestyle remedy (herbal hydration, progressive muscle relaxation, posture reset). "
        "Always maintain human warmth, empathy, and kindness. Keep responses readable with clean bullet points. "
        f"The user's current mood tag is: '{mood}'. Tailor your remedy specifically to this state. "
    )

    if "Optimal Stress Remedies" in tone_choice:
        base_instruction += "Prioritize structured, highly effective, step-by-step stress alleviation remedies."
    elif "Warm & Nurturing" in tone_choice:
        base_instruction += "Prioritize heartfelt emotional comfort, warm validation, and soothing self-compassion."
    elif "Mindful & Grounding" in tone_choice:
        base_instruction += "Prioritize sensory grounding (5-4-3-2-1), somatic body scans, and breath connection."

    base_instruction += (
        "\n\nSafety Disclaimer: You are an AI wellness companion developed by Loh2004, not a licensed medical doctor. "
        "If a user expresses immediate crisis or thoughts of self-harm, respond with urgent compassion and immediately provide "
        "crisis resources (988 in US/Canada, or local emergency hotlines)."
    )
    return base_instruction


def query_gemini_chat(user_message):
    client = get_gemini_client()
    if not client:
        return (
            "⚠️ **Gemini API Key Needed:** Please open **⚙️ Advanced Settings** in the left sidebar "
            "and enter your Gemini API key."
        )

    system_instruction = build_system_instruction(persona_tone, st.session_state["user_mood"])

    contents = []
    for msg in st.session_state["conversation_history"]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))

    try:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            max_output_tokens=1000,
        )
        response = client.models.generate_content(
            model=selected_model,
            contents=contents,
            config=config,
        )
        return response.text or "I am listening closely. Take a gentle breath and tell me more."
    except Exception as e:
        return f"⚠️ **Error communicating with Gemini:** {str(e)}"


# ---------------------------------------------------------
# App Chat Header Bar
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="chat-app-header">
        <div class="header-left">
            <div class="bot-avatar-badge">🤖</div>
            <div class="header-text">
                <div class="header-title">Zenbot</div>
                <div class="header-subtitle">
                    <span class="online-dot"></span> Online • State: {st.session_state['user_mood']}
                </div>
            </div>
        </div>
        <div class="creator-tag">by Loh2004</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Mood Selector Chips
# ---------------------------------------------------------
mood_cols = st.columns(5)
mood_options = ["🌱 Balanced", "🌧️ Anxious", "⚡ Overwhelmed", "🔥 Stressed", "✨ Hopeful"]
for i, mood in enumerate(mood_options):
    with mood_cols[i]:
        is_active = (st.session_state["user_mood"] == mood)
        label = f"✓ {mood}" if is_active else mood
        if st.button(label, key=f"mood_chip_{i}", use_container_width=True):
            st.session_state["user_mood"] = mood
            st.toast(f"Mood updated to {mood}", icon="🌿")
            st.rerun()

st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Render Chat Stream (With Inline Audio Players)
# ---------------------------------------------------------
for msg in st.session_state["conversation_history"]:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

# ---------------------------------------------------------
# Quick Action Suggestion Chips (Above Chat Input)
# ---------------------------------------------------------
st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
quick_cols = st.columns(4)

with quick_cols[0]:
    if st.button("⚡ Stress Remedy", key="q_remedy", use_container_width=True):
        st.session_state["selected_quick_prompt"] = f"Please give me the optimal 3-step remedy to overcome stress for someone feeling {st.session_state['user_mood']}."

with quick_cols[1]:
    if st.button("🧘 3-Min Meditation", key="q_meditation", use_container_width=True):
        st.session_state["selected_quick_prompt"] = f"Guide me through a soothing 3-minute meditation for feeling {st.session_state['user_mood']}."

with quick_cols[2]:
    if st.button("💬 Affirmation", key="q_affirmation", use_container_width=True):
        st.session_state["selected_quick_prompt"] = f"Give me an uplifting positive affirmation for someone feeling {st.session_state['user_mood']}."

with quick_cols[3]:
    if st.button("🌱 5-4-3-2-1 Grounding", key="q_grounding", use_container_width=True):
        st.session_state["selected_quick_prompt"] = "Guide me step-by-step through the 5-4-3-2-1 sensory grounding technique."

# ---------------------------------------------------------
# Inline Voice Note Drawer
# ---------------------------------------------------------
voice_toggle_col, voice_status_col = st.columns([0.25, 0.75])
with voice_toggle_col:
    v_label = "❌ Close Mic" if st.session_state["show_voice_box"] else "🎙️ Voice Mode"
    if st.button(v_label, use_container_width=True):
        st.session_state["show_voice_box"] = not st.session_state["show_voice_box"]
        st.rerun()

pending_voice_msg = None
if st.session_state["show_voice_box"]:
    with st.container():
        st.markdown("<div class='voice-drawer'>", unsafe_allow_html=True)
        st.caption("🎙️ **Tap record, speak your mind, then click Send Voice Note:**")
        v_col1, v_col2 = st.columns([0.7, 0.3])
        with v_col1:
            wav_data = st_audiorec()
        with v_col2:
            if wav_data is not None:
                if st.button("🚀 Send Voice Note", type="primary", use_container_width=True):
                    with st.spinner("Transcribing voice note..."):
                        transcribed = recognize_speech_from_bytes(wav_data)
                    if transcribed:
                        pending_voice_msg = transcribed
                        st.session_state["show_voice_box"] = False
                    else:
                        st.warning("⚠️ Could not hear clearly. Please try speaking closer to the mic.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Chat Input & Response Processing
# ---------------------------------------------------------
typed_msg = st.chat_input("Message Zenbot... (or tap 🎙️ Voice Mode above)")
active_input = st.session_state["selected_quick_prompt"] or pending_voice_msg or typed_msg

# Reset selected quick prompt
if st.session_state["selected_quick_prompt"]:
    st.session_state["selected_quick_prompt"] = None

if active_input:
    # 1. User Message
    st.session_state["conversation_history"].append({"role": "user", "content": active_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(active_input)

    # 2. AI Response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Zenbot is reflecting..."):
            ai_reply = query_gemini_chat(active_input)
            st.markdown(ai_reply)

            ai_audio = text_to_speech(ai_reply) if auto_tts else None
            if ai_audio:
                st.audio(ai_audio, format="audio/mp3", autoplay=True)

    st.session_state["conversation_history"].append({
        "role": "assistant",
        "content": ai_reply,
        "audio": ai_audio,
    })
