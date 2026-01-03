# ---------------------------------------------------------
# 📚 BIBLIOTECAS E RECURSOS INTERNOS
# ---------------------------------------------------------
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import hashlib
from utils.db_connector import get_gspread_client, load_data, SHEET_NAME 
from utils.data_processing import process_data

# ---------------------------------------------------------
# ⚙️ CONFIGURAÇÕES INICIAIS DA INTERFACE (STREAMLIT)
# ---------------------------------------------------------
st.set_page_config(page_title="Login | Gastos Residenciais", 
                   page_icon="🔐.", 
                   layout="centered")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

# ---------------------------------------------------------
# 🎨 UTILITÁRIOS DE ESTILIZAÇÃO (CSS)
# ---------------------------------------------------------
#Lê um arquivo CSS externo e injeta no Streamlit para personalizar o visual.
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🔐 LÓGICA DE AUTENTICAÇÃO E SEGURANÇA
# ---------------------------------------------------------
# Criptografa a senha digitada em SHA256 e compara com o hash armazenado.
def check_password(input_password, stored_password):
    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    return input_hash == stored_password

# ---------------------------------------------------------
# 🗂️ Carregar Credenciais de Usuário
# ---------------------------------------------------------
# Tentativa de carregar os usuários autorizados via Secrets do Streamlit (Segurança)
try:
    USERS = st.secrets["AUTH_USERS"]
except KeyError:
    st.error("Credenciais de usuário ausentes em secrets.toml.")
    st.stop()

# ---------------------------------------------------------
# 🔗 CONEXÃO COM A BASE DE DADOS (GOOGLE SHEETS)
# ---------------------------------------------------------
# Inicializa o cliente e verifica se a conexão está ativa antes de prosseguir
sheet_client, connected = get_gspread_client()
if connected:
    st.success("✅ Conectado ao Google Sheets.")
else:
    st.error("❌ Não foi possível conectar ao Google Sheets.")

# ---------------------------------------------------------
# 🎨 RENDERIZAÇÃO DO FORMULÁRIO DE LOGIN
# ---------------------------------------------------------
# 1. Cria o contêiner do formulário para agrupar os campos
# 2. Exibe o título centralizado e uma linha divisória
# 3. Coleta o usuário e a senha (com máscara de proteção)
# 4. Define o botão de envio e carrega o estilo visual
with st.form("login_form"): #1
    st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)
    st.divider() #2

    username = st.text_input("👤 Usuário").strip() #3
    password = st.text_input("🔒 Senha", type="password").strip() #3

    submit = st.form_submit_button("Entrar") #4
    local_css('style_button_login.css') #4

# ---------------------------------------------------------
# 🚀 VALIDAÇÃO E PROCESSAMENTO DO LOGIN
# ---------------------------------------------------------
# 1. Verifica se o usuário existe e se a senha coincide
# 2. Se autenticado, carrega os dados brutos da planilha
# 3. Processa/Limpa os dados (Data Wrangling)
# 4. Salva o estado da sessão para manter o usuário logado e os dados em memória
if submit and connected:
    if username in USERS and check_password(password, USERS[username]): #1        
        
        df_bruto = load_data(SHEET_NAME, sheet_client) #2 
        
        if not df_bruto.empty: #3
            df_dados = process_data(df_bruto)
            
            st.session_state['logged_in'] = True #4
            st.session_state['df_Bi_Gastos_Resid'] = df_dados
            
            st.success("✅ Login bem-sucedido! Redirecionando...")
            #switch_page("painel") 
        else:
            st.warning("⚠️ A planilha está vazia.")
    else:
        st.error("❌ Usuário ou senha inválidos.")
elif submit and not connected:
    st.error("❌ Erro de conexão impede o login.")