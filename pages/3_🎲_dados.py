import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Visualização dos Dados | Gastos Residencias)",
    page_icon="🎲",
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

st.markdown("""
<div style="
    padding: 5px;
    text-align: center;">
    <h2 style=" font-size: 40px; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif">
                Gastos familia Sales_Ribeiro</h2>
    <div id="chart-container" style="margin-bottom: 30px; color:'blue'"></div>
</div>
""", unsafe_allow_html=True)

aba1, aba2 = st.tabs(['Dados Brutos', 'Inserindo Dados na base']) 

with aba1:
    with st.sidebar.expander("🔍 Visualizar colunas"):
        options = st.multiselect('Escolha a Coluna:', df_dados.columns, default=list(df_dados.columns))

    options_dados = st.sidebar.radio('Escolha qual o filtro de visualização:',
                            ['Todos', 'Head', 'Tail'])

    if options:
        df_filtrado = df_dados[options]
        if options_dados == 'Todos':
            st.write('Dataframe Filtrado Total:', df_filtrado)
        elif options_dados == 'Head':
            st.write('Dataframe Filtrado 10 primeiras linhas:', df_filtrado.head(10))
        else:
            st.write('Dataframe Filtrado 10 ultimas linhas:', df_filtrado.tail(10))
    else:
        st.write('Por favor, selecione ao menos uma coluna.')

    st.divider()
    st.markdown(f"O dataset possui :blue[{df_dados.shape[0]}] linhas e :blue[{df_dados.shape[1]}] colunas.")

    st.divider()

with aba2:
    # Lista dos tipos de despesa diárias
    tipos_categorias = ['Receita', 'Despesa Moto', 'Despesa Casa', 'Despesa Combustivel', 
                        'Despesa Remedio', 'Outros Laser/Festa/Reforma']

    select_categoria = st.selectbox('Selecione qual a categoria:', tipos_categorias, placeholder='')
    select_valor = st.number_input('Insira o valor R$:', min_value=0.0, format="%.2f", step=0.01)

    if st.button('Adicionar novos valores'):
        if select_categoria and select_valor > 0:
            nova_linha = [datetime.now().strftime("%d/%m/%y"), select_categoria, select_valor]
            st.write(nova_linha)
            st.success("Novo valor adicionado com sucesso!")
        else:
            st.warning("Preencha todos os campos corretamente.")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')