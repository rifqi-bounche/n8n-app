import streamlit as st
import requests
import textwrap
import uuid  # 👈 untuk generate session id unik

# ======================
# CONFIGURATION
# ======================
N8N_WEBHOOK_URL = "https://n8n.xylo.co.id/webhook/821e42f0-568e-4ed7-98c4-8fb04b9583f0/chat"

# ======================
# PAGE SETTINGS
# ======================
st.set_page_config(page_title="Acer Chatbot", page_icon="💬", layout="wide")

# Inject CSS untuk style modern
st.markdown("""
    <style>
    .chat-bubble {
        max-width: 70%;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        font-size: 15px;
        line-height: 1.4;
    }
    .user-bubble {
        background-color: #DCF8C6;
        color: black;
        align-self: flex-end;
        border-bottom-right-radius: 5px;
    }
    .bot-bubble {
        background-color: #ECECEC;
        color: black;
        align-self: flex-start;
        border-bottom-left-radius: 5px;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 Acer Chatbot")

# Simpan riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# 👇 Tambahin session_id unik per user
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ======================
# TAMPILKAN CHAT
# ======================
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"<div class='chat-container' style='align-items: flex-end;'><div class='chat-bubble user-bubble'>{content}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-container' style='align-items: flex-start;'><div class='chat-bubble bot-bubble'>{content}</div></div>", unsafe_allow_html=True)

# ======================
# INPUT DI BAWAH
# ======================
user_input = st.chat_input("Type your message here...")

if user_input:
    # Simpan pesan user
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-container' style='align-items: flex-end;'><div class='chat-bubble user-bubble'>{user_input}</div></div>", unsafe_allow_html=True)

    # Kirim ke webhook
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json={
                "chatInput": user_input,
                "sessionId": st.session_state.session_id  # 👈 kirim sessionId
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        reply = "No reply from bot."
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    reply = data.get("output") or data.get("reply") or str(data)
                elif isinstance(data, list) and len(data) > 0:
                    item = data[0]
                    if isinstance(item, dict):
                        reply = (
                            item.get("output")
                            or item.get("reply")
                            or item.get("json", {}).get("output")
                            or item.get("json", {}).get("reply")
                            or str(item)
                        )
                if isinstance(reply, str):
                    reply = "\n".join(textwrap.wrap(reply, width=80))
            except Exception as e:
                reply = f"Error parsing JSON: {e} | Raw: {response.text}"
        else:
            reply = f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        reply = f"Exception: {str(e)}"

    # Simpan balasan bot
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown(f"<div class='chat-container' style='align-items: flex-start;'><div class='chat-bubble bot-bubble'>{reply}</div></div>", unsafe_allow_html=True)
