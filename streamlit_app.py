import streamlit as st
from groq import Groq
import datetime, urllib.parse
from duckduckgo_search import DDGS
from gtts import gTTS
import io

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="centered")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("SI 🌍 Worldwide")
    st.subheader("Built by Stephen - Global AI")
    pw = st.text_input("Code:", type="password")
    if st.button("Enter"):
        if pw == "SI2026":
            st.session_state.logged_in = True
            st.balloons()
            st.rerun()
        else:
            st.error("Wrong")
    st.stop()

st.title("SI 🌍")
st.caption(f"Serving {st.session_state.user_name or 'You'}")

if not st.session_state.user_name:
    name = st.text_input("Your name?")
    if st.button("Start"):
        if name:
            st.session_state.user_name = name.strip()
            st.session_state.messages.append({"role": "assistant", "content": f"Akwaaba {name}! I'm SI Ultimate - I speak all languages and generate pictures! Try: 'picture of an airplane' 🌍"})
            st.rerun()
    st.stop()

TODAY = datetime.datetime.now().strftime("%B %d, %Y")
SYS = f"You are SI Ultimate Worldwide, built by Stephen Asante in Ghana but GLOBAL like Meta AI. Date {TODAY}. User {st.session_state.user_name}. RULES: Detect language and reply in SAME language. You speak all languages. You are global, not attached to one country. Ghana President is John Mahama 2025."

with st.sidebar:
    st.write(f"Hello {st.session_state.user_name}")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "IMAGE_URL::" in m["content"]:
            text_part = m["content"].split("IMAGE_URL::")[0]
            url_part = m["content"].split("IMAGE_URL::")[1].strip()
            if text_part:
                st.write(text_part)
            st.image(url_part)
        else:
            st.write(m["content"])

prompt = st.chat_input("Ask anything or 'picture of...'")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    is_pic = any(k in prompt.lower() for k in ["picture of", "image of", "photo of", "generate", "draw a"])

    if is_pic:
        with st.chat_message("assistant"):
            with st.spinner("🎨 Generating picture..."):
                # Clean prompt
                clean = prompt.lower()
                for w in ["picture of", "image of", "photo of", "generate", "draw", "a picture", "a image"]:
                    clean = clean.replace(w, "")
                clean = clean.strip() or "airplane"
                safe_prompt = urllib.parse.quote(clean + " highly detailed 4k")
                img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true&seed={abs(hash(prompt)) % 10000}"
                st.image(img_url, caption=clean)
                txt = f"Here is your image: **{clean}** 🌍✈️"
                st.write(txt)
                st.session_state.messages.append({"role": "assistant", "content": f"{txt}\nIMAGE_URL::{img_url}"})
    else:
        # Search + chat
        search_text = ""
        if any(k in prompt.lower() for k in ["president", "who is", "current", "news"]):
            try:
                with DDGS() as ddgs:
                    res = list(ddgs.text(prompt, max_results=2))
                    search_text = " ".join([r['body'] for r in res])
            except:
                pass

        final_q = f"Search: {search_text}\nQuestion: {prompt}\nReply in user's language!" if search_text else prompt

        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    comp = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "system", "content": SYS},
                            {"role": "user", "content": final_q}
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )
                    ans = comp.choices[0].message.content
                    st.write(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error(f"Error: {e}")
