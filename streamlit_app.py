import streamlit as st
from groq import Groq
import base64
import urllib.parse
from duckduckgo_search import DDGS
import datetime
from gtts import gTTS
import io

st.set_page_config(page_title="Bible Bot Ghana Level 10", page_icon="📖", layout="centered")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

st.title("📖 Bible Bot Ghana 🇬🇭 Level 10")
st.caption("Voice 🔊 | WhatsApp 💬 | Memory 🧠 | Pictures 🖼️")

# --- LONG MEMORY (names forever) ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Maakye! Level 10 active! I fit speak Twi, share to WhatsApp, and remember your name forever! What's your name?"}
    ]

# Sidebar
with st.sidebar:
    st.markdown("### 🧠 Memory")
    name_input = st.text_input("Your name:", value=st.session_state.user_name)
    if name_input:
        st.session_state.user_name = name_input
        st.success(f"Remembered: {name_input} ✅")

    st.divider()
    st.markdown("### 📤 Upload to READ")
    uploaded = st.file_uploader("Upload photo", type=["jpg","png","jpeg"])
    uploaded_base64 = None
    if uploaded:
        st.image(uploaded)
        uploaded_base64 = base64.b64encode(uploaded.getvalue()).decode('utf-8')

    st.divider()
    voice_on = st.checkbox("🔊 Voice On (Twi/English)", value=True)
    if st.button("Clear Chat 🗑️"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# Show chats + WhatsApp + Voice buttons
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "image_url" in m:
            st.image(m["image_url"])

        if m["role"] == "assistant":
            col1, col2 = st.columns(2)
            # WhatsApp Share
            with col1:
                share_text = urllib.parse.quote(m["content"][:1000])
                wa_link = f"https://wa.me/?text={share_text}%0A%0AFrom Bible Bot Ghana 🇬🇭 {st.secrets.get('app_url','bible-bot-gh.streamlit.app')}"
                st.link_button("📤 Share WhatsApp", wa_link)
            # Voice
            with col2:
                if voice_on and m["content"]:
                    try:
                        tts = gTTS(text=m["content"][:300], lang='en', slow=False)
                        audio_fp = io.BytesIO()
                        tts.write_to_fp(audio_fp)
                        st.audio(audio_fp.getvalue(), format='audio/mp3')
                    except:
                        pass

SYSTEM_PROMPT = f"""You are Bible Bot Ghana Level 10, warm Ghanaian friend.
User name: {st.session_state.user_name if st.session_state.user_name else 'Friend'}
Speak like Ghanaian, mix Twi if user likes Twi.
Keep short, mobile friendly.
Date: {datetime.datetime.now().strftime('%A %d %B %Y')}
"""

if prompt := st.chat_input("Ask, search, or ask about photo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        image_url = None

        try:
            if "picture" in prompt.lower() or "image" in prompt.lower() or "draw" in prompt.lower():
                clean = prompt.lower().replace("picture of","").replace("image of","").replace("picture","").strip()
                query = urllib.parse.quote(clean)
                image_url = f"https://image.pollinations.ai/prompt/{query}?width=800&height=800&nologo=true&seed={datetime.datetime.now().second}"
                full = f"{st.session_state.user_name}, here's **{clean}**:"
                placeholder.markdown(full)
                st.image(image_url)
                full += "\n\nPsalm 19:1 - The heavens declare God's glory! 🙏"
            elif prompt.lower().startswith("search:"):
                search_q = prompt.replace("search:","").strip()
                placeholder.markdown(f"Searching: {search_q}... 🔍")
                results = DDGS().text(search_q, max_results=3)
                context = "\n".join([r['body'] for r in results])
                comp = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content": SYSTEM_PROMPT + f"\nWeb: {context}"},{"role":"user","content":prompt}]
                )
                full = comp.choices[0].message.content
                placeholder.markdown(full)
            elif uploaded_base64:
                placeholder.markdown("Reading photo... 👁️")
                comp = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role":"system","content": SYSTEM_PROMPT},
                        {"role":"user","content": [
                            {"type":"text","text": prompt},
                            {"type":"image_url","image_url":{"url": f"data:image/jpeg;base64,{uploaded_base64}"}}
                        ]}
                    ]
                )
                full = comp.choices[0].message.content
                placeholder.markdown(full)
            else:
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":SYSTEM_PROMPT}, *st.session_state.messages],
                    temperature=0.7, max_tokens=700, stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        placeholder.markdown(full + "▌")
                placeholder.markdown(full)
        except Exception as e:
            full = f"Error: {e}"
            placeholder.markdown(full)

        # Save + show buttons
        msg = {"role":"assistant","content":full}
        if image_url:
            msg["image_url"] = image_url
        st.session_state.messages.append(msg)

        col1, col2 = st.columns(2)
        with col1:
            share_text = urllib.parse.quote(full[:1000])
            wa_link = f"https://wa.me/?text={share_text}"
            st.link_button("📤 Share to WhatsApp Status", wa_link)
        with col2:
            if voice_on:
                try:
                    tts = gTTS(text=full[:300], lang='en')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp.getvalue(), format='audio/mp3')
                    st.caption("🔊 Voice: English (Twi accent coming!)")
                except:
                    pass
