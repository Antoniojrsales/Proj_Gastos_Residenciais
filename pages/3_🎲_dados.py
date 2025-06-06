import streamlit as st

if 'df_Bi_Gastos_Resid' not in st.session_state:
    st.session_state['df_Bi_Gastos_Resid'] = carregar_dados()

df_original = st.session_state['df_Bi_Gastos_Resid']

with st.sidebar.expander("🔍 Visualizar colunas"):
    options = st.multiselect('Escolha a Coluna:', df_original.columns)

if options:
    df_filtrado = df_original[options]
    st.write('Dataframe Filtrado:', df_filtrado.tail())
else:
    st.write('Por favor, selecione ao menos uma coluna.')
