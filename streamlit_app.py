import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="Bible Bot Ghana", page_icon="📖")
st.title("📖 Bible Bot Ghana 🇬🇭")
st.write("Ask me any Bible question - English, Twi or Pidgin!")

api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.warning("Add GROQ_API_KEY in Streamlit Secrets after this.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content":"Maakye! I am your Bible Bot Ghana. How can I help?"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ask Bible question..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        resp = client.chat.completions.create(
            model=model="llama-3.1-8b-instant"
            messages=[{"role":"system","content":"You are Bible Bot Ghana. Answer with Bible verses, simple English, Twi or Pidgin when asked."}, *st.session_state.messages]
        )
        ans = resp.choices[0].message.content
        st.markdown(ans)
        st.session_state.messages.append({"role":"assistant","content":ans})
