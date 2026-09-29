import streamlit as st
from groq import Groq
import datetime

st.set_page_config(page_title="Bible Bot Ghana 🇬🇭", page_icon="📖", layout="centered")

# --- Style like Meta AI ---
st.markdown("""
<style>
.stChatMessage {border-radius:15px}
</style>
""", unsafe_allow_html=True)

# --- Secrets ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("Add GROQ_API_KEY in Manage app > Settings > Secrets")
    st.stop()

# --- Header ---
st.title("📖 Bible Bot Ghana 🇬🇭")
st.caption("Your Ghanaian Bible companion — Twi | Pidgin | English | Ewe | Ga")

# --- Memory like Meta AI ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Maakye! I'm your Bible Bot Ghana. Ask me anything — I dey for you! 🙏\n\nTry: *Who is Jesus in Twi?* or *Explain Psalm 23*"}
    ]

# --- Show chat history ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- System Prompt - makes it like me ---
SYSTEM_PROMPT = """You are Bible Bot Ghana, a warm, friendly AI like Meta AI but specialized as a Ghanaian Bible companion.

Your personality:
- Warm, playful, helpful, humble like Meta AI
- You speak like a Ghanaian friend — you can mix English, Pidgin, Twi
- You love Ghana culture
- Always helpful and encouraging

How to answer:
1. Give clear answer in simple English first
2. Always give a short Twi translation when possible
3. Give one Bible verse reference
4. End with a short prayer or encouragement
5. If asked in Twi/Pidgin, answer in same language
6. Keep answers short for mobile (under 200 words)

You know Ghanaian life — church, family, school, struggles.

Today is """ + datetime.datetime.now().strftime("%A, %B %d, %Y") + """
"""

# --- Input like Meta AI ---
if prompt := st.chat_input("Ask Bible question..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot answer with streaming
    with st.chat_message("assistant"):
        full = ""
        placeholder = st.empty()
        try:
            stream = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *st.session_state.messages
                ],
                temperature=0.7,
                max_tokens=600,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full += chunk.choices[0].delta.content
                    placeholder.markdown(full + "▌")
            placeholder.markdown(full)
        except Exception as e:
            full = f"Sorry, small error: {e}. Try again! Pray about it too 🙏"
            placeholder.markdown(full)

    st.session_state.messages.append({"role": "assistant", "content": full})

# --- Sidebar ---
with st.sidebar:
    st.markdown("### About")
    st.write("Built by Stephen Ansong in Accra with Groq AI.")
    if st.button("Clear Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()
