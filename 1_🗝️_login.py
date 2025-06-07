from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

with st.form('sign_in'):
    st.markdown("<h1 style='text-align: center;'>Sign In</h1>", unsafe_allow_html=True)
    st.caption('Please enter your username and password.')
    st.divider()
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    
    submit_btn = st.form_submit_button(label="Submit", type="primary", use_container_width=True)
    google_btn = st.form_submit_button(label="Continue with Google", type="secondary", use_container_width=True, icon=':material/mail:')

    col1, col2, col3, col4 = st.columns(4)
    with col3:
        remember_box = st.checkbox("Remember me")
    with col4:
        st.markdown('<p style="margin-top:8px; color:#FFAC41"><a href="https://www.google.com.br/?hl=pt-BR">Forgot password?</a></p>', unsafe_allow_html=True)

create_acc_btn = st.button(label="Create an Account", type="secondary", use_container_width=True)

@st.cache_data(ttl=600)
#Criando a conexao com a planilha do google sheets
def load_data():
    try:
        load_dotenv()
        sheet_id = os.getenv('SHEET_ID')
        sheet_name = os.getenv('SHEET_NAME')
        if not sheet_id or not sheet_name:
            raise ValueError("Variáveis de ambiente não definidas.")
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()  # Retorna DataFrame vazio como fallback

#df_dados = load_data()

# Acesse os usuários diretamente de st.secrets
# st.secrets carrega o conteúdo de .streamlit/secrets.toml
try:
    USERS = st.secrets["AUTH_USERS"]
except KeyError:
    st.error("Erro: A seção [AUTH_USERS] não foi encontrada em .streamlit/secrets.toml.")
    st.stop() # Interrompe a execução se os segredos não forem carregados

# Aqui entra a lógica de login e redirecionamento
if submit_btn:
    if username in USERS and password == USERS[username]:
        df_dados = load_data()
         # Verifica se o DataFrame foi carregado antes de armazenar na sessão
        if not df_dados.empty:
            st.session_state['logged_in'] = True
            st.session_state['df_Bi_Gastos_Resid'] = df_dados

            st.success("Login bem-sucedido!")
            # st.write(df_dados) # Opcional: Removido para não mostrar dados na tela de login
            switch_page("2_🏠_painel")  # redireciona
        else:
            st.error("Erro ao carregar dados após o login. Tente novamente.")
    else:
        st.error("Usuário ou senha incorretos.")
