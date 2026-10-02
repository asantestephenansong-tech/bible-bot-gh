import streamlit as st
from groq import Groq
import datetime, urllib.parse

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="centered")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("❌ Add GROQ_API_KEY in Streamlit Secrets")
    st.stop()

if "user_name" not in st.session_state: st.session_state.user_name = "Stephen"
if "messages" not in st.session_state: st.session_state.messages = []

st.title("SI 🌍 Worldwide")
st.caption("Global AI Built by Stephen Asante in Ghana — Akwaaba Stephen!")

# Show old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

# Input - FIXED
prompt = st.chat_input("Ask SI anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Image?
        if any(x in prompt.lower() for x in ["draw", "picture", "image", "photo", "logo"]):
            enc = urllib.parse.quote(prompt)
            img_url = f"https://image.pollinations.ai/prompt/{enc}?width=1024&height=1024"
            st.image(img_url, caption=prompt)
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": img_url})
        else:
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"system","content": f"You are SI, built by Stephen Asante in Ghana. User is {st.session_state.user_name}. Be helpful, speak user's language. Date {datetime.datetime.now()}"}] +
                             [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m.get("type")!="image"][-6:],
                    max_tokens=1000
                )
                ans = res.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"Groq Error: {e}")
