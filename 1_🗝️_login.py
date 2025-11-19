#-- Bibliotecas --#
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import hashlib
# Importa as funções de conexão
from utils.db_connector import get_gspread_client, load_data, SHEET_NAME 
from utils.data_processing import process_data

# -------------------------------
# ⚙️ Configuração da página
# -------------------------------
st.set_page_config(page_title="Login | Gastos Residenciais", 
                   page_icon="🔐.", 
                   layout="centered")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

# -------------------------------
# 🎨 Estilo CSS personalizado
# -------------------------------
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 🔐 Função para verificar senha (Pode ser movida para 'utils/auth.py' para ser mais limpo)
# -------------------------------
def check_password(input_password, stored_password):
    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    return input_hash == stored_password

# -------------------------------
# 🗂️ Carregar Credenciais de Usuário
# -------------------------------
try:
    USERS = st.secrets["AUTH_USERS"]
except KeyError:
    st.error("Credenciais de usuário ausentes em secrets.toml.")
    st.stop()


# -------------------------------
# 🔗 Status de Conexão (Feedback Visual)
# -------------------------------
sheet_client, connected = get_gspread_client()
if connected:
    st.success("✅ Conectado ao Google Sheets.")
else:
    st.error("❌ Não foi possível conectar ao Google Sheets.")

# -------------------------------
# 🎨 Formulário de Login (Mantém igual)
# -------------------------------
with st.form("login_form"):
    st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)
    st.divider()

    username = st.text_input("👤 Usuário").strip()
    password = st.text_input("🔒 Senha", type="password").strip()

    submit = st.form_submit_button("Entrar")

# -------------------------------
# 🚀 Processamento do Login
# -------------------------------
if submit and connected: # Apenas processa se estiver conectado
    if username in USERS and check_password(password, USERS[username]):
        
        # Chama a função modularizada
        df_bruto = load_data(SHEET_NAME, sheet_client) 

        if not df_bruto.empty:
            df_dados = process_data(df_bruto)
            st.session_state['logged_in'] = True
            st.session_state['df_Bi_Gastos_Resid'] = df_dados
            
            st.success("✅ Login bem-sucedido! Redirecionando...")
            # Use switch_page para ir para o painel
            #switch_page("painel") 
        else:
            st.warning("⚠️ A planilha está vazia.")
    else:
        st.error("❌ Usuário ou senha inválidos.")
elif submit and not connected:
    st.error("❌ Erro de conexão impede o login.")