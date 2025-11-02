import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.auth_check import check_login
from utils.data_processing import aggregate_monthly_data

st.set_page_config(
    page_title="Tendências | Gastos Residencias",
    page_icon="📊",
    layout="wide"
)

check_login()

# Acessa o DataFrame salvo na sessão
if 'df_Bi_Gastos_Resid' in st.session_state:
    df_dados = st.session_state['df_Bi_Gastos_Resid']
else:
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")

# Chama a função modularizada para obter os dados agregados
df_tendencia = aggregate_monthly_data(df_dados)

if df_tendencia.empty:
    st.warning("Dados insuficientes ou falha na agregação para análise de tendência.")
    st.stop()

st.markdown("""
    <div style="
        text-align: center;">
        <h3 style=" font-size: 2em; 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            Evolução Mensal da Receita e Despesa
        </h3>
        
    </div>
""", unsafe_allow_html=True)

fig = go.Figure()

# --- 1. GRÁFICO DE LINHAS (EVOLUCAO MENSAL) ---
# Linha da Receita
fig.add_trace(go.Scatter(
    x=df_tendencia['Mes/Ano'], 
    y=df_tendencia['Receita'],
    mode='lines+markers',
    name='Receita',
    line=dict(color='#2ECC71', width=3) # Verde
))

# Linha da Despesa
fig.add_trace(go.Scatter(
    x=df_tendencia['Mes/Ano'], 
    y=df_tendencia['Despesa'],
    mode='lines+markers',
    name='Despesa',
    line=dict(color='#E74C3C', width=3) # Vermelho
))

fig.update_layout(
    xaxis_title='Mês/Ano',
    yaxis_title='Valor (R$)',
    hovermode="x unified",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# --- 2. GRÁFICO DE BARRAS (SALDO MENSAL) ---
st.markdown("""
    <div style="
        text-align: center;">
        <h3 style=" font-size: 2em; 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            Saldo Líquido Mensal
        </h3>
        
    </div>
""", unsafe_allow_html=True)

fig_bar = px.bar(
    df_tendencia, 
    x='Mes/Ano', 
    y='Saldo',
    color='Saldo',
    color_continuous_scale=[(0, 'red'), (0.5, 'yellow'), (1, 'green')],
    title="Saldo por Mês"
)

fig_bar.update_traces(marker_color=['red' if s < 0 else 'green' for s in df_tendencia['Saldo']])

st.plotly_chart(fig_bar, use_container_width=True)

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')