from streamlit_extras.switch_page_button import switch_page
import pandas as pd
import streamlit as st
import gspread

st.set_page_config(page_title="Login (Gastos Residencias)", page_icon="🔐", layout="centered")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

with st.form('sign_in'):
    st.markdown("<h1 style='text-align: center;'>Sign In</h1>", unsafe_allow_html=True)
    st.caption('Please enter your username and password.')
    st.divider()
    username = st.text_input('Username').strip()
    password = st.text_input('Password', type='password').strip()
    
    submit_btn = st.form_submit_button(label="Submit", type="primary", use_container_width=True)
    google_btn = st.form_submit_button(label="Continue with Google", type="secondary", use_container_width=True, icon=':material/mail:')

    col1, col2, col3, col4 = st.columns(4)
    with col3:
        remember_box = st.checkbox("Remember me")
    with col4:
        st.markdown('<p style="margin-top:8px; color:#FFAC41"><a href="https://www.google.com.br/?hl=pt-BR">Forgot password?</a></p>', unsafe_allow_html=True)

# Acesse os usuários diretamente de st.secrets
# st.secrets carrega o conteúdo de .streamlit/secrets.toml
try:
    USERS = st.secrets["AUTH_USERS"]
except KeyError:
    st.error("Erro: A seção [AUTH_USERS] não foi encontrada em .streamlit/secrets.toml.")
    st.stop() # Interrompe a execução se os segredos não forem carregados

try:
    gspread_credentials = st.secrets["GSPREAD"]
    gc = gspread.service_account_from_dict(gspread_credentials)
    sheet_id = st.secrets["SHEET"]["SHEET_ID"]  # 👉 Somente o ID da planilha
    sheet_name = st.secrets["SHEET"]["SHEET_NAME"]
    sheet = gc.open_by_key(sheet_id)
    st.success("✅ Conectado ao Google Sheets com sucesso.")
except Exception as e:
    st.error(f"❌ Erro ao conectar com o Google Sheets: {e}")
    st.stop()

@st.cache_data(ttl=600)  # Cache de 10 minutos
def load_worksheet_data(worksheet_name):
    try:
        worksheet = sheet.worksheet(worksheet_name)
        data = worksheet.get_all_values()
        colunas = data.pop(0)  # Remove o cabeçalho
        df = pd.DataFrame(data, columns=colunas)
        st.success(f"✅ Aba '{worksheet_name}' carregada com sucesso.")
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados da aba {worksheet_name}: {e}")
        return pd.DataFrame()

if submit_btn:
    if username in USERS and password == USERS[username]:
        try:
            df_dados = load_worksheet_data(sheet_name)
            
            st.session_state['logged_in'] = True
            st.session_state['df_Bi_Gastos_Resid'] = df_dados

            st.success("Login bem-sucedido!")
            switch_page("2_🏠_painel")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
    else:
        st.error("Usuário ou senha incorretos.")
