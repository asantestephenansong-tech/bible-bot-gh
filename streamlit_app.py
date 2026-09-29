import streamlit as st
from groq import Groq
import base64, urllib.parse, datetime, io
from duckduckgo_search import DDGS
from gtts import gTTS

st.set_page_config(page_title="SI - Stephen's Intelligence", page_icon="🧠", layout="centered")

# API
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("Add GROQ_API_KEY in Streamlit Secrets"); st.stop()

# Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("SI 🔐")
    st.subheader("Stephen's Intelligence")
    st.caption("Executive AI - Built by Stephen")
    pw = st.text_input("Password:", type="password")
    if st.button("Enter SI"):
        if pw == "SI2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong! Ask Stephen for password")
    st.stop()

# Main App
st.title("SI 🧠")
st.caption("Stephen's Intelligence - Executive AI")

if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Akwaaba! I am SI - Stephen's Intelligence. Built by Stephen. I speak Twi, create pictures, search web, and read photos. What's your name?"}
    ]

with st.sidebar:
    st.markdown("### SI\nStephen's Intelligence")
    name = st.text_input("Your Name:", value=st.session_state.user_name)
    if name:
        st.session_state.user_name = name

    uploaded = st.file_uploader("📤 Upload Photo", type=["jpg","png","jpeg"])
    b64_image = None
    if uploaded:
        st.image(uploaded)
        b64_image = base64.b64encode(uploaded.getvalue()).decode()

    voice_on = st.checkbox("🔊 Voice Answer", True)
    st.markdown("---")
    st.markdown("💎 SI Executive\nBuilt by Stephen")
    st.markdown("💰 MoMo: 055XXXXXXX")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "image_url" in m:
            st.image(m["image_url"])
        if m["role"] == "assistant":
            st.link_button("📤 Share on WhatsApp", f"https://wa.me/?text={urllib.parse.quote(m['content'][:800])}")

SYS = f"You are SI - Stephen's Intelligence, built by Stephen. Your name is SI, never say you are Meta AI or Bible Bot. User name is {st.session_state.user_name or 'Friend'}. Speak warm, smart, mix Twi and English. Be executive, helpful. Date: {datetime.datetime.now()}"

if prompt := st.chat_input("Ask SI anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        image_url = None
        try:
            low = prompt.lower()
            # PICTURE FEATURE
            if any(k in low for k in ["picture", "image", "draw", "generate"]):
                clean = low.replace("picture of","").replace("picture","").replace("image","").replace("draw","").replace("generate","").strip() or "future executive technology"
                q = urllib.parse.quote(clean)
                image_url = f"https://image.pollinations.ai/prompt/{q}?width=800&height=800&nologo=true"
                full_text = f"Here is {clean} — created by SI:"
                placeholder.markdown(full_text)
                st.image(image_url)
                full_text += "\n\nSI Executive 🧠"

            # SEARCH FEATURE
            elif low.startswith("search:"):
                sq = prompt.replace("search:","").strip()
                placeholder.markdown(f"🔍 Searching: {sq}...")
                results = DDGS().text(sq, max_results=3)
                context = "\n".join([r['body'] for r in results])
                comp = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":SYS + f"\nWeb results:\n{context}"},{"role":"user","content":prompt}]
                )
                full_text = comp.choices[0].message.content
                placeholder.markdown(full_text)

            # PHOTO READING
            elif b64_image:
                placeholder.markdown("👁️ SI is reading your photo...")
                comp = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role":"system","content":SYS},
                        {"role":"user","content":[
                            {"type":"text","text":prompt},
                            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64_image}"}}
                        ]}
                    ]
                )
                full_text = comp.choices[0].message.content
                placeholder.markdown(full_text)

            # NORMAL CHAT
            else:
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":SYS}] + st.session_state.messages,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_text += chunk.choices[0].delta.content
                        placeholder.markdown(full_text + "▌")
                placeholder.markdown(full_text)

        except Exception as e:
            full_text = f"SI error: {e}"
            placeholder.markdown(full_text)

        # Save
        msg = {"role":"assistant","content":full_text}
        if image_url:
            msg["image_url"] = image_url
        st.session_state.messages.append(msg)

        st.link_button("📤 Share on WhatsApp", f"https://wa.me/?text={urllib.parse.quote(full_text[:800])}")

        # Voice
        if voice_on and full_text:
            try:
                tts = gTTS(text=full_text[:300], lang='en', tld='com')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp.getvalue(), format='audio/mp3')
            except:
                pass
