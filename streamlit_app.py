import streamlit as st
from groq import Groq
import datetime
import urllib.parse

st.set_page_config(page_title="Bible Bot Ghana 🇬🇭", page_icon="📖", layout="centered")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

st.title("📖 Bible Bot Ghana 🇬🇭")
st.caption("Twi | Pidgin | English — Now with Images! 🖼️")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Maakye! I can now show pictures! Try: *picture of Orion* or upload your own photo below! 🙏"}
    ]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "image_url" in m:
            st.image(m["image_url"])

# --- Upload photo section ---
with st.sidebar:
    st.markdown("### 📤 Upload Photo")
    uploaded = st.file_uploader("Upload your picture", type=["jpg","png","jpeg"])
    if uploaded:
        st.image(uploaded, caption="Your upload")
        st.success("Photo uploaded! Now ask bot about it")
    if st.button("Clear Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()

SYSTEM_PROMPT = """You are Bible Bot Ghana... friendly Ghanaian Bible companion.
If user asks for picture/image/photo, say you will show it.
Keep answers short for mobile.
Today is """ + datetime.datetime.now().strftime("%A %d %B %Y")

if prompt := st.chat_input("Ask Bible question or ask for picture..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full = ""
        placeholder = st.empty()
        image_url = None

        # If user wants picture, generate via free Pollinations API
        if "picture" in prompt.lower() or "image" in prompt.lower() or "photo" in prompt.lower():
            # Create image URL
            query = urllib.parse.quote(prompt.replace("picture of","").strip())
            image_url = f"https://image.pollinations.ai/prompt/{query}?width=800&height=600&nologo=true"
            full = f"Here's a picture of **{prompt}**:\n\n"
            placeholder.markdown(full)
            st.image(image_url)
            full += f"\n\nIn the Bible, the heavens declare God's glory! Psalm 19:1 🙏"
        else:
            # Normal text chat
            try:
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":SYSTEM_PROMPT}, *st.session_state.messages],
                    temperature=0.7, max_tokens=600, stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full += chunk.choices[0].delta.content
                        placeholder.markdown(full + "▌")
                placeholder.markdown(full)
            except Exception as e:
                full = f"Small error: {e}"
                placeholder.markdown(full)

    msg = {"role":"assistant","content":full}
    if image_url:
        msg["image_url"] = image_url
    st.session_state.messages.append(msg)
