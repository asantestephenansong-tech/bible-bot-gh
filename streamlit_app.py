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

def clean_for_speech(text):
    # Remove markdown, emojis, links, punctuation that causes bug
    text = re.sub(r'\*\*|__|\*|#|•|- \[|\]|\(.*?\)', ' ', text)
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\u00C0-\u024F\s,.?!\']', ' ', text)
    text = text[:400]
    return text

def speak_js(text, lang_code="en-US"):
    clean = clean_for_speech(text).replace("'", "\\'").replace('"', '')
    # Uses YOUR PHONE speaker - supports 100+ languages automatically
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance('{clean}');
    msg.lang = '{lang_code}';
    msg.rate = 1;
    window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js, height=0)

with st.sidebar:
    st.title("SI Controls")
    lang = st.selectbox("Language", ["Auto-detect", "English", "Twi", "Ga", "Ewe", "Hausa", "French", "Spanish", "Arabic", "Pidgin", "Hindi"], index=0)
    speak_answer = st.checkbox("🔊 Speak answer (Phone voice)", value=True)
    st.divider()
    st.subheader("Chat History")
    if st.session_state.messages:
        chat_text = "\n".join([f"{m['role']}: {m['content'][:150]}" for m in st.session_state.messages])
        st.download_button("💾 Download Chat", chat_text, file_name="SI_chat.txt")
        wa_all = urllib.parse.quote(f"My SI chat: {chat_text[:800]} https://si-worldwide.streamlit.app")
        st.link_button("📱 Share to WhatsApp", f"https://wa.me/?text={wa_all}")
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

st.title("SI Worldwide")
st.caption("Built by Stephen Asante Ghana - All Languages + Voice + Share")

audio = st.audio_input("🎤 Tap to speak any language - Twi, Ga, Ewe, Hausa, French...")

voice_prompt = None
if audio:
    with st.spinner("Listening... understands ALL languages"):
        try:
            # Give whisper hint for Ghana languages
            tr = client.audio.transcriptions.create(
                file=(audio.name, audio.getvalue()),
                model="whisper-large-v3",
                prompt="Twi, Ga, Ewe, Hausa, Akan, English, French, Pidgin. Transcribe exactly.",
                response_format="text"
            )
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
            lang_inst = "Respond in SAME language user used. If Twi, answer in Twi. If Ga, answer Ga. Auto-detect all Ghana languages and world languages."
        else:
            lang_inst = f"Respond ONLY in {lang}. Even if user speaks English, answer in {lang}."

        if is_image:
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_prompt)}?width=1024&height=1024&nologo=true"
            st.image(url)
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            try:
                r = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":f"You are SI by Stephen Asante Ghana. {lang_inst} Keep answer short, clean, no markdown symbols like ** or •. Just plain text for voice."}] + [{"role":x["role"],"content":x["content"]} for x in st.session_state.messages if x.get("type")!="image"][-8:],
                    max_tokens=800
                )
                ans = r.choices[0].message.content
                st.markdown(ans)

                if speak_answer:
                    # Map language to phone voice code - phone handles Twi/Ga as English accent but reads Twi words correctly
                    lang_map = {"English":"en-US", "Twi":"en-GH", "Ga":"en-GH", "Ewe":"en-GH", "Hausa":"en-NG", "French":"fr-FR", "Spanish":"es-ES", "Arabic":"ar-SA", "Hindi":"hi-IN", "Auto-detect":"en-US"}
                    code = lang_map.get(lang, "en-US")
                    # If answer is Twi but selector is Auto, use Ghana voice
                    if any(w in ans.lower() for w in ["maakye", "maaha", "wo ho", "akwaaba", "medaase"]):
                        code = "en-GH"
                    speak_js(ans, code)

                st.session_state.messages.append({"role":"assistant","content":ans})
                wa = urllib.parse.quote(f"{ans[:700]} - From SI Worldwide https://si-worldwide.streamlit.app")
                st.link_button("📱 Share to WhatsApp", f"https://wa.me/?text={wa}")

            except Exception as e:
                st.error(f"Error: {e}")
