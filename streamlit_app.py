import streamlit as st
from groq import Groq
import urllib.parse, datetime, re
import streamlit.components.v1 as components

st.set_page_config(page_title="SI Worldwide", page_icon=":earth_africa:", layout="wide")

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
    return t[:400].replace("'", "").replace('"', '')

with st.sidebar:
    st.title("SI Controls")
    lang = st.selectbox("Answer Language", ["Auto-detect", "English", "Twi", "Ga", "Ewe", "Hausa", "French", "Spanish", "Arabic", "Pidgin", "Hindi"], index=0, key="lang_select")
    speak = st.checkbox("Speak answer", value=True, key="speak_check")
    st.divider()
    if st.session_state.messages:
        txt = "\n".join([f"{m['role']}: {m['content'][:120]}" for m in st.session_state.messages])
        st.download_button("Download Chat", txt, file_name="SI_chat.txt", key="dl_btn")
        wa = urllib.parse.quote(f"From SI Worldwide https://si-worldwide.streamlit.app")
        st.link_button("Share WhatsApp", f"https://wa.me/?text={wa}", key="wa_side")
    if st.button("Clear History", key="clear_btn"):
        st.session_state.messages = []
        st.rerun()

st.title("SI Worldwide")
st.caption("Built by Stephen Asante Ghana - V3.3")

# SIMPLE VOICE - Uses phone mic, understands Twi better
audio = st.audio_input("Tap to speak - Twi, Ga, Ewe, Hausa, English", key="audio_input_unique")

voice_prompt = None
if audio:
    with st.spinner("SI listening..."):
        try:
            tr = client.audio.transcriptions.create(
                file=(audio.name, audio.getvalue()),
                model="whisper-large-v3",
                prompt="This is Twi, Ga, Ewe, Hausa, Akan, Ghana Pidgin. Transcribe.",
                response_format="text"
            )
            voice_prompt = tr
            st.success(f"You said: {voice_prompt}")
        except Exception as e:
            st.error(f"Voice error: {e}")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"])
        else:
            st.markdown(m["content"])

prompt = st.chat_input("Ask SI anything...", key="chat_input_main")
final_prompt = voice_prompt if voice_prompt else prompt

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        is_image = "draw" in low or "picture" in low or "photo" in low or "image" in low

        if lang.startswith("Auto"):
            lang_inst = "Respond in SAME language as user. If user speaks Twi, answer in Twi."
        else:
            lang_inst = f"Respond ONLY in {lang}."

        if is_image:
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_prompt)}?width=1024&height=1024&nologo=true"
            st.image(url)
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": url})
        else:
            try:
                r = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "system", "content": f"You are SI by Stephen Asante. {lang_inst} Use plain text only, no ** or bullets."}] + [{"role": x["role"], "content": x["content"]} for x in st.session_state.messages if x.get("type") != "image"][-8:],
                    max_tokens=700
                )
                ans = r.choices[0].message.content
                st.markdown(ans)

                if speak:
                    clean = clean_text(ans)
                    # Use Ghana voice code if Twi detected
                    vcode = "en-GH" if any(w in ans.lower() for w in ["maakye", "wo ho", "akwaaba", "medaase", "bra"]) else "en-US"
                    if lang == "French": vcode = "fr-FR"
                    if lang == "Spanish": vcode = "es-ES"
                    if lang == "Arabic": vcode = "ar-SA"
                    if lang == "Hindi": vcode = "hi-IN"
                    js = f"<script>var m=new SpeechSynthesisUtterance('{clean}');m.lang='{vcode}';speechSynthesis.speak(m);</script>"
                    components.html(js, height=0)

                st.session_state.messages.append({"role": "assistant", "content": ans})
                wa2 = urllib.parse.quote(f"{ans[:600]} - SI Worldwide https://si-worldwide.streamlit.app")
                st.link_button("Share to WhatsApp", f"https://wa.me/?text={wa2}", key=f"wa_{len(st.session_state.messages)}")
            except Exception as e:
                st.error(f"Error: {e}")
