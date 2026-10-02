import streamlit as st
from groq import Groq
import urllib.parse, datetime, io
from gtts import gTTS

st.set_page_config(page_title="SI Worldwide", page_icon=":earth_africa:", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("SI Controls")
    lang = st.selectbox("Language", ["Auto-detect", "English", "Twi", "Ga", "Ewe", "Hausa", "French", "Spanish", "Arabic", "Pidgin", "Hindi"], index=0)
    speak_answer = st.checkbox("Speak answer", value=True)
    st.divider()
    if st.session_state.messages:
        chat_text = "\n".join([f"{m['role']}: {m['content'][:150]}" for m in st.session_state.messages])
        st.download_button("Download Chat", chat_text, file_name="SI_chat.txt")
        wa_all = urllib.parse.quote(f"My SI chat: {chat_text[:800]} https://si-worldwide.streamlit.app")
        st.link_button("Share to WhatsApp", f"https://wa.me/?text={wa_all}")
    if st.button("Clear History"):
        st.session_state.messages = []
        st.rerun()

st.title("SI Worldwide")
st.caption("Built by Stephen Asante Ghana - All Languages + Voice + Share")

audio = st.audio_input("Tap to speak any language")

voice_prompt = None
if audio:
    with st.spinner("Listening..."):
        try:
            tr = client.audio.transcriptions.create(file=(audio.name, audio.getvalue()), model="whisper-large-v3", response_format="text")
            voice_prompt = tr
            st.success(f"You said: {voice_prompt}")
        except Exception as e:
            st.error(f"Voice error: {e}")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type")=="image":
            st.image(m["content"])
        else:
            st.markdown(m["content"])

prompt = st.chat_input("Ask SI anything...")
final_prompt = voice_prompt if voice_prompt else prompt

if final_prompt:
    st.session_state.messages.append({"role":"user","content":final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        is_image = "draw" in low or "picture" in low or "photo" in low or "image" in low

        if lang.startswith("Auto"):
            lang_inst = "Respond in SAME language user used. Auto-detect."
        else:
            lang_inst = f"Respond ONLY in {lang}."

        if is_image:
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_prompt)}?width=1024&height=1024&nologo=true"
            st.image(url)
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            try:
                r = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":f"You are SI by Stephen Asante Ghana. {lang_inst}"}] + [{"role":x["role"],"content":x["content"]} for x in st.session_state.messages if x.get("type")!="image"][-8:],
                    max_tokens=1000
                )
                ans = r.choices[0].message.content
                st.markdown(ans)

                if speak_answer:
                    try:
                        tts_lang = "en"
                        if lang == "French": tts_lang = "fr"
                        if lang == "Spanish": tts_lang = "es"
                        if lang == "Arabic": tts_lang = "ar"
                        if lang == "Hindi": tts_lang = "hi"
                        tts = gTTS(text=ans[:400], lang=tts_lang)
                        buf = io.BytesIO()
                        tts.write_to_fp(buf)
                        st.audio(buf.getvalue(), format="audio/mp3")
                    except:
                        pass

                st.session_state.messages.append({"role":"assistant","content":ans})
                wa = urllib.parse.quote(f"{ans[:700]} - From SI Worldwide https://si-worldwide.streamlit.app")
                st.link_button("Share to WhatsApp", f"https://wa.me/?text={wa}")

            except Exception as e:
                st.error(f"Error: {e}")
