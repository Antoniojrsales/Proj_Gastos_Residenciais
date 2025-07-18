# 📚 Bibliotecas
import streamlit as st
import pandas as pd
import gspread
from streamlit_extras.switch_page_button import switch_page
import hashlib

# ⚙️ Configuração da página
st.set_page_config(page_title="Login | Gastos Residenciais", 
                   page_icon="🔐", 
                   layout="centered")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

# 🎨 Estilo CSS personalizado
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
# 🔐 Função para verificar senha
# -------------------------------
def check_password(input_password, stored_password):
    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    return input_hash == stored_password

# -------------------------------
# 🗂️ Carregar Credenciais
# -------------------------------
try:
    USERS = st.secrets["AUTH_USERS"]
    GSPREAD_CREDENTIALS = st.secrets["GSPREAD"]
    SHEET_ID = st.secrets["SHEET"]["SHEET_ID"]
    SHEET_NAME = st.secrets["SHEET"]["SHEET_NAME"]
except Exception as e:
    st.error(f"Erro nas configurações do secrets.toml: {e}")
    st.stop()

# -------------------------------
# 🔗 Conectar ao Google Sheets
# -------------------------------
try:
    gc = gspread.service_account_from_dict(GSPREAD_CREDENTIALS)
    sheet = gc.open_by_key(SHEET_ID)
    st.success("✅ Conectado ao Google Sheets.")
except Exception as e:
    st.error(f"❌ Erro ao conectar com o Google Sheets: {e}")
    st.stop()

# -------------------------------
# 📥 Função para carregar dados
# -------------------------------
@st.cache_data(ttl=600)
def load_data(sheet_name):
    try:
        ws = sheet.worksheet(sheet_name)
        data = ws.get_all_values()
        cols = data.pop(0)
        df = pd.DataFrame(data, columns=cols)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba '{sheet_name}': {e}")
        return pd.DataFrame()

# -------------------------------
# 🎨 Formulário de Login
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
if submit:
    if username in USERS and check_password(password, USERS[username]):
        df_dados = load_data(SHEET_NAME)

        if not df_dados.empty:
            st.session_state['logged_in'] = True
            st.session_state['df_Bi_Gastos_Resid'] = df_dados

            st.success("✅ Login bem-sucedido!")
            #switch_page("2_🏠_painel")
        else:
            st.warning("⚠️ A planilha está vazia ou não foi encontrada.")
    else:
        st.error("❌ Usuário ou senha inválidos.")
