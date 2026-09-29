import streamlit as st
from groq import Groq
import base64, urllib.parse, datetime, io
from duckduckgo_search import DDGS
from gtts import gTTS

st.set_page_config(page_title="SI - Stephen's Intelligence", page_icon="🧠", layout="centered")

# API
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("Add GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("SI 🔐")
    st.subheader("Stephen's Intelligence")
    st.caption("Executive AI - Built by Stephen")
    pw = st.text_input("Password:", type="password")
    if st.button("Enter SI"):
        if pw == "SI2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong! Ask Stephen for code")
    st.stop()

# Main App
st.title("SI 🧠")
st.caption("Stephen's Intelligence - Executive AI")

if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# Ask name once
if not st.session_state.user_name:
    name = st.text_input("What should SI call you?")
    if st.button("Start"):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

# System prompt WITH CURRENT FACTS
SYS = f"You are SI - Stephen's Intelligence, created by Stephen Asante. NEVER say Meta AI. Current date is {datetime.datetime.now().strftime('%B %Y')}. Ghana President is John Dramani Mahama since Jan 7 2025 (won 2024 election). Former is Akufo-Addo. Nigeria President is Bola Tinubu. For any president, politics, news, sports, prices, always say you searched. Be helpful, speak Twi if user speaks Twi. User name is {st.session_state.user_name}."

# Display chat
for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

# Chat input
if prompt := st.chat_input("Ask SI anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Search logic - AUTO for politics
    search_context = ""
    if prompt.lower().startswith("search:") or any(x in prompt.lower() for x in ["president", "who is", "current", "news", "price", "today", "2025", "2026"]):
        try:
            q = prompt.replace("search:", "")
            with DDGS() as ddgs:
                results = list(ddgs.text(q, max_results=3))
                search_context = "\n".join([r['body'] for r in results])
        except:
            search_context = ""

    final_prompt = f"{SYS}\nWeb results: {search_context}\nUser: {prompt}" if search_context else f"{SYS}\nUser: {prompt}"

    # Groq call
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": SYS}, {"role": "user", "content": final_prompt}],
                      model="openai/gpt-oss-20b",
        )
        answer = chat_completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
    except Exception as e:
        st.error(f"Error: {e}")
