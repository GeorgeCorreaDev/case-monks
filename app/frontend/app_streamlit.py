import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

# carrega envs se estiver rodando local sem docker
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY_INTERNAL", "monks-secret-key-2026")

st.set_page_config(
    page_title="monks media analyst | ai agent",
    page_icon="☕",
    layout="wide"
)

# style customizado 
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 15px;
    }
    .usage-metric {
        font-size: 0.8rem;
        color: #888;
    }
    </style>
""", unsafe_allow_html=True)

st.title("☕ monks media analyst jr.")
st.caption("seu agente júnior (estagiario) especializado em bigquery (movido a café ☕ e planilhas)")

# gerenciamento de Memo thread Id
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# sidebar .. info e config
with st.sidebar:
    st.header("⚙️ configurações")
    st.info(f"sessao id: `{st.session_state.thread_id[:8]}...`")
    
    if st.button("nova conversa (reset)"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### 📊 status do agente")
    st.success("conectado ao backend")
    st.write("Provider: `OpenAI` (Default)")

# historico Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "usage" in message and message["role"] == "assistant":
            u = message["usage"]
            st.markdown(f"<p class='usage-metric'>Tokens: {u.get('total_tokens', 0)} | Custo: ${u.get('total_cost', 0):.4f}</p>", unsafe_allow_html=True)

# input chat
if prompt := st.chat_input("Pergunte algo sobre os dados de mídia..."):
    # adiciona perg do user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # chama o back
    with st.chat_message("assistant"):
        with st.spinner("Tomando o 5º café e cruzando as planilhas antes que o diretor peça o report..."):
            try:
                headers = {"X-API-KEY": API_KEY}
                payload = {
                    "question": prompt,
                    "thread_id": st.session_state.thread_id
                }
                
                response = requests.post(f"{API_URL}/ask", json=payload, headers=headers, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    usage = data.get("usage", {})
                    
                    st.markdown(answer)
                    st.markdown(f"<p class='usage-metric'>Tokens: {usage.get('total_tokens', 0)} | Custo: ${usage.get('total_cost', 0):.4f}</p>", unsafe_allow_html=True)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "usage": usage
                    })
                elif response.status_code == 403:
                    st.error("Erro de Autenticação: X-API-KEY inválida.")
                else:
                    st.error(f"Erro no Backend ({response.status_code}): {response.text}")
            
            except Exception as e:
                st.error(f"Falha na conexão com o servidor: {str(e)}")
