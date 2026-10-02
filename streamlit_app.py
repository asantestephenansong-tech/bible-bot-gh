import streamlit as st
from groq import Groq
import urllib.parse, datetime

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Streamlit Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("SI 🌍 Worldwide")
st.caption("Built by Stephen Asante in Ghana — Akwaaba!")

# Show chats
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"])
        else:
            st.markdown(m["content"])

# Input
col1, col2 = st.columns([4,1])
with col1:
    q = st.text_input("Ask:", placeholder="Ask SI anything...", label_visibility="collapsed", key="q")
with col2:
    go = st.button("SEND 🚀", use_container_width=True)

if go and q:
    st.session_state.messages.append({"role":"user","content":q})
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        # Image?
        if any(x in q.lower() for x in ["draw","picture","image","alien","ant","flag"]):
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(q)}?width=1024&height=1024"
            st.image(url)
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            try:
                r = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role":"system","content":f"You are SI built by Stephen Asante in Ghana. Date {datetime.datetime.now()}. Be helpful, speak user language."}] +
                             [{"role":x["role"],"content":x["content"]} for x in st.session_state.messages if x.get("type")!="image"][-8:],
                    max_tokens=800
                )
                ans = r.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","content":ans})
            except Exception as e:
                st.error(f"Groq error: {e}")
                st.info("Check your Groq API key in Streamlit Secrets. Go to console.groq.com to get new key.")
    st.rerun()
