import streamlit as st
from groq import Groq
import urllib.parse
import datetime

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="centered")

# --- API KEY ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Please add GROQ_API_KEY in Streamlit Secrets")
    st.stop()

# --- MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI ---
st.title("SI 🌍 Worldwide")
st.caption("Built by Stephen Asante in Ghana — Akwaaba!")

# Show old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"], caption=msg.get("caption",""))
        else:
            st.markdown(msg["content"])

# --- INPUT ---
prompt = st.chat_input("Ask SI anything...")

if prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant reply
    with st.chat_message("assistant"):
        low = prompt.lower()

        # SMART IMAGE CHECK - only if user WANTS to draw
        draw_keywords = ["draw a", "draw an", "draw the", "create a picture", "create an image", "generate a picture", "generate an image", "picture of", "photo of", "image of"]
        wants_image = any(k in low for k in draw_keywords)

        if wants_image:
            with st.spinner("SI is drawing..."):
                img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&seed={datetime.datetime.now().microsecond}"
                st.image(img_url, caption=prompt)
                st.session_state.messages.append({"role": "assistant", "type": "image", "content": img_url, "caption": prompt})
        else:
            with st.spinner("SI is thinking..."):
                try:
                    system_prompt = f"You are SI, a helpful AI built by Stephen Asante in Ghana. Today is {datetime.datetime.now().strftime('%Y-%m-%d')}. Answer clearly in the user's language. Be friendly."

                    # Get last 8 messages for context
                    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m.get("type")!= "image"][-8:]

                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "system", "content": system_prompt}] + history,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("Tip: Check your GROQ_API_KEY. Get new one at console.groq.com")
