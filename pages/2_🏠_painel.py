#Bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import re

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

def calculate_sum(df, categoria):
    return df[df['Categorias'] == categoria]['Valor'].sum()

def calculate_mean(df, categoria):
    return df[df['Categorias'] == categoria]['Valor'].mean()

def calculate_total(df, categoria):
    return df[df['Categorias'] == categoria].groupby('Mes')['Valor'].sum().mean()

def total_revenue(df):
    # Soma os valores da categoria 'Receita'
    return calculate_sum(df, 'Receita')

def general_expense():
    # Soma os valores total da categoria 'despesas'
    df_despesas = df_dados[df_dados['Categorias'].isin(tipos_despesa)]    
    total_despesas = df_despesas['Valor'].sum()
    
    # Retorna o valor total das despesas.
    return total_despesas

def daily_expense():
    # Filtra todos os 'Valor's associados às categorias de despesa listadas em 'tipos_despesa_diarias' no DataFrame 'df_dados'.
    df_despesas_diarias = df_dados[df_dados['Categorias'].isin(tipos_despesa_diarias)]

    # Retorna o valor total das despesas diarias.
    return df_despesas_diarias

def housing_expenses(df):
    # Retorna uma media por semana dos valores da categoria 'despesas moradia'
    return  calculate_mean(df, 'Despesa Casa')

def remedy_expenses(df):    
    # Retorna uma media por mes dos valores da categoria 'despesas remedios'
    return  calculate_total(df, 'Despesa Remedio')

def fuel_expenses(df):
    # Retorna a media diaria dos valores da categoria 'despesas combustivel'
    return calculate_mean(df, 'Despesa Combustivel')

def repair_expenses(df):   
    # Retorna a media por mes dos valores da categoria 'Despesa Moto'
    return calculate_total(df, 'Despesa Moto')

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
        font-size: 1.2em;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    """
    saldo_style = """
        font-size: 1.5em;
        font-weight: bold;
    """
    st.markdown(f"""
        <div style="{card_style}">
            {title}
            <div style="{saldo_style}">{valor_formatado}</div>
        </div>
    """, unsafe_allow_html=True)

# Aplica a função e converte a coluna para float
df_dados['Valor'] = df_dados['Valor'].apply(clean_currency).astype(float)

df_dados['Categorias'] = df_dados['Categorias'].str.strip().str.title()

df_dados['Data'] = pd.to_datetime(df_dados['Data'], format='%d/%m/%y', errors='coerce')
df_dados['Mes'] = df_dados['Data'].dt.strftime('%b/%Y')  # Formato: Jan/2024

# Separar receitas e despesas
receitas_por_mes = df_dados[df_dados['Categorias'] == 'Receita'].groupby('Mes')['Valor'].sum()
despesas_por_mes = df_dados[df_dados['Categorias'] != 'Receita'].groupby('Mes')['Valor'].sum()

# Preparar lista de meses únicos (já formatados no estilo 'Jan/2025')
meses_disponiveis = ['Saldo Atual'] + list(receitas_por_mes.index)
mes_escolhido = st.sidebar.selectbox('Escolha o mês: ', meses_disponiveis, index=0)

col1, col2, col3 = st.columns([1, 1, 1])
if mes_escolhido == 'Saldo Atual': # Obter valores total
    # Calculando o Saldo Atual (Receita  - Despesas)
    saldo_atual = total_revenue(df_dados) - general_expense()
    
    with col1:
        render_card("Saldo Atual", saldo_atual, "#FF8C00, #E91E63")
    with col2:
        render_card("Receita", total_revenue(df_dados), "#A9A9A9, #696969")
    with col3:
        render_card("Despesas", general_expense(), "#A9A9A9, #696969")
else: # Obter valores específicos do mês escolhido
    receita_mes = receitas_por_mes.get(mes_escolhido, 0)
    despesa_mes = despesas_por_mes.get(mes_escolhido, 0)
    saldo_mes = receita_mes - despesa_mes
    
    with col1:
        render_card(f"Saldo de {mes_escolhido}", saldo_mes, "#FF8C00, #E91E63")
    with col2:
        render_card(f"Receita de {mes_escolhido}", receita_mes, "#A9A9A9, #696969")
    with col3:
        render_card(f"Despesas de {mes_escolhido}", despesa_mes, "#A9A9A9, #696969")

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
    fig = px.pie(daily_expense(), 
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
            <h3 style=" font-size: 2em; 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                Distribuição Principais Gastos
            </h3>
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
        
        render_card("Media de gastos com Moradia", housing_expenses(df_dados), "#555555, #696969")

    with col_12:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos Combustivel", fuel_expenses(df_dados), "#555555, #696969")
    
    col_21, col_22 = st.columns([1, 1])

    with col_21:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos com Remedios", remedy_expenses(df_dados), "#555555, #696969")

    with col_22:
        st.markdown("""
        <div style="
            padding: 10px;">
            <div id="chart-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        render_card("Media de gastos com Veiculo", repair_expenses(df_dados), "#555555, #696969")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')