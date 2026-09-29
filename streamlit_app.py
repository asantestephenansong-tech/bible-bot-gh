import streamlit as st
from groq import Groq
import base64
import urllib.parse
from duckduckgo_search import DDGS
import datetime
from gtts import gTTS
import io

st.set_page_config(page_title="Bible Bot Ghana Final", page_icon="📖", layout="centered")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("Add GROQ_API_KEY in Streamlit Secrets")
    st.stop()

st.title("📖 Bible Bot Ghana 🇬🇭 FINAL")
st.caption("Pictures 🖼️ | Reads Photos 👁️ | Search 🔍 | Voice 🔊 | WhatsApp 💬")

if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Maakye Stephen! Final Level active! Wo ho te sɛn? I can now do EVERYTHING — picture, read, search, voice, WhatsApp. What's your name?"}
    ]

with st.sidebar:
    st.markdown("### 🧠 Memory")
    name_input = st.text_input("Your name:", value=st.session_state.user_name)
    if name_input:
        st.session_state.user_name = name_input
        st.success(f"Remembered: {name_input} ✅")

    st.divider()
    st.markdown("### 📤 Upload to READ")
    uploaded = st.file_uploader("Upload Bible page / photo", type=["jpg","png","jpeg"])
    uploaded_base64 = None
    if uploaded:
        st.image(uploaded)
        uploaded_base64 = base64.b64encode(uploaded.getvalue()).decode('utf-8')
        st.info("Now ask: what does this say?")

    st.divider()
    voice_on = st.checkbox("🔊 Voice On", value=True)
    if st.button("Clear Chat 🗑️"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# Display chats
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "image_url" in m:
            st.image(m["image_url"])
        if m["role"] == "assistant":
            share_text = urllib.parse.quote(m["content"][:800])
            st.link_button("📤 Share to WhatsApp", f"https://wa.me/?text={share_text}")

SYSTEM_PROMPT = f"You are Bible Bot Ghana Final. User: {st.session_state.user_name or 'Friend'}. Speak Twi if asked, warm Ghanaian style. Short answers. Date: {datetime.datetime.now().strftime('%A %d %B %Y')}"

if prompt := st.chat_input("Ask, picture, search:, or about photo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        image_url = None

        try:
            # PICTURE
            if any(k in prompt.lower() for k in ["picture","image","draw","show me"]):
                clean = prompt.lower().replace("picture of","").replace("picture","").replace("image of","").replace("draw","").strip()
                if not clean:
                    clean = "Jesus blessing children Ghana"
                query = urllib.parse.quote(clean)
                image_url = f"https://image.pollinations.ai/prompt/{query}?width=800&height=800&nologo=true"
                full = f"{st.session_state.user_name}, here's **{clean}**:"
                placeholder.markdown(full)
                st.image(image_url)
                full += "\n\nPsalm 19:1 - The heavens declare God's glory! 🙏"

            # SEARCH
            elif prompt.lower().startswith("search:"):
                search_q = prompt.replace("search:","").strip()
                placeholder.markdown(f"🔍 Searching: {search_q}...")
                results = DDGS().text(search_q, max_results=3)
                context = "\n".join([r['body'] for r in results])
                comp = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content": SYSTEM_PROMPT + f"\nWeb info: {context}"},{"role":"user","content":prompt}]
                )
                full = comp.choices[0].message.content
                placeholder.markdown(full)

            # READ PHOTO
            elif uploaded_base64:
                placeholder.markdown("👁️ Reading your photo...")
                comp = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role":"system","content": SYSTEM_PROMPT},
                        {"role":"user","content":[
                            {"type":"text","text":prompt},
                            {"type":"image_url","image_url":{"url": f"data:image/jpeg;base64,{uploaded_base64}"}}
                        ]}
                    ]
                )
                full = comp.choices[0].message.content
                placeholder.markdown(full)

            # NORMAL CHAT
            else:
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":SYSTEM_PROMPT}] + st.session_state.messages,
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

        # Save
        msg = {"role":"assistant","content":full}
        if image_url:
            msg["image_url"] = image_url
        st.session_state.messages.append(msg)

        # Buttons + Voice
        share_text = urllib.parse.quote(full[:800])
        st.link_button("📤 Share to WhatsApp", f"https://wa.me/?text={share_text}")

        if voice_on and full:
            try:
                tts = gTTS(text=full[:300], lang='en', tld='com.gh')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp.getvalue(), format='audio/mp3')
            except:
                pass
