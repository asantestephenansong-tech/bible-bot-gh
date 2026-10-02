import streamlit as st
from groq import Groq
import datetime, urllib.parse
from duckduckgo_search import DDGS

st.set_page_config(page_title="SI Worldwide - Meta AI Clone", page_icon="🌍", layout="centered")

# --- SETUP GROQ ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = "Stephen"

# --- SIDEBAR LIKE META AI ---
with st.sidebar:
    st.title("SI 🌍 Features")
    st.markdown("Built by Stephen Asante")
    st.divider()
    search_on = st.toggle("🌐 Web Search", value=True)
    image_on = st.toggle("🎨 Image Gen", value=True)
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("SI Worldwide | Akwaaba!")

# --- FUNCTIONS ---
def search_web(q):
    try:
        with DDGS() as ddgs:
            res = list(ddgs.text(q, max_results=3))
            if res:
                return "\n".join([f"- {r['title']}: {r['body'][:200]}" for r in res])
    except:
        pass
    return ""

def gen_image(prompt):
    enc = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{enc}?width=1024&height=1024&nologo=true&seed=7"

# --- MAIN UI ---
st.title("SI 🌍 Worldwide")
st.caption(f"Global AI Built by Stephen Asante in Ghana — Akwaaba {st.session_state.user_name}! | I speak ALL languages, generate pictures, search the web!")

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], caption=m.get("caption",""))
        else:
            st.markdown(m["content"])

# --- CHAT INPUT - MOBILE FIX ---
col1, col2 = st.columns([4,1])
with col1:
    prompt = st.text_input("Ask SI:", placeholder="Ask SI anything...", label_visibility="collapsed", key="input_box")
with col2:
    send = st.button("SEND 🚀", use_container_width=True)

if send and prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        is_image = any(k in prompt.lower() for k in ["draw","picture","image","photo","logo"])
        if is_image and image_on:
            url = gen_image(prompt)
            st.image(url, caption=prompt)
            st.session_state.messages.append({"role":"assistant","type":"image","content":url,"caption":prompt})
        else:
            context = ""
            if search_on:
                with st.spinner("Searching..."):
                    context = search_web(prompt)

            system = f"You are SI built by Stephen in Ghana. User {st.session_state.user_name}. Date {datetime.datetime.now()}. Web: {context}. Reply in user language."
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role":"system","content":system}] + [{"role": x["role"], "content": x["content"]} for x in st.session_state.messages if x.get("type")!="image"][-6:],
                    max_tokens=1000
                )
                ans = completion.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","content":ans})
            except Exception as e:
                st.error(f"Error: {e}")
    st.rerun()
