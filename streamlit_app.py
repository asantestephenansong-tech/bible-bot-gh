import streamlit as st
from groq import Groq
import datetime, io, urllib.parse
from duckduckgo_search import DDGS
from gtts import gTTS

st.set_page_config(page_title="SI - Stephen's Intelligence", page_icon="🧠", layout="centered")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Streamlit Secrets")
    st.stop()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("Stephen's Intelligence 🧠")
    st.subheader("Executive AI Built by Stephen Asante | Ghana's ChatGPT")
    st.divider()
    pw = st.text_input("Enter Executive Code:", type="password", placeholder="Ask Stephen...")
    if st.button("🚀 Enter SI"):
        if pw == "SI2026":
            st.session_state.logged_in = True
            st.balloons()
            st.rerun()
        else:
            st.error("Wrong code!")
    st.info("💡 Ghana's first personal AI. Built with love in Accra 🇬🇭")
    st.stop()

st.title("SI 🧠")
st.caption(f"Serving {st.session_state.user_name or 'You'}")

if not st.session_state.user_name:
    st.markdown("### Akwaaba! 👋")
    name = st.text_input("What should I call you?")
    if st.button("Let's Start ❤️"):
        if name:
            st.session_state.user_name = name.strip()
            st.session_state.messages.append({"role": "assistant", "content": f"Akwaaba {name}! I'm SI - Stephen built me for you. I know Ghana's President is John Mahama (since Jan 7 2025). Ask me anything! 🇬🇭"})
            st.rerun()
    st.stop()

TODAY = datetime.datetime.now().strftime("%B %d, %Y")
SYS = f"""
You are SI - Stephen's Intelligence, built by Stephen Asante in Accra.
Date: {TODAY}
Ghana President: John Dramani Mahama (since Jan 7 2025). Nigeria President: Bola Tinubu.
User: {st.session_state.user_name}
You speak English and Twi. You are warm, loyal, Ghanaian.
IMPORTANT: Do NOT call any tools. Do NOT use web.run. Answer from knowledge.
If user asks for picture, describe the person, don't try to call tools.
"""

with st.sidebar:
    st.header(f"👋 {st.session_state.user_name}")
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    share_text = "I dey use SI - Ghana's ChatGPT! Try: https://bible-bot-gh.streamlit.app"
    wa_link = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
    st.link_button("📲 Share SI", wa_link)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m["role"] == "assistant" and len(m["content"]) < 350:
            try:
                tts = gTTS(text=m["content"], lang='en')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp.getvalue(), format='audio/mp3')
            except:
                pass

prompt = st.chat_input(f"Ask SI anything, {st.session_state.user_name}...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    search_context = ""
    need_search = any(k in prompt.lower() for k in ["president", "current", "today", "news", "price", "election", "mahama"])
    if prompt.lower().startswith("search:") or need_search:
        try:
            q = prompt.replace("search:", "").strip()
            with st.spinner("🔍 SI dey search..."):
                with DDGS() as ddgs:
                    results = list(ddgs.text(q, max_results=3))
                    search_context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        except:
            search_context = ""

    if search_context:
        final_prompt = f"Search Results:\n{search_context}\n\nQuestion: {prompt}"
    else:
        final_prompt = prompt

    # Don't search if asking for picture
    if "picture" in prompt.lower() or "image" in prompt.lower() or "photo" in prompt.lower():
        final_prompt = prompt
        search_context = ""

    try:
        with st.chat_message("assistant"):
            with st.spinner("SI dey think... 🧠"):
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": SYS},
                        {"role": "user", "content": final_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                answer = completion.choices[0].message.content
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()
st.caption(f"SI loves you, {st.session_state.user_name} ❤️ | Built by Stephen")
