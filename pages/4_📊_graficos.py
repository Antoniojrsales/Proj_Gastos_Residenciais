import streamlit as st

st.set_page_config(
    page_title="Gastos Residenciais",
    page_icon="💰",
    layout="wide"
)

# --- Proteção: Verifica se o usuário está logado ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Você precisa estar logado para acessar esta página.")
    st.info("Por favor, volte para a [página de login](/)")
    st.stop()

# Acessa o DataFrame salvo na sessão
if 'df_Bi_Gastos_Resid' in st.session_state:
    df_dados = st.session_state['df_Bi_Gastos_Resid']
else:
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")