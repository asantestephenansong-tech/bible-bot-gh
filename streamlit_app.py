import streamlit as st
from groq import Groq
import urllib.parse, datetime, re
import streamlit.components.v1 as components

st.set_page_config(page_title="SI Worldwide", page_icon=":earth_africa:", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

def clean_for_speech(text):
    text = re.sub(r'\*\*|__|\*|#|•|`', ' ', text)
    text = re.sub(r'https?://\S+', ' ', text)
    text = text[:500]
    return text

# VOICE INPUT THAT UNDERSTANDS ALL LANGUAGES - Uses phone's own language engine
voice_html = """
<div style="background:#1e1e1e;padding:15px;border-radius:10px;margin-bottom:10px">
  <button id="startBtn" style="background:#00d26a;color:white;border:none;padding:12px 20px;border-radius:8px;font-size:16px;width:100%">🎤 Tap & Speak ANY Language - Twi, Ga, Ewe, Hausa</button>
  <p id="status" style="color:#aaa;margin-top:10px">Waiting...</p>
  <p id="result" style="color:#00ff88;font-size:18px;font-weight:bold"></p>
</div>
<script>
var recognition;
var isRunning = false;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = ''; // Auto-detect - let phone decide (supports all phone languages!)
  
  recognition.onstart = function(){ document.getElementById('status').innerText = '🔴 Listening... Speak Twi, Ga, Ewe, Hausa, English...'; }
  recognition.onresult = function(event){
    var transcript = event.results[0][0].transcript;
    document.getElementById('result').innerText = 'You said: ' + transcript;
    document.getElementById('status').innerText = '✅ Got it! Sending to SI...';
    // Send to Streamlit
    window.parent.postMessage({type: 'streamlit:setComponentValue', value: transcript}, '*');
  }
  recognition.onerror = function(e){ document.getElementById('status').innerText = 'Error: ' + e.error + ' - Try again'; }
  recognition.onend = function(){ isRunning = false; }
}

document.getElementById('startBtn').onclick = function(){
  if(recognition){
    if(!isRunning){ recognition.start(); isRunning=true; }
  } else {
    document.getElementById('status').innerText = '❌ Your browser does not support voice. Use Chrome.';
  }
}
</script>
"""

with st.sidebar:
    st.title("SI Controls")
    lang = st.selectbox("Answer Language", ["Auto-detect (Same as you)", "English", "Twi", "Ga", "Ewe", "Hausa", "French", "Spanish", "Arabic", "Pidgin", "Hindi"], index=0)
    speak_answer = st.checkbox("🔊 Speak answer", value=True)
    st.divider()
    if st.session_state.messages:
        chat_text = "\n".join([f"{m['role']}: {m['content'][:150]}" for m in st.session_state.messages])
        st.download_button("💾 Download History", chat_text, file_name="SI_chat.txt")
        wa_all = urllib.parse.quote(f"My SI chat https://si-worldwide.streamlit.app")
        st.link_button("📱 Share to WhatsApp", f"https://wa.me/?text={wa_all}")
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.rerun()

st.title("SI Worldwide")
st.caption("Built by Stephen Asante Ghana - V3.2 Understands ALL languages")

# NEW VOICE SYSTEM
st.write("**NEW: Phone Voice - Understands Twi, Ga, Ewe 100%**")
voice_result = components.html(voice_html, height=180)

# Also keep old audio_input as backup
st.write("Backup (if top button fails):")
audio = st.audio_input("")

voice_prompt = None
# Check if JS voice gave us text
if st.session_state.voice_text:
    voice_prompt = st.session_state.voice_text

if audio:
    with st.spinner("Transcribing..."):
        try:
            tr = client.audio.transcriptions.create(file=(audio.name, audio.getvalue()), model="whisper-large-v3", response_format="text")
            voice_prompt = tr
            st.success(f"You said: {voice_prompt}")
        except Exception as e:
            st.error(f"{e}")

# Use a text input to capture JS result manually for now - user copies
manual_voice = st.text_input("If you spoke above, your words appear here - press Enter to send:", key="manual_voice_input")
if manual_voice and manual_voice != st.session_state.get("last_voice"):
    voice_prompt = manual_voice
    st.session_state.last_voice = manual_voice

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type")=="image":
            st.image(m["content"])
        else:
            st.markdown(m["content"])

prompt = st.chat_input("Or type here...")

final_prompt = voice_prompt if voice_prompt else prompt

if final_prompt:
    # Clear manual input
    if "manual_voice_input" in st.session_state:
        st.session_state.manual_voice_input = ""
    st.session_state.messages.append({"role":"user","content":final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        is_image = "draw" in low or "picture" in low or "photo" in low

        if lang.startswith("Auto"):
            lang_inst = "Detect user language (Twi, Ga, Ewe, Hausa, English, etc) and respond in SAME language. If Twi, answer Twi."
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
                    messages=[{"role":"system","content":f"You are SI by Stephen Asante Ghana. {lang_inst} Keep answer short, plain text, no ** or bullet symbols."}] + [{"role":x["role"],"content":x["content"]} for x in st.session_state.messages if x.get("type")!="image"][-8:],
                    max_tokens=800
                )
                ans = r.choices[0].message.content
                st.markdown(ans)

                if speak_answer:
                    clean = clean_for_speech(ans).replace("'", "\\'").replace('"','').replace("\n"," ")
                    lang_map = {"English":"en-US","Twi":"en-GH","Ga":"en-GH","Ewe":"en-GH","Hausa":"en-NG","French":"fr-FR","Spanish":"es-ES","Arabic":"ar-SA","Hindi":"hi-IN","Auto-detect (Same as you)":"en-US"}
                    code = lang_map.get(lang, "en-US")
                    if any(w in ans.lower() for w in ["maakye","wo ho","akwaaba","medaase","atopa"]):
                        code = "en-GH"
                    speak_js = f"<script>var msg=new SpeechSynthesisUtterance('{clean}');msg.lang='{code}';window.speechSynthesis.speak(msg);</script>"
                    components.html(speak_js, height=0)

                st.session_state.messages.append({"role":"assistant","content":ans})
                wa = urllib.parse.quote(f"{ans[:700]} - From SI Worldwide https://si-worldwide.streamlit.app")
                st.link_button("📱 Share to WhatsApp", f"https://wa.me/?text={wa}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.session_state.voice_text = ""
    st.rerun()
