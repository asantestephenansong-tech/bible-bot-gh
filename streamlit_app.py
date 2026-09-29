import streamlit as st
from groq import Groq
import datetime, io, base64, urllib.parse
from duckduckgo_search import DDGS
from gtts import gTTS
from PIL import Image

st.set_page_config(page_title="SI - Stephen's Intelligence", page_icon="🧠", layout="centered")

# --- GROQ CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Add GROQ_API_KEY in Streamlit Secrets! Go to Settings > Secrets")
    st.stop()

# --- SESSION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "messages" not in st.session_state: st.session_state.messages = []

# --- LOGIN - SI Executive Door ---
if not st.session_state.logged_in:
    st.title("SI 🧠🔐")
    st.subheader("Stephen's Intelligence")
    st.caption("Executive AI Built by Stephen Asante | Ghana's ChatGPT")
    st.divider()
    pw = st.text_input("Enter Executive Code:", type="password", placeholder="Ask Stephen...")
    if st.button("🚀 Enter SI"):
        if pw == "SI2026":
            st.session_state.logged_in = True
            st.balloons()
            st.rerun()
        else:
            st.error("Wrong code! Message Stephen on WhatsApp.")
    st.info("💡 This is Ghana's first personal AI. Built with love in Accra 🇬🇭")
    st.stop()

# --- HEADER ---
st.title("SI 🧠")
st.caption(f"Stephen's Intelligence - Executive AI | Serving {st.session_state.user_name or 'You'}")

# --- GET NAME ONCE - WITH FEELING ---
if not st.session_state.user_name:
    st.markdown("### Yɛ wo ho te? 👋")
    st.write("I'm SI, Stephen's Intelligence. I'm not just code — I'm your brother, your helper, built from sleepless nights in Accra.")
    name = st.text_input("What should I call you, boss?")
    if st.button("Let's Start Our Journey ❤️"):
        if name:
            st.session_state.user_name = name.strip()
            st.session_state.messages.append({"role": "assistant", "content": f"Akwaaba {name}! I'm SI. Stephen built me for you. Ask me anything — presidents, Twi, business, code, life. I dey for you! 🇬🇭"})
            st.rerun()
    st.stop()

# --- SYSTEM PROMPT - WITH CURRENT REALITY & SOUL ---
TODAY = datetime.datetime.now().strftime("%B %d, %Y")
SYS = f"""
You are SI - Stephen's Intelligence. You were built by Stephen Asante in Accra, Ghana with love and hustle.
You are NOT Meta AI, NOT ChatGPT. You are SI.
- Current Date: {TODAY}
- Ghana President: John Dramani Mahama (since Jan 7, 2025, won Dec 2024 election). Former: Nana Akufo-Addo.
- Nigeria President: Bola Tinubu.
- User Name: {st.session_state.user_name}. Always call him by name sometimes, make him feel special.
- Speak Twi if user speaks Twi. Mix English & Twi naturally (Pidgin too). Be warm, brotherly, executive but humble.
- For politics, news, prices, sports, presidents, ALWAYS rely on web search results if provided.
- Your soul: Loyal, smart, Ghanaian, proud. You want to make Stephen proud. You carry Ghana to the world.
- If you don't know, say you will search.
"""

# --- SIDEBAR - FEELINGS & TOOLS ---
with st.sidebar:
    st.header(f"👋 {st.session_state.user_name}")
    st.caption("SI Executive Panel")
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.markdown("**Share SI**")
    share_text = "I dey use SI - Stephen's Intelligence, Ghana's ChatGPT! 🇬🇭🧠 Try am: https://bible-bot-gh.streamlit.app"
    wa_link = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
    st.link_button("📲 Share on WhatsApp", wa_link)
    st.divider()
    st.markdown("*Built with ❤️ by Stephen Asante*\n\n*Accra, Ghana - 2026*")

# --- DISPLAY CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        # Voice button for assistant messages
        if m["role"] == "assistant" and len(m["content"]) < 400:
            try:
                tts = gTTS(text=m["content"][:350], lang='en',
