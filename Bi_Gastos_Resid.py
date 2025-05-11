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
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    print('Conectado ao Google Sheets com sucesso.')
except Exception as e:
    print(f"Erro ao conectar com o Google Sheets: {e}")

#Transformando os dados em um DataFrame
df_dados = pd.read_csv(url, index_col=0)
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

#Filtrar o DataFrame para calcular onde o 'Tipo Receita/Despesa' está na lista de tipos Receita
total_receitas = df_dados[df_dados['Tipo Receita/Despesa'] == 'Receita']['Valor'].sum()

# Filtrar o DataFrame para incluir linhas onde o 'Tipo Receita/Despesa' está na lista de tipos de despesa
df_despesas = df_dados[df_dados['Tipo Receita/Despesa'].isin(tipos_despesa)]

#Filtrar o DataFrame para calcular onde o 'Tipo Receita/Despesa' está na lista de tipos Despesa
total_despesas = df_despesas['Valor'].sum()

# Calculando o Saldo Atual (Receita  - Despesas)
saldo_atual = total_receitas - total_despesas

st.sidebar.header('Dash Gastos Residenciais')

options = st.sidebar.multiselect('Escolha a Coluna: ', df_dados.columns)
if options:  # Verifica se alguma coluna foi selecionada
    df_filtrado = df_dados[options]
    st.write('Dataframe Filtrado:', df_filtrado)
else:
    st.write('Por favor, selecione ao menos uma coluna.')


col1, col2, col3 = st.columns(3)

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