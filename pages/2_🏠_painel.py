#Bibliotecas
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.data_processing import render_card, calculate_balance, get_available_months, calculate_average_by_category, calculate_monthly_balance, calculate_average_by_detailed_category
from utils.auth_check import check_login

# -------------------------------
# 1. CONFIGURAÇÃO E SEGURANÇA
# -------------------------------
st.set_page_config(
    page_title="Painel Geral | Gastos Residencias",
    page_icon="🏠",
    layout="wide"
)

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

check_login()

# Acessa o DataFrame salvo na sessão
if 'df_Bi_Gastos_Resid' in st.session_state:
    df_dados = st.session_state['df_Bi_Gastos_Resid']
else:
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")

# -------------------------------
# 2. LÓGICA DO FILTRO TEMPORAL
# -------------------------------
# 1. Obtém a lista de meses (modularizada)
meses_disponiveis = get_available_months(df_dados)
mes_escolhido = st.sidebar.selectbox('Escolha o mês: ', meses_disponiveis, index=0)

# Calcula o balanço (Total ou Mensal)
receita, despesa, saldo = calculate_monthly_balance(df_dados, mes_escolhido)
col1, col2, col3 = st.columns([1, 1, 1])
if mes_escolhido == 'Saldo Atual':
    with col1:
        render_card(f"Saldo de {mes_escolhido}" if mes_escolhido != 'Saldo Atual' else "Saldo Atual", 
                saldo, "#FF8C00, #E91E63")
    with col2:
        render_card(f"Receita de {mes_escolhido}" if mes_escolhido != 'Saldo Atual' else "Receita", 
                receita, "#A9A9A9, #696969")
    with col3:
        render_card(f"Despesas de {mes_escolhido}" if mes_escolhido != 'Saldo Atual' else "Despesas", 
                despesa, "#A9A9A9, #696969")

# -------------------------------
# 4. GRÁFICO DE PIZZA (Distribuição de Despesas)
# -------------------------------
col4, col5 = st.columns([1, 1])
with col4:
    st.markdown("""
        <div style="
            padding: 20px;
            text-align: center;">
            <h3 style=" font-size: 2em; 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                Distribuição de Despesas Diárias
            </h3>
            <div id="chart-container" style="margin-top: 10px;"></div>
        </div>
    """, unsafe_allow_html=True)
    # Filtra para o Tipo 'Despesa'
    df_despesas = df_dados[df_dados['Tipo'] == 'Despesa']
    
    # 1. Agrupa pela Categoria Principal (Visão de Alto Nível) ou Categorias detalhadas
    df_pie = df_despesas.groupby('Categoria Principal')['Valor'].sum().reset_index()

    fig = px.pie(df_pie, 
                 values='Valor', 
                 names='Categoria Principal',
                 hole=0.4,
                 title=" ")

    # Melhorar o layout
    fig.update_layout(
                title_x=0.5,
                width=900,    
                height=400,
                font=dict(size=14),
                margin=dict(l=40, r=40, t=5, b=40))
    st.plotly_chart(fig, use_container_width=True)

with col5:
    st.markdown("""
        <div style="
            padding: 20px;
            text-align: center;">
            <h3 style=" font-size: 2em; 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                Distribuição Principais Gastos
            </h3>
            <div id="chart-container"></div>
        </div>
    """, unsafe_allow_html=True)
    
    col_11, col_12 = st.columns([1, 1])
    
    media_casa = calculate_average_by_category(df_dados, 'Despesa Casa')
    with col_11:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Média de gastos com Moradia", media_casa, "#555555, #696969")

    media_combustivel = calculate_average_by_category(df_dados, 'Despesa Combustivel')
    with col_12:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos Combustivel", media_combustivel, "#555555, #696969")
    
    col_21, col_22 = st.columns([1, 1])

    media_remedio = calculate_average_by_detailed_category(df_dados, 'Despesa Remedio')
    with col_21:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos com Remedios", media_remedio, "#555555, #696969")

    media_moto = calculate_average_by_detailed_category(df_dados, 'Despesa Moto')        
    with col_22:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Média Gasto Moto", media_moto, "#555555, #696969")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')