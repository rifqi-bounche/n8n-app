import streamlit as st
import requests
import textwrap
import uuid
import re

# ======================
# CONFIGURATION
# ======================
N8N_WEBHOOK_URL = "https://n8n.xylo.co.id/webhook/3cafb6a1-f64b-4c4b-82d2-d99cef781298/chat"

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
    .bot-bubble ul {
        margin: 10px 0;
        padding-left: 20px;
    }
    .bot-bubble li {
        margin: 8px 0;
    }
    .bot-bubble h3 {
        color: #2E86AB;
        margin: 15px 0 8px 0;
    }
    .bot-bubble strong {
        color: #1F4E79;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 Acer Chatbot")

# ======================
# FUNCTION TO PROCESS MARKDOWN
# ======================
def process_markdown_to_html(text):
    """Convert markdown-like text to HTML for better display"""
    
    # Handle numbered lists (1. 2. 3.)
    text = re.sub(r'^(\d+)\.\s*\*\*(.*?)\*\*', r'<h3>\1. \2</h3>', text, flags=re.MULTILINE)
    
    # Handle bullet points with bold text
    text = re.sub(r'^\s*-\s*\*\*(.*?)\*\*:\s*(.*?)$', r'<li><strong>\1:</strong> \2</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*-\s*(.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    
    # Handle bold text
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Handle bullet points (convert to HTML list)
    lines = text.split('\n')
    processed_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check if line starts with bullet point
        if stripped.startswith('<li>'):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            processed_lines.append(f'  {stripped}')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            if stripped:  # Only add non-empty lines
                processed_lines.append(stripped)
    
    if in_list:
        processed_lines.append('</ul>')
    
    # Join lines and add line breaks
    result = '<br>'.join(processed_lines)
    
    # Clean up extra line breaks
    result = re.sub(r'(<br>\s*){3,}', '<br><br>', result)
    
    return result

# Simpan riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Session ID unik per user
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
        # Process markdown for bot response
        formatted_content = process_markdown_to_html(content)
        st.markdown(f"<div class='chat-container' style='align-items: flex-start;'><div class='chat-bubble bot-bubble'>{formatted_content}</div></div>", unsafe_allow_html=True)

# ======================
# INPUT DI BAWAH
# ======================
user_input = st.chat_input("Type your message here...")

if user_input:
    # Simpan pesan user
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message immediately
    st.markdown(f"<div class='chat-container' style='align-items: flex-end;'><div class='chat-bubble user-bubble'>{user_input}</div></div>", unsafe_allow_html=True)

    # Show loading indicator
    with st.spinner('Thinking...'):
        # Kirim ke webhook
        try:
            response = requests.post(
                N8N_WEBHOOK_URL,
                json={
                    "chatInput": user_input,
                    "sessionId": st.session_state.session_id
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
                    
                    # Don't wrap text here - let markdown processing handle it
                    if isinstance(reply, str):
                        # Clean up the reply - remove excessive whitespace
                        reply = re.sub(r'\n\s*\n\s*\n', '\n\n', reply)
                        
                except Exception as e:
                    reply = f"Error parsing JSON: {e} | Raw: {response.text}"
            else:
                reply = f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            reply = f"Exception: {str(e)}"

    # Simpan balasan bot
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    # Display bot response with markdown formatting
    formatted_reply = process_markdown_to_html(reply)
    st.markdown(f"<div class='chat-container' style='align-items: flex-start;'><div class='chat-bubble bot-bubble'>{formatted_reply}</div></div>", unsafe_allow_html=True)

# ======================
# SIDEBAR INFO
# ======================
with st.sidebar:
    st.header("💡 Info")
    st.write("Session ID:", st.session_state.session_id[:8] + "...")
    
    # Count only user messages (chat inputs)
    user_message_count = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
    st.write("Total chat inputs:", user_message_count)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()