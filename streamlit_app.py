import streamlit as st
from groq import Groq
import datetime, urllib.parse
from duckduckgo_search import DDGS

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="centered")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "user_name" not in st.session_state: st.session_state.user_name = ""
if "messages" not in st.session_state: st.session_state.messages = []

st.title("SI 🌍 Worldwide")
st.caption(f"Global AI Built by Stephen Asante in Ghana | Serving {st.session_state.user_name or 'You'}")

if not st.session_state.user_name:
    name = st.text_input("What should I call you? / Comment tu t'appelles?")
    if st.button("Start Chatting 🌍❤️"):
        if name:
            st.session_state.user_name = name.strip()
            st.session_state.messages.append({"role": "assistant", "content": f"Akwaaba {name}! 🌍 I'm SI - Stephen's Intelligence. I speak ALL languages, I generate pictures, I search the web! Just like Meta AI, but built in Ghana! Try me: 'picture of an eagle' or 'Bonjour' 🚀"})
            st.rerun()
    st.stop()

TODAY = datetime.datetime.now().strftime("%B %d, %Y")
SYS = f"You are SI Worldwide, built by Stephen Asante in Ghana but GLOBAL like Meta AI. Date {TODAY}. User {st.session_state.user_name}. RULES: Auto-detect language and reply in SAME language. Speak all languages. Global, not attached to one country. Ghana President John Mahama 2025."

with st.sidebar:
    st.write(f"👋 {st.session_state.user_name}")
    st.caption("SI Worldwide - No Code Needed")
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.link_button("📲 Share SI", "https://wa.me/?text=I%20dey%20use%20SI%20Worldwide%20Built%20in%20Ghana%20https://bible-bot-gh.streamlit.app")

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "IMAGE_URL::" in m["content"]:
            text_part = m["content"].split("IMAGE_URL::")[0]
            url_part = m["content"].split("IMAGE_URL::")[1].strip()
            if text_part: st.write(text_part)
            st.image(url_part)
        else:
            st.write(m["content"])

prompt = st.chat_input(f"Ask SI anything, {st.session_state.user_name}...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    is_pic = any(k in prompt.lower() for k in ["picture of", "image of", "photo of", "generate", "draw a", "imagen", "create image"])

    if is_pic:
        with st.chat_message("assistant"):
            with st.spinner("🎨 Generating picture..."):
                clean = prompt.lower()
                for w in ["picture of", "image of", "photo of", "generate", "draw", "a picture", "a image", "picture"]:
                    clean = clean.replace(w, "")
                clean = clean.strip() or "beautiful landscape"
                safe = urllib.parse.quote(clean + " highly detailed 4k")
                img_url = f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&seed={abs(hash(prompt)) % 10000}"
                st.image(img_url, caption=clean)
                txt = f"Here is your image: **{clean}** 🌍🖼️"
                st.write(txt)
                st.session_state.messages.append({"role": "assistant", "content": f"{txt}\nIMAGE_URL::{img_url}"})
    else:
        search_text = ""
        if any(k in prompt.lower() for k in ["president", "who is", "current", "news"]):
            try:
                with DDGS() as ddgs:
                    res = list(ddgs.text(prompt, max_results=2))
                    search_text = " ".join([r['body'] for r in res])
            except: pass
        final_q = f"Search: {search_text}\nQuestion: {prompt}\nReply in user's language!" if search_text else prompt
        try:
            with st.chat_message("assistant"):
                with st.spinner("SI thinking... 🌍"):
                    comp = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "system", "content": SYS}, {"role": "user", "content": final_q}],
                        temperature=0.7, max_tokens=800
                    )
                    ans = comp.choices[0].message.content
                    st.write(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption(f"SI 🌍 Worldwide | Built by Stephen | Free for the World | {TODAY}")
