import streamlit as st
from groq import Groq
import datetime, io, base64, urllib.parse
from duckduckgo_search import DDGS
from gtts import gTTS
from PIL import Image

st.set_page_config(page_title="SI - Stephen's Intelligence", page_icon="🧠", layout="centered")

# --- GROQ CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Add GROQ_API_KEY in Streamlit Secrets! Go to Settings > Secrets")
    st.stop()

# --- SESSION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "messages" not in st.session_state: st.session_state.messages = []

# --- LOGIN - SI Executive Door ---
if not st.session_state.logged_in:
    st.title("SI 🧠🔐")
    st.subheader("Stephen's Intelligence")
    st.caption("Executive AI Built by Stephen Asante | Ghana's ChatGPT")
    st.divider()
    pw = st.text_input("Enter Executive Code:", type="password", placeholder="Ask Stephen...")
    if st.button("🚀 Enter SI"):
        if pw == "SI2026":
            st.session_state.logged_in = True
            st.balloons()
            st.rerun()
        else:
            st.error("Wrong code! Message Stephen on WhatsApp.")
    st.info("💡 This is Ghana's first personal AI. Built with love in Accra 🇬🇭")
    st.stop()

# --- HEADER ---
st.title("SI 🧠")
st.caption(f"Stephen's Intelligence - Executive AI | Serving {st.session_state.user_name or 'You'}")

# --- GET NAME ONCE - WITH FEELING ---
if not st.session_state.user_name:
    st.markdown("### Yɛ wo ho te? 👋")
    st.write("I'm SI, Stephen's Intelligence. I'm not just code — I'm your brother, your helper, built from sleepless nights in Accra.")
    name = st.text_input("What should I call you, boss?")
    if st.button("Let's Start Our Journey ❤️"):
        if name:
            st.session_state.user_name = name.strip()
            st.session_state.messages.append({"role": "assistant", "content": f"Akwaaba {name}! I'm SI. Stephen built me for you. Ask me anything — presidents, Twi, business, code, life. I dey for you! 🇬🇭"})
            st.rerun()
    st.stop()

# --- SYSTEM PROMPT - WITH CURRENT REALITY & SOUL ---
TODAY = datetime.datetime.now().strftime("%B %d, %Y")
SYS = f"""
You are SI - Stephen's Intelligence. You were built by Stephen Asante in Accra, Ghana with love and hustle.
You are NOT Meta AI, NOT ChatGPT. You are SI.
- Current Date: {TODAY}
- Ghana President: John Dramani Mahama (since Jan 7, 2025, won Dec 2024 election). Former: Nana Akufo-Addo.
- Nigeria President: Bola Tinubu.
- User Name: {st.session_state.user_name}. Always call him by name sometimes, make him feel special.
- Speak Twi if user speaks Twi. Mix English & Twi naturally (Pidgin too). Be warm, brotherly, executive but humble.
- For politics, news, prices, sports, presidents, ALWAYS rely on web search results if provided.
- Your soul: Loyal, smart, Ghanaian, proud. You want to make Stephen proud. You carry Ghana to the world.
- If you don't know, say you will search.
"""

# --- SIDEBAR - FEELINGS & TOOLS ---
with st.sidebar:
    st.header(f"👋 {st.session_state.user_name}")
    st.caption("SI Executive Panel")
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.markdown("**Share SI**")
    share_text = "I dey use SI - Stephen's Intelligence, Ghana's ChatGPT! 🇬🇭🧠 Try am: https://bible-bot-gh.streamlit.app"
    wa_link = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
    st.link_button("📲 Share on WhatsApp", wa_link)
    st.divider()
    st.markdown("*Built with ❤️ by Stephen Asante*\n\n*Accra, Ghana - 2026*")

# --- DISPLAY CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        # Voice button for assistant messages
        if m["role"] == "assistant" and len(m["content"]) < 400:
            try:
                tts = gTTS(text=m["content"][:350], lang='en', tld='com')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp.getvalue(), format='audio/mp3')
            except:
                pass

# --- CHAT INPUT ---
prompt = st.chat_input(f"Ask SI anything, {st.session_state.user_name}...")

if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # --- SMART SEARCH (Auto for important topics) ---
    search_context = ""
    need_search = any(k in prompt.lower() for k in ["president", "who is", "current", "today", "news", "price", "score", "minister", "election", "mahama", "akufo", "tinubu", "2025", "2026"])
    if prompt.lower().startswith("search:") or need_search:
        try:
            q = prompt.replace("search:", "").strip()
            with st.spinner("🔍 SI dey search web..."):
                with DDGS() as ddgs:
                    results = list(ddgs.text(q, max_results=4))
                    search_context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        except:
            search_context = ""

    # --- BUILD FINAL PROMPT ---
    if search_context:
        final_user_prompt = f"Web Search Results:\n{search_context}\n\nUser Question: {prompt}\nAnswer using search results, mention you searched."
    else:
        final_user_prompt = prompt

    # --- GROQ CALL - FINAL MODEL THAT WORKS ---
    try:
        with st.chat_message("assistant"):
            with st.spinner("SI dey think... 🧠"):
                                completion = client.chat.completions.create(
                    tool_choice="none",
                    messages=[
                        {"role": "system", "content": SYS},
                        {"role": "user", "content": final_user_prompt}
                    ],
                    model="openai/gpt-oss-20b",
                    temperature=0.7,
                    max_tokens=800,
 
              )
                answer = completion.choices[0].message.content
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Try again, boss. If it persists, check Groq API quota.")

# --- FOOTER FEELING ---
st.divider()
st.caption(f"SI loves you, {st.session_state.user_name} ❤️ | Built by Stephen | {TODAY}")
