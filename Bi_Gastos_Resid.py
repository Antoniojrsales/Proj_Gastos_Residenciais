#Bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from dotenv import load_dotenv
import os
import streamlit as st
import re

#Criando a conexao com a planilha do google
try:
    load_dotenv()  # Carrega as variáveis do .env
    sheet_id = os.getenv('SHEET_ID')
    sheet_name = os.getenv('SHEET_NAME')
    if sheet_id and sheet_name:
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df_dados = pd.read_csv(url, index_col=0)
        print('Conectado ao Google Sheets com sucesso.')
    else:
        st.error("As variáveis de ambiente SHEET_ID e SHEET_NAME não foram carregadas corretamente.")    
except Exception as e:
    st.error(f"Erro ao conectar com o Google Sheets: {e}")

def clean_currency(value):
    if pd.isna(value):  # Se for NaN, retorna 0.0
        return 0.0
    if isinstance(value, str):
        # Remove "R$", espaços, pontos e mantém apenas números, "-" e ","
        value = re.sub(r'[^\d,.-]', '', value).replace(',', '.')
        return float(value) if value else 0.0
    return float(value)

# Aplica a função e converte a coluna para float
df_dados['Valor'] = df_dados['Valor'].apply(clean_currency).astype(float)

# Lista dos tipos de despesa
tipos_despesa = ['Despesa Moto', 'Despesa Casa', 'Transporte',
                 'Despesa Combustivel', 'Despesa Remedio', 'Luz',
                 'Agua', 'Faculdade', 'Grafnet', 'Claro',
                 'Plano', 'Natacao', 'Nubank', 'Dentista']

# Lista dos tipos de despesa diarias
tipos_despesa_diarias = ['Despesa Moto', 'Despesa Casa', 'Transporte',
                        'Despesa Combustivel', 'Despesa Remedio']

#Filtrar o DataFrame para calcular onde o 'Tipo Receita/Despesa' está na lista de tipos Receita
total_receitas = df_dados[df_dados['Categorias'] == 'Receita']['Valor'].sum()

# Filtrar o DataFrame para incluir linhas onde o 'Tipo Receita/Despesa' está na lista de tipos de despesa
df_despesas = df_dados[df_dados['Categorias'].isin(tipos_despesa)]
total_despesas = df_despesas['Valor'].sum()

# Filtrar o DataFrame para incluir linhas onde o 'Tipo Receita/Despesa' está na lista de tipos de despesa diarias
df_despesas_diarias = df_dados[df_dados['Categorias'].isin(tipos_despesa_diarias)]

# Filtrar o DataFrame para incluir linhas onde o 'Tipo Receita/Despesa' está na lista de tipos de despesa com moradia
df_despesas_moradia = df_dados[df_dados['Categorias'] == 'Despesa Casa']
total_despesas_moradia = df_despesas_moradia['Valor'].mean()

# Filtrar o DataFrame para incluir linhas onde o 'Tipo Receita/Despesa' está na lista de tipos de despesa com combustivel
df_despesas_combustivel = df_dados[df_dados['Categorias'] == 'Despesa Combustivel']
total_despesas_combustivel = df_despesas_combustivel['Valor'].mean()

# Calculando o Saldo Atual (Receita  - Despesas)
saldo_atual = total_receitas - total_despesas

st.set_page_config(
    page_title="Gastos Residenciais",
    page_icon="💰",
    layout="wide"
)


st.sidebar.markdown("""
    <div style="
        padding: 5px;
        text-align: center;">
        <h2 style="font-size: 24px;">Dash Gastos Residenciais</h2>
        <div id="chart-container" style="margin-top: 2px;"></div>
    </div>
""", unsafe_allow_html=True)

with st.sidebar.expander("🔍 Visualizar colunas (debug)"):
    options = st.multiselect('Escolha a Coluna:', df_dados.columns)
    if options:
        df_filtrado = df_dados[options]
        st.write('Dataframe Filtrado:', df_filtrado)
    else:
        st.write('Por favor, selecione ao menos uma coluna.')

col1, col2, col3 = st.columns([1, 1, 1])

with col1:

    card_style = """
        background: linear-gradient(to right, #FF8C00, #E91E63);
        color: white;
        padding: 20px;
        border-radius: 10px;
    """

    saldo_style = """
        font-size: 2em;
        font-weight: bold;
    """

    st.markdown(f"""
        <div style="{card_style}">
            Saldo
            <div style="{saldo_style}">R${saldo_atual:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    card_style_gray = """
        background: linear-gradient(to right, #A9A9A9, #696969);
        color: white;
        padding: 20px;
        border-radius: 10px;
    """

    saldo_style = """
        font-size: 2em;
        font-weight: bold;
    """

    st.markdown(f"""
        <div style="{card_style_gray}">
            Receita
            <div style="{saldo_style}">R${total_receitas:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    card_style_gray = """
        background: linear-gradient(to right, #A9A9A9, #696969);
        color: white;
        padding: 20px;
        border-radius: 10px;
    """

    saldo_style = """
        font-size: 2em;
        font-weight: bold;
    """

    st.markdown(f"""
        <div style="{card_style_gray}">
            Despesas
            <div style="{saldo_style}">R${total_despesas:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

col4, col5 = st.columns([1, 1])

with col4:
    st.markdown("""
        <div style="
            padding: 20px;
            text-align: center;">
            <h3>Distribuição de Despesas Diárias</h3>
            <div id="chart-container" style="margin-top: 10px;"></div>
        </div>
    """, unsafe_allow_html=True)
    fig = px.pie(df_despesas_diarias, 
                    values='Valor', 
                    names='Categorias',
                    hole=0.4,
                    title=" ")

    # Melhorar o layout
    fig.update_layout(
    title_x=0.5,
    width=600,    
    height=350,
    font=dict(size=14),
    margin=dict(l=40, r=40, t=5, b=40))
    st.plotly_chart(fig, use_container_width=True)

with col5:
    col_ed, col_ad = st.columns([1, 1])
    
    with col_ed:
        st.markdown("""
        <div style="
            padding: 20px;">
            <div id="chart-container" style="margin-top: 10px;"></div>
        </div>
        """, unsafe_allow_html=True)

        card_style_gray = """
        background: linear-gradient(to right, #555555, #696969);
        color: white;
        padding: 20px;
        border-radius: 10px;
        """

        saldo_style = """
            font-size: 2em;
            font-weight: bold;
        """

        st.markdown(f"""
            <div style="{card_style_gray}">
                Media de gastos por semana Moradia
                <div style="{saldo_style}">R${total_despesas_moradia:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_ad:
        st.markdown("""
        <div style="
            padding: 20px;">
            <div id="chart-container" style="margin-top: 10px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        card_style_gray = """
        background: linear-gradient(to right, #555555, #696969);
        color: white;
        padding: 20px;
        border-radius: 10px;
        """

        saldo_style = """
            font-size: 2em;
            font-weight: bold;
        """

        st.markdown(f"""
            <div style="{card_style_gray}">
                Media e gastos de Combustivel
                <div style="{saldo_style}">R${total_despesas_combustivel:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

