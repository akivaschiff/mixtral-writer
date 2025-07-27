import streamlit as st
import requests
import os

# --- Secure API Key Loader (works locally and on Streamlit Cloud) ---
def get_api_key():
    try:
        return st.secrets["DEEPINFRA_API_KEY"]
    except Exception:
        return os.getenv("DEEPINFRA_API_KEY")

API_KEY = get_api_key()

if not API_KEY:
    st.error("API key not found. Please set DEEPINFRA_API_KEY as an environment variable or Streamlit secret.")
    st.stop()

# --- App Config ---
st.set_page_config(page_title="Mixtral Story Generator", layout="centered")
st.title("🔥 Mixtral Story Chat")

# --- Initialize Session Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a talented fiction writer"
            )
        }
    ]

# --- Display Conversation So Far ---
for msg in st.session_state.messages[1:]:
    st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

# --- Input ---
user_input = st.text_area("You:", height=100, placeholder="Start or continue the scene...")

if st.button("Submit"):
    if user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Mixtral is writing..."):
            payload = {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": st.session_state.messages,
                "temperature": 0.9,
                "max_tokens": 1024
            }
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post("https://api.deepinfra.com/v1/openai/chat/completions", json=payload, headers=headers)
            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            else:
                st.error(f"API Error {response.status_code}")
                st.text(response.text)

# --- Reset Button ---
if st.button("🗑️ New Story"):
    st.session_state.messages = [st.session_state.messages[0]]
    st.rerun()
