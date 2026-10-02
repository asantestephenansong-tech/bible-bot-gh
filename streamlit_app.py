import streamlit as st
from groq import Groq
import urllib.parse, datetime, re
import streamlit.components.v1 as components

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def clean_text(t):
    t = re.sub(r'\*\*|__|\*|#|•|`', ' ', t)
    t = re.sub(r'https?://\S+', ' ', t)
    return t[:400].replace("'", "").replace('"', '').replace("\n"," ")

# ALL LANGUAGES OF THE WORLD
ALL_LANGS = [
    "Auto-detect (Speak ANY language, SI answers same)",
    "English", "Twi (Akan)", "Ga", "Ewe", "Hausa", "Fante", "Dagbani", "Nzema",
    "French", "Spanish", "Portuguese", "German", "Italian", "Dutch", "Russian",
    "Arabic", "Hindi", "Urdu", "Bengali", "Tamil", "Telugu", "Malayalam", "Kannada", "Gujarati", "Punjabi",
    "Chinese (Mandarin)", "Chinese (Cantonese)", "Japanese", "Korean", "Thai", "Vietnamese", "Indonesian", "Malay", "Tagalog",
    "Turkish", "Persian", "Hebrew", "Swahili", "Yoruba", "Igbo", "Zulu", "Xhosa", "Amharic", "Somali", "Lingala", "Kinyarwanda",
    "Pidgin", "Creole"
]

LANG_VOICE = {
    "English":"en-US", "Twi (Akan)":"en-GH", "Ga":"en-GH", "Ewe":"en-GH", "Hausa":"en-NG", "Fante":"en-GH",
    "French":"fr-FR", "Spanish":"es-ES", "Portuguese":"pt-PT", "German":"de-DE", "Italian":"it-IT", "Dutch":"nl-NL",
    "Russian":"ru-RU", "Arabic":"ar-SA", "Hindi":"hi-IN", "Urdu":"ur-PK", "Bengali":"bn-IN", "Tamil":"ta-IN",
    "Chinese (Mandarin)":"zh-CN", "Japanese":"ja-JP", "Korean":"ko-KR", "Thai":"th-TH", "Vietnamese":"vi-VN",
    "Turkish":"tr-TR", "Swahili":"sw-KE", "Yoruba":"yo-NG", "Igbo":"ig-NG", "Zulu":"zu-ZA"
}

with st.sidebar:
    st.title("🌍 SI World Languages")
    st.write("V4.0 - ALL Languages")
    lang = st.selectbox("Choose Answer Language", ALL_LANGS, index=0, key="lang_all")
    speak = st.checkbox("🔊 Speak Answer", value=True, key="speak_all")
    st.divider()
    st.subheader("Chat History")
    if st.session_state.messages:
        txt = "\n".join([f"{m['role']}: {m['content'][:120]}" for m in st.session_state.messages])
        st.download_button("💾 Download Chat", txt, file_name="SI_chat.txt", key="dl_all")
        wa = urllib.parse.quote("Try SI Worldwide - Speaks ALL languages: https://si-worldwide.streamlit.app")
        st.link_button("📱 Share SI to WhatsApp", f"https://wa.me/?text={wa}")
    if st.button("🗑️ Clear", key="clear_all"):
        st.session_state.messages = []
        st.rerun()

st.title("SI Worldwide 🌍")
st.caption(f"Built by Stephen Asante Ghana - Speaks {len(ALL_LANGS)} Languages!")

audio = st.audio_input("🎤 Tap to speak ANY language in the world", key="audio_world")

voice_prompt = None
if audio:
    with st.spinner("Listening..."):
        try:
            tr = client.audio.transcriptions.create(
                file=(audio.name, audio.getvalue()),
                model="whisper-large-v3",
                prompt="Transcribe any language: Twi, Ga, Ewe, Hausa, French, Arabic, Hindi, Chinese, Spanish, etc.",
                response_format="text"
            )
            voice_prompt = tr
            st.success(f"You said: {voice_prompt}")
        except Exception as e:
            st.error(f"{e}")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"])
        else:
            st.markdown(m["content"])

prompt = st.chat_input("Ask in ANY language... Type here", key="chat_world")
final_prompt = voice_prompt if voice_prompt else prompt

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        is_image = "draw" in low or "picture" in low or "photo" in low or "image" in low or "twa" in low

        if lang.startswith("Auto"):
            lang_inst = f"You are SI Worldwide. User language is: {final_prompt}. DETECT the language automatically and answer in EXACT SAME language. You can speak ALL {len(ALL_LANGS)} world languages fluently. If Twi, answer Twi. If Japanese, answer Japanese. If Arabic, answer Arabic."
        else:
            lang_inst = f"Respond ONLY in {lang}. Translate everything to {lang}."

        if is_image:
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_prompt)}?width=1024&height=1024&nologo=true"
            st.image(url)
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": url})
        else:
            try:
                r = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "system", "content": f"{lang_inst} Keep answer short, plain text, no ** or symbols."}] + [{"role": x["role"], "content": x["content"]} for x in st.session_state.messages if x.get("type") != "image"][-6:],
                    max_tokens=800
                )
                ans = r.choices[0].message.content
                st.markdown(ans)

                if speak:
                    vcode = LANG_VOICE.get(lang, "en-US")
                    if lang.startswith("Auto"):
                        # Auto guess voice from answer script
                        if any(c in ans for c in ["你", "我"]): vcode = "zh-CN"
                        elif any(c in ans for c in ["あ", "い", "う"]): vcode = "ja-JP"
                        elif any(c in ans for c in ["ا", "ب", "ت"]): vcode = "ar-SA"
                        elif any(c in ans for c in ["ह", "न"]): vcode = "hi-IN"
                    js = f"<script>var m=new SpeechSynthesisUtterance('{clean_text(ans)}');m.lang='{vcode}';speechSynthesis.speak(m);</script>"
                    components.html(js, height=0)

                st.session_state.messages.append({"role": "assistant", "content": ans})
                wa2 = urllib.parse.quote(f"{ans[:600]} - SI Worldwide https://si-worldwide.streamlit.app")
                st.link_button("📱 Share to WhatsApp", f"https://wa.me/?text={wa2}", key=f"wa{len(st.session_state.messages)}")
            except Exception as e:
                st.error(f"Error: {e}")
