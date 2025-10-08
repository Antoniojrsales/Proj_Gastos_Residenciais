#-- 📚 Bibliotecas --#
import streamlit as st
import pandas as pd
import gspread

#-- 🗂️Acessa as credenciais do secrets.toml --#
try:
    GSPREAD_CREDENTIALS = st.secrets["GSPREAD"]
    SHEET_ID = st.secrets["SHEET"]["SHEET_ID"]
    SHEET_NAME = st.secrets["SHEET"]["SHEET_NAME"]
except Exception as e:
    # Apenas loga o erro, não para a aplicação imediatamente
    # st.error(f"Erro ao carregar secrets de GSPREAD: {e}")
    GSPREAD_CREDENTIALS = None
    SHEET_ID = None
    SHEET_NAME = None

@st.cache_resource
def get_gspread_client():
    """Conecta ao Google Sheets API e retorna o cliente."""
    if GSPREAD_CREDENTIALS:
        try:
            # Usar st.cache_resource garante que a conexão só seja estabelecida uma vez
            gc = gspread.service_account_from_dict(GSPREAD_CREDENTIALS)
            return gc.open_by_key(SHEET_ID), True
        except Exception as e:
            st.error(f"❌ Erro ao conectar com o Google Sheets: {e}")
            return None, False
    return None, False

@st.cache_data(ttl=600)
def load_data(sheet_name, _sheet_client):
    """Carrega dados da planilha para um DataFrame do Pandas."""
    if not _sheet_client:
        return pd.DataFrame()
    try:
        ws = _sheet_client.worksheet(sheet_name)
        data = ws.get_all_values()
        if not data:
            return pd.DataFrame()
        
        cols = data.pop(0)
        df = pd.DataFrame(data, columns=cols)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba '{sheet_name}': {e}")
        return pd.DataFrame()
    
def append_row(new_row: list, _sheet_client): # Não esqueça do _ underscore no cliente!
    """
    Insere uma nova linha na aba principal da planilha.
    """
    if not _sheet_client:
        return False

    try:
        ws = _sheet_client.worksheet(st.secrets["SHEET"]["SHEET_NAME"])
        
        # Insere a nova linha no final
        ws.append_row(new_row, value_input_option='USER_ENTERED')
        
        # CRUCIAL: Limpa o cache para que load_data() traga o novo dado
        st.cache_data.clear() 

        return True

    except Exception as e:
        # st.error(f"❌ Erro ao adicionar dados na planilha: {e}") # (Opcional: use st.error aqui ou no front-end)
        return False