import streamlit as st

def check_login():
    # --- Proteção: Verifica se o usuário está logado ---
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("🔒 Você precisa estar logado para acessar esta página.")
        st.info("Por favor, volte para a [página de login](/)")
        st.stop()