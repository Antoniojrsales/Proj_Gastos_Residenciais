import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.auth_check import check_login
from utils.data_processing import aggregate_monthly_data
from datetime import date
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Tendências | Gastos Residencias",
    page_icon="📊",
    layout="wide"
)

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

st.markdown("""
<div style="
    padding: 5px;
    text-align: center;">
    <h2 style=" font-size: 40px; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif">
                Tendências | Gastos Residencias</h2>
    <div id="chart-container" style="margin-bottom: 30px; color:'blue'"></div>
</div>
""", unsafe_allow_html=True)

check_login()

# Acessa o DataFrame salvo na sessão
if 'df_Bi_Gastos_Resid' in st.session_state:
    df_dados = st.session_state['df_Bi_Gastos_Resid']
else:
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")

aba1, aba2 = st.tabs(['Visualização', 'Predição']) 

# Chama a função modularizada para obter os dados agregados
df_tendencia = aggregate_monthly_data(df_dados)

with aba1:
    if df_tendencia.empty:
        st.warning("Dados insuficientes ou falha na agregação para análise de tendência.")
        st.stop()

    st.markdown("""
        <div style="
            text-align: center;">
            <h3 style=" font-size: 1.5em; 
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
            <h3 style=" font-size: 1.5em; 
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

with aba2:
    if df_tendencia.empty:
        st.warning("Dados insuficientes ou falha na agregação para análise de tendência.")
        st.stop()

    st.markdown("""
        <div style="
            text-align: center;">
            <h3 style=" font-size: 1.5em; 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                Sistema de Análise e Previsão de Séries Temporais
            </h3>
            
        </div>
    """, unsafe_allow_html=True)

    # Configurações na barra lateral ou principal
    col1, col2 = st.columns(2)
    with col1:
        periodo_previsao = st.number_input("Meses para prever", 1, 48, 12)
    with col2:
        # Opção de seleção solicitada
        opcao_analise = st.selectbox("O que deseja analisar?", 
                                    ["Comparativo Geral", "Apenas Receitas", "Apenas Despesas", "Saldo Líquido"])

    processar = st.button("Executar Previsão")
    st.markdown("""
        <style>
        /* Alvo específico para o botão de submit dentro do form */
        .stButton > button {
            background-color: #075eb2 !important;
            color: white !important;
            border-radius: 5px;
            border: none;
            height: auto;
            padding: 0.5em 1em;
        }
        
        /* Efeito de hover para não ficar estático */
        .stButton > button:hover {
            background-color: #004d9f !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)

    if processar:
        try:
            # Preparação do DataFrame
            df_ts = df_tendencia.copy()
            df_ts['Mes/Ano'] = pd.to_datetime(df_ts['Mes/Ano'], format='%b/%Y')
            df_ts.set_index('Mes/Ano', inplace=True)
            df_ts = df_ts.asfreq('MS').fillna(0)

            # --- PROCESSAMENTO SEPARADO PARA CÁLCULOS ---
            
            # 1. Modelo para Receita
            mod_rec = SARIMAX(df_ts['Receita'], order=(1,1,1), seasonal_order=(0,1,1,12))
            res_rec = mod_rec.fit(disp=False)
            pred_mean_rec = res_rec.get_forecast(steps=periodo_previsao).predicted_mean

            # 2. Modelo para Despesa
            mod_desp = SARIMAX(df_ts['Despesa'], order=(1,1,1), seasonal_order=(0,1,1,12))
            res_desp = mod_desp.fit(disp=False)
            pred_mean_desp = res_desp.get_forecast(steps=periodo_previsao).predicted_mean

            # --- CÁLCULO DAS MÉTRICAS ---
            total_rec = pred_mean_rec.sum()
            total_desp = pred_mean_desp.sum()
            saldo_proj = total_rec - total_desp

            # Exibição das Métricas no Streamlit
            st.markdown("### 📊 Resumo da Projeção (Próximos meses)")
            m1, m2, m3 = st.columns(3)
            m1.metric("Receita Total", f"R$ {total_rec:,.2f}")
            m2.metric("Despesa Total", f"R$ {total_desp:,.2f}", delta_color="inverse")
            m3.metric("Saldo Projetado", f"R$ {saldo_proj:,.2f}")

            # --- LÓGICA DO GRÁFICO (Baseado na seleção do Selectbox) ---
            fig, ax = plt.subplots(figsize=(12, 6))
            
            if opcao_analise == "Apenas Receitas":
                ax.plot(df_ts.index, df_ts['Receita'], label='Histórico', color='#2ecc71')
                ax.plot(pred_mean_rec.index, pred_mean_rec, '--', color='#2ecc71', label='Previsão')
            
            elif opcao_analise == "Apenas Despesas":
                ax.plot(df_ts.index, df_ts['Despesa'], label='Histórico', color='#e74c3c')
                ax.plot(pred_mean_desp.index, pred_mean_desp, '--', color='#e74c3c', label='Previsão')
                
            elif opcao_analise == "Comparativo Geral":
                # Plota ambos
                ax.plot(df_ts.index, df_ts['Receita'], color='#2ecc71', label='Rec. Real')
                ax.plot(pred_mean_rec.index, pred_mean_rec, '--', color='#2ecc71', label='Rec. Prevista')
                ax.plot(df_ts.index, df_ts['Despesa'], color='#e74c3c', label='Desp. Real')
                ax.plot(pred_mean_desp.index, pred_mean_desp, '--', color='#e74c3c', label='Desp. Prevista')

            ax.legend()
            ax.grid(True, alpha=0.2)
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Erro ao calcular: {e}")
            