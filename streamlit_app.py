import streamlit as st
from groq import Groq
import urllib.parse, datetime, io
from gtts import gTTS

st.set_page_config(page_title="SI Worldwide", page_icon=":earth_africa:", layout="wide")

# CLIENT
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Streamlit Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR - KEEP CHAT HISTORY + SHARE
with st.sidebar:
    st.title("SI Controls")
    
    lang = st.selectbox(
        "Language",
        ["Auto-detect (Speak my language)", "English", "Twi", "Ga", "Ewe", "Hausa", "French", "Spanish", "Arabic", "Pidgin", "Chinese", "Hindi", "Italian", "German"],
        index=0
    )
    
    speak_answer = st.checkbox("🔊 Speak answer (SI voice)", value=True)
    
    st.divider()
    st.subheader("Chat History")
    if st.session_state.messages:
        chat_text = "\n\n".join([f"{m['role']}: {m['content'][:200]}" for m in st.session_state.messages])
        st.download_button("💾 Download Chat", chat_text, file_name=f"SI_chat_{datetime.date.today()}.txt")
        
        # WhatsApp Share Whole Chat
        wa_text = urllib.parse.quote(f"Check my chat with SI Worldwide (Built by Stephen Asante Ghana):\n\n{chat_text[:1000]}... \nTry: https://si-worldwide.streamlit.app")
        st.link_button("📱 Share to WhatsApp", f"https://wa.me/?text={wa_text}")
    
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

st.title("SI Worldwide")
st.caption("Built by Stephen Asante in Ghana - Akwaaba! Speaks ALL languages + Voice + Share")

# VOICE INPUT - SPEAK ALL LANGUAGES, SI ANSWERS
st.write("🎤 **Speak any language:**")
audio = st.audio_input("Tap to speak")

voice_prompt = None
if audio:
    with st.spinner("SI is listening..."):
        try:
            # Transcribe with Groq Whisper - understands ALL languages
            transcription = client.audio.transcriptions.create(
                file=(audio.name, audio.getvalue()),
                model="whisper-large-v3",
                response_format="text"
            )
            voice_prompt = transcription
            st.success(f"You said: {voice_prompt}")
        except Exception as e:
            st.error(f"Voice error: {e}")

# DISPLAY HISTORY
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type")=="image":
            st.image(m["content"])
        else:
            st.markdown(m["content"])
            # Share button per answer
            if m["role"]=="assistant" and m.get("type")!="image":
                wa_msg = urllib.parse.quote(f"{m['content'][:800]} \n\n- From SI Worldwide by Stephen Asante: https://si-worldwide.streamlit.app")
                st.link_button("📱 WhatsApp", f"https://wa.me/?text={wa_msg}", key=f"wa_{id(m)}")

# INPUTS
prompt = st.chat_input("Ask SI anything... type or speak above")

final_prompt = voice_prompt if voice_prompt else prompt

if final_prompt:
    st.session_state.messages.append({"role":"user","content":final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)
    
    with st.chat_message("assistant"):
        low=final_prompt.lower()
        is_image=any(k in low for k in ["draw a","draw an","picture of","photo of","image of
