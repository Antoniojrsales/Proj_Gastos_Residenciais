#Bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from dotenv import load_dotenv
import os
import streamlit as st

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
df_dados = pd.read_csv(url)
options = st.multiselect('Escolha a Coluna: ', df_dados.columns)
if options:  # Verifica se alguma coluna foi selecionada
    df_filtrado = df_dados[options]
    st.write('Dataframe Filtrado:', df_filtrado)
else:
    st.write('Por favor, selecione ao menos uma coluna.')