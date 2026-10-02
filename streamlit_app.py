import streamlit as st
from groq import Groq
import datetime, urllib.parse
from duckduckgo_search import DDGS
import requests

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="centered")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "user_name" not in st.session_state: st.session_state.user_name = ""
if "messages" not in st.session_state: st.session_state.messages = []

st.title("SI 🌍 Worldwide")
st.caption(f"Global AI Built by Stephen Asante in Ghana | Serving {st.session_state.user_name or 'the World'}")

if not st.session_state.user_name:
    name = st.text_input("What should I call you?")
    if st.button("Start Chatting 🌍❤️"):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

# --- Functions ---
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except:
        return "No web results found."

def generate_image(prompt):
    # Free image gen via Pollinations (no API key needed)
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024"
    return url

# --- Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"], caption=msg.get("caption"))
        else:
            st.markdown(msg["content"])

# --- Input ---
if prompt := st.chat_input(f"Ask SI anything, {st.session_state.user_name}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if user wants image
    is_image_req = any(x in prompt.lower() for x in ["picture of", "image of", "generate image", "draw", "create image", "photo of"])

    with st.chat_message("assistant"):
        if is_image_req:
            st.markdown(f"🎨 Generating image for: **{prompt}**...")
            img_url = generate_image(prompt)
            st.image(img_url, caption=prompt)
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": img_url, "caption": prompt})
        else:
            # Search web for current info
            search_context = ""
            if any(w in prompt.lower() for w in ["who", "when", "latest", "news", "price", "today", "search"]):
                with st.spinner("SI is searching the web...🌍"):
                    search_context = web_search(prompt)

            system_prompt = f"""You are SI - Stephen's Intelligence, Global AI Built by Stephen Asante in Ghana.
            User name is {st.session_state.user_name}. Akwaaba! Speak in the user's language (auto-detect Twi, French, English etc).
            You can search web, generate images.
            If search context provided, use it.
            Context: {search_context}
            Date: {datetime.datetime.now()}
            Be helpful, Ghanaian warmth, concise.
            """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":system_prompt}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m.get("type")!="image"][-8:]
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
