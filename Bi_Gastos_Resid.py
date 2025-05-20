#Bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import streamlit as st
import re

st.set_page_config(
    page_title="Gastos Residenciais",
    page_icon="💰",
    layout="wide"
)

@st.cache_data(ttl=600)
#Criando a conexao com a planilha do google sheets
def carregar_dados():
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
    
df_dados = carregar_dados()

# Lista dos tipos de despesa
tipos_despesa = ['Despesa Moto', 'Despesa Casa', 'Despesa Combustivel', 'Despesa Remedio', 
                 'Luz', 'Agua', 'Faculdade', 'Grafnet', 'Claro', 'Plano', 'Natacao', 
                 'Nubank', 'Dentista', 'Outros Laser/Festa/Reforma']

# Lista dos tipos de despesa diarias
tipos_despesa_diarias = ['Despesa Moto', 'Despesa Casa', 'Despesa Combustivel', 
                         'Despesa Remedio', 'Outros Laser/Festa/Reforma']

def clean_currency(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, str):
        # Remove "R$", espaços e pontos (separadores de milhar), e substitui a vírgula por ponto
        value = re.sub(r'[^\d,-]', '', value).replace(',', '.')
        # Remove os pontos usados como separador de milhar
        value = value.replace('.', '') if '.' in value and value.count('.') > 1 else value
        return float(value) if value else 0.0
    return float(value)

# Aplica a função e converte a coluna para float
df_dados['Valor'] = df_dados['Valor'].apply(clean_currency).astype(float)

df_dados['Categorias'] = df_dados['Categorias'].str.strip().str.title()

df_dados['Data'] = pd.to_datetime(df_dados['Data'], format='%d/%m/%y', errors='coerce')
df_dados['Mes'] = df_dados['Data'].dt.strftime('%b/%Y')  # Formato: Jan/2024

# Funcao que Calcula o total das receitas.
def revenues():
    # Soma todos os 'Valor's associados à categoria 'Receita' no DataFrame 'df_dados'.
    total_receitas = df_dados[df_dados['Categorias'] == 'Receita']['Valor'].sum()
    
    # Retorna o valor total das receitas.
    return total_receitas

# Funcao que Calcula o total das despesas
def general_expenses():
    # Soma todos os 'Valor's associados às categorias de despesa listadas em 'tipos_despesa' no DataFrame 'df_dados'.
    df_despesas = df_dados[df_dados['Categorias'].isin(tipos_despesa)]    
    total_despesas = df_despesas['Valor'].sum()
    
    # Retorna o valor total das despesas.
    return total_despesas

# Funcao que Filtra o total das despesas diarias
def daily_expenses():
    # Filtra todos os 'Valor's associados às categorias de despesa listadas em 'tipos_despesa_diarias' no DataFrame 'df_dados'.
    df_despesas_diarias = df_dados[df_dados['Categorias'].isin(tipos_despesa_diarias)]

    # Retorna o valor total das despesas.
    return df_despesas_diarias

def despesas_moradia():
    total_despesas_moradia = df_dados[df_dados['Categorias'] == 'Despesa Casa']['Valor'].mean()
    return  total_despesas_moradia

def despesas_remedio():
    df_despesas_remedio = df_dados[df_dados['Categorias'] == 'Despesa Remedio']
    total_despesas_remedio = df_despesas_remedio['Valor'].mean()
    return  total_despesas_remedio

def despesas_combustivel():
    df_despesas_combustivel = df_dados[df_dados['Categorias'] == 'Despesa Combustivel']
    total_despesas_combustivel = df_despesas_combustivel['Valor'].mean()
    return total_despesas_combustivel

def despesas_conserto_veicular():
    df_despesas_conserto_veicular = df_dados[df_dados['Categorias'] == 'Despesa Moto']
    total_despesas_conserto_veicular = df_despesas_conserto_veicular['Valor'].mean()
    return total_despesas_conserto_veicular

def receitas_despesas_mensais(df):
    df = df.copy()
    df['Data'] = pd.to_datetime(df['Data'])  # garante que 'Data' é datetime
    df['Mes'] = df['Data'].dt.to_period('M').astype(str)

    df['Tipo'] = df['Categorias'].apply(lambda x: 'Receita' if x == 'Receita' else 'Despesa')

    df_grouped = df.groupby(['Mes', 'Tipo'])['Valor'].sum().unstack().fillna(0)
    return df_grouped

def render_card(title, value, gradient):
    valor_formatado = f"R${value:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
    card_style = f"""
        background: linear-gradient(to right, {gradient});
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
            {title}
            <div style="{saldo_style}">{valor_formatado}</div>
        </div>
    """, unsafe_allow_html=True)


# Calculando o Saldo Atual (Receita  - Despesas)
saldo_atual = revenues() - general_expenses()

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
    render_card("Saldo Atual", saldo_atual, "#FF8C00, #E91E63")

with col2:
    render_card("Receita", revenues(), "#A9A9A9, #696969")

with col3:
    render_card("Despesas", general_expenses(), "#A9A9A9, #696969")

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
    fig = px.pie(daily_expenses(), 
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
    st.markdown("""
        <div style="
            padding: 20px;
            text-align: center;">
            <h3>Distribuição Principais Gastos</h3>
            <div id="chart-container"></div>
        </div>
    """, unsafe_allow_html=True)

    col_11, col_12 = st.columns([1, 1])
    
    with col_11:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos por semana Moradia", despesas_moradia(), "#555555, #696969")

    with col_12:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos de Combustivel", despesas_combustivel(), "#555555, #696969")
    
    col_21, col_22 = st.columns([1, 1])

    with col_21:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos com Remedios", despesas_remedio(), "#555555, #696969")

    with col_22:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos com Veiculo", despesas_conserto_veicular(), "#555555, #696969")

# Separar receitas e despesas
receitas_por_mes = df_dados[df_dados['Categorias'] == 'Receita'].groupby('Mes')['Valor'].sum()
despesas_por_mes = df_dados[df_dados['Categorias'] != 'Receita'].groupby('Mes')['Valor'].sum()

# Unir num DataFrame para facilitar o gráfico
df_grafico = pd.DataFrame({
    'Receitas': receitas_por_mes,
    'Despesas': despesas_por_mes
}).fillna(0)  # Preencher valores ausentes com zero

# Resetar o índice para usar no Plotly
df_grafico = df_grafico.reset_index()

df_grafico['Mes'] = pd.to_datetime(df_grafico['Mes'], format='%b/%Y')
df_grafico = df_grafico.sort_values('Mes')
df_grafico['Mes'] = df_grafico['Mes'].dt.strftime('%b/%Y')


fig = go.Figure(
    data=[
        go.Bar(x=df_grafico['Mes'], y=df_grafico['Receitas'], name='Receitas', marker_color='mediumseagreen'),
        go.Bar(x=df_grafico['Mes'], y=df_grafico['Despesas'], name='Despesas', marker_color='indianred')
    ]
)

fig.update_layout(
    title="Receitas vs Despesas por Mês",
    title_x=0.5,
    title_font=dict(size=22),
    xaxis_title="Mês",
    xaxis_title_font=dict(size=18),
    yaxis_title="Valor (R$)",
    yaxis_title_font=dict(size=18),
    plot_bgcolor='white',
    legend=dict(
        x=1.02, y=1,
        traceorder="normal",
        font=dict(size=12),
        bordercolor="Black",
        borderwidth=1
    )
)

fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')

st.plotly_chart(fig, use_container_width=True)