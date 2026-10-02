import streamlit as st
from groq import Groq
import urllib.parse, re
import streamlit.components.v1 as components

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_voice_id" not in st.session_state:
    st.session_state.last_voice_id = None

def clean_text(t):
    t = re.sub(r'\*\*|__|\*|#|•|`', ' ', t)
    t = re.sub(r'https?://\S+', ' ', t)
    return t[:400].replace("'", "").replace('"', '').replace("\n", " ")

ALL_LANGS = [
    "Auto-detect (ANY language)",
    "English", "Twi (Akan)", "Ga", "Ewe", "Hausa", "Fante",
    "French", "Spanish", "Portuguese", "German", "Italian", "Dutch", "Russian",
    "Arabic", "Hindi", "Chinese", "Japanese", "Korean", "Thai", "Vietnamese", "Indonesian",
    "Turkish", "Swahili", "Yoruba", "Igbo", "Zulu", "Amharic", "Somali", "Pidgin"
]

LANG_VOICE = {
    "English": "en-US",
    "Twi (Akan)": "en-GH",
    "Ga": "en-GH",
    "Ewe": "en-GH",
    "Hausa": "en-NG",
    "French": "fr-FR",
    "Spanish": "es-ES",
    "Portuguese": "pt-PT",
    "German": "de-DE",
    "Russian": "ru-RU",
    "Arabic": "ar-SA",
    "Hindi": "hi-IN",
    "Chinese": "zh-CN",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Swahili": "sw-KE",
    "Yoruba": "yo-NG"
}

with st.sidebar:
    st.title("🌍 SI Controls")
    lang = st.selectbox("Answer Language", ALL_LANGS, index=0, key="lang_v43")
    speak = st.checkbox("🔊 Speak Answer", value=True, key="speak_v43")
    st.divider()
    if st.button("🗑️ Clear Chat", key="clear_v43"):
        st.session_state.messages = []
        st.session_state.last_voice_id = None
        st.rerun()

st.title("SI Worldwide 🌍")
st.caption("V4.3 - All Languages Fixed")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"])
        else:
            st.markdown(m["content"])

audio = st.audio_input("🎤 Tap to speak", key="audio_v43")

voice_prompt = None
if audio:
    audio_id = audio.file_id if hasattr(audio, 'file_id') else str(len(audio.getvalue()))
    if audio_id != st.session_state.last_voice_id:
        with st.spinner("Listening..."):
            try:
                tr = client.audio.transcriptions.create(
                    file=(audio.name, audio.getvalue()),
                    model="whisper-large-v3",
                    prompt="Twi, Ga, Ewe, Hausa, Akan, English, French, Arabic, etc.",
                    response_format="text"
                )
                voice_prompt = tr
                st.session_state.last_voice_id = audio_id
            except Exception as e:
                st.error(f"{e}")

prompt = st.chat_input("Type in ANY language here and press send →", key="chat_v43")
final_prompt = voice_prompt if voice_prompt else prompt

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        is_meaning_question = "what is" in low or "meaning" in low or "translate" in low or "means" in low
        is_image_request = ("draw" in low or "picture" in low or "photo" in low or "image" in low or "twa" in low)
        is_image = is_image_request and not is_meaning_question

        if lang.startswith("Auto"):
            lang_inst = "Detect language and answer in SAME language. Support ALL world languages."
        else:
            lang_inst = f"Respond ONLY in {lang}."

                if is_image:
            # Clean "I want a picture of" -> just "motorbike"
            clean_prompt = final_prompt.lower().replace("i want a picture of", "").replace("i want", "").replace("picture of", "").replace("a picture", "").replace("draw", "").strip()
            if clean_prompt == "": clean_prompt = final_prompt
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_prompt)}?width=1024&height=1024&seed={len(clean_prompt)}&nologo=true&enhance=true"
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": url})
        else:
            try:
                r = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "system", "content": f"You are SI. {lang_inst} Plain text, short, no **."}] + [{"role": x["role"], "content": x["content"]} for x in st.session_state.messages if x.get("type") != "image"][-6:],
                    max_tokens=600
                )
                ans = r.choices[0].message.content
                st.markdown(ans)
                if speak:
                    vcode = LANG_VOICE.get(lang, "en-US")
                    js = f"<script>var m=new SpeechSynthesisUtterance('{clean_text(ans)}');m.lang='{vcode}';speechSynthesis.speak(m);</script>"
                    components.html(js, height=0)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                wa2 = urllib.parse.quote(f"{ans[:500]} - https://si-worldwide.streamlit.app")
                st.link_button("📱 Share to WhatsApp", f"https://wa.me/?text={wa2}", key=f"wa{len(st.session_state.messages)}_v43")
            except Exception as e:
                st.error(f"Error: {e}")
    st.rerun()
