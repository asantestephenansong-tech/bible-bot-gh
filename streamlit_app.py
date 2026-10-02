import streamlit as st
from groq import Groq
import urllib.parse, datetime

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("SI 🌍 Worldwide")
st.caption("Built by Stephen Asante in Ghana — Akwaaba!")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type")=="image":
            st.image(m["content"])
        else:
            st.markdown(m["content"])

prompt = st.chat_input("Ask SI anything...")

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        low=prompt.lower()
        is_image=any(k in low for k in ["draw a","draw an","picture of","photo of","image of","create a picture","generate"])
        if is_image:
            url=f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true"
            st.image(url, caption=prompt)
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            try:
                r=client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":f"You are SI built by Stephen Asante in Ghana. Date {datetime.datetime.now()}. Be helpful."}]+[{"role":x["role"],"content":x["content"]} for x in st.session_state.messages if x.get("type")!="image"][-8:],
                    max_tokens=1000
                )
                ans=r.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","content":ans})
            except Exception as e:
                st.error(f"Error: {e}")
🌍 Language: [Auto-detect ▼]
Options: Auto-detect, English, Twi, Ga, Ewe, Hausa, French, Spanish, Arabic...
