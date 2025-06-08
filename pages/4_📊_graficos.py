import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Graficos (Gastos Residencias)",
    page_icon="📊",
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

# Separar receitas e despesas
receitas_por_mes = df_dados[df_dados['Categorias'] == 'Receita'].groupby('Mes')['Valor'].sum()
despesas_por_mes = df_dados[df_dados['Categorias'] != 'Receita'].groupby('Mes')['Valor'].sum()

c = st.container()
with c:
    st.markdown("""
        <div style="
            text-align: center;">
            <h3 style=" font-size: 2em; 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                Distribuição de Despesas Diárias
            </h3>
            
        </div>
    """, unsafe_allow_html=True)
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
        xaxis_title="Meses",
        xaxis_title_font=dict(size=20),
        yaxis_title="Valor (R$)",
        yaxis_title_font=dict(size=20),
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

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')