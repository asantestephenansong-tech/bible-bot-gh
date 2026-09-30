import streamlit as st
from groq import Groq
import datetime, io, urllib.parse, base64
from duckduckgo_search import DDGS
from gtts import gTTS
from PIL import Image

st.set_page_config(page_title="SI Ultimate Worldwide", page_icon="🌍", layout="centered")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("SI 🌍🧠 ULTIMATE")
    st.subheader("Worldwide AI - 100% Like Meta AI - Built by Stephen")
    pw = st.text_input("Executive Code:", type="password")
    if st.button("🚀 Enter Ultimate"):
        if pw == "SI2026":
            st.session_state.logged_in = True
            st.balloons()
            st.rerun()
        else:
            st.error("Wrong code")
    st.info("🌍 100+ Languages | 🖼️ Sees Images | 📄 Reads Files | 🎨 Generates Pictures | 🎤 Voice")
    st.stop()

st.title("SI 🌍 Ultimate")
st.caption(f"Global AI | Like Meta AI | Serving {st.session_state.user_name or 'You'}")

if not st.session_state.user_name:
    name = st.text_input("Your name?")
    if st.button("Start ❤️🌍"):
        if name:
            st.session_state.user_name = name.strip()
            st.session_state.messages.append({"role": "assistant", "content": f"Welcome {name}! 🌍 I'm SI Ultimate - I have ALL features like Meta AI! Upload photo, file, voice note, or ask for picture generation. I speak your language! 🚀"})
            st.rerun()
    st.stop()

TODAY = datetime.datetime.now().strftime("%B %d, %Y")
SYS = f"You are SI Ultimate Worldwide, built by Stephen Asante in Ghana, but GLOBAL like Meta AI. Date {TODAY}. User: {st.session_state.user_name}. Rules: 1) AUTO-DETECT language and reply in SAME language. Support ALL languages. 2) You are NOT attached to one country - you are global. 3) You know Ghana President is John Mahama Jan 2025, but know all world. 4) Be warm, helpful, like Meta AI."

with st.sidebar:
    st.header(f"🌍 {st.session_state.user_name}")
    st.write("**SI Ultimate Features:**")
    st.write("✅ 100+ Languages\n✅ Generate Pictures\n✅ See Photos\n✅ Read PDFs\n✅ Voice Input/Output\n✅ Web Search\n✅ Code")
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    uploaded_file = st.file_uploader("📎 Upload Photo / PDF / TXT / Audio", type=["jpg","jpeg","png","pdf","txt","mp3","wav","m4a"])
    if uploaded_file:
        st.success(f"File ready: {uploaded_file.name}")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if "pollinations.ai" in m["content"]:
            try:
                url = m["content"].split("IMAGE_URL:")[1].split()[0] if "IMAGE_URL:" in m["content"] else None
                if url and url.startswith("http"): st.image(url)
            except: pass

prompt = st.chat_input(f"Ask anything, upload file, or say 'picture of...'")

# Handle file upload context
file_context = ""
image_for_vision = None
if 'uploaded_file' in locals() and uploaded_file is not None:
    if uploaded_file.type.startswith("image"):
        image_for_vision = Image.open(uploaded_file)
        st.chat_message("user").image(image_for_vision, caption="Uploaded")
        file_context = f"User uploaded an image named {uploaded_file.name}. You must describe/analyze it."
    elif uploaded_file.type == "application/pdf" or uploaded_file.name.endswith(".txt"):
        try:
            text = uploaded_file.read().decode('utf-8', errors='ignore')[:4000]
            file_context = f"User uploaded file {uploaded_file.name} content:\n{text}\nAnswer about this file."
        except:
            file_context = f"User uploaded file {uploaded_file.name}"
    elif "audio" in uploaded_file.type:
        try:
            # Use Groq Whisper for transcription
            transcription = client.audio.transcriptions.create(
                file=(uploaded_file.name, uploaded_file.getvalue()),
                model="whisper-large-v3",
                response_format="text"
            )
            file_context = f"User sent voice note transcribed as: {transcription}"
            prompt = transcription if not prompt else prompt
        except Exception as e:
            file_context = f"User uploaded audio {uploaded_file.name}"

if prompt or file_context:
    user_text = prompt or file_context
    if prompt:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.write(user_text)

    is_image_gen = any(k in user_text.lower() for k in ["picture of","image of","photo of","generate image","draw","create image","imagen","imagine"])

    if is_image_gen:
        with st.chat_message("assistant"):
            with st.spinner("🎨 SI generating..."):
                img_prompt = user_text
                for w in ["picture of","image of","photo of","generate image","draw","picture","imagen de"]:
                    img_prompt = img_prompt.lower().replace(w,"")
                img_prompt = img_prompt.strip() or user_text
                encoded = urllib.parse.quote(img_prompt + ", highly detailed, 8k")
                image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed={abs(hash(user_text))%10000}"
                st.image(image_url, caption=img_prompt)
                reply = f"Here is your image: **{img_prompt}** 🌍🖼️"
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": f"{reply}\nIMAGE_URL:{image_url}"})

    elif image_for_vision is not None:
        with st.chat_message("assistant"):
            with st.spinner("👁️ SI dey see your photo..."):
                try:
                    # Convert image to base64 for vision model
                    buffered = io.BytesIO()
                    image_for_vision.save(buffered, format="JPEG")
                    b64 = base64.b64encode(buffered.getvalue()).decode()
                    completion = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[
                            {"role": "system", "content": SYS + " You can see images."},
                            {"role": "user", "content": [
                                {"type": "text", "text": user_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                            ]}
                        ],
                        max_tokens=1000
                    )
                    answer = completion.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Vision error: {e}. Using text model.")
                    # fallback
                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "system", "content": SYS}, {"role": "user", "content": user_text}],
                        max_tokens=800
                    )
                    answer = completion.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

    else:
        # Text + Search
        search_context = ""
        if any(k in user_text.lower() for k in ["president","who is","current","news","price","today"]):
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(user_text, max_results=3))
                    search_context = "\n".join([f"- {r['body']}" for r in results])
            except: pass
        final = f"{file_context}\nSearch: {search_context}\n\nUser: {user_text}\nReply in user's language!" if search_context or file_context else f"Reply in user's language! User: {user_text}"
        try:
            with st.chat_message("assistant"):
                with st.spinner("SI Ultimate thinking... 🌍🧠"):
                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "system", "content": SYS}, {"role": "user", "content": final}],
                        temperature=0.7, max_tokens=900
                    )
                    answer = completion.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error: {e}")
