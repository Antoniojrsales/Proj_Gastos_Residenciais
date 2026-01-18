# ---------------------------------------------------------
# 📚 BIBLIOTECAS E RECURSOS INTERNOS
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# ⚙️ CONFIGURAÇÕES INICIAIS DA INTERFACE (STREAMLIT)
# ---------------------------------------------------------
# 1. Define o título da aba e o ícone da aplicação
# 2. Configura o layout como 'wide' para usar toda a largura da tela
# 3. Adiciona os créditos do desenvolvedor na barra lateral
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

# ---------------------------------------------------------
# 🎨 ESTILIZAÇÃO E CABEÇALHO HTML
# ---------------------------------------------------------
# 1. Função para carregar arquivo CSS externo
# 2. Renderiza o título principal da página usando tags HTML/CSS personalizadas
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🔐 SEGURANÇA E CONTROLE DE SESSÃO
# ---------------------------------------------------------
# 1. Verifica se o usuário está logado
# 2. Inicializa chaves de controle no session_state para reset de formulários
# 3. Valida se os dados necessários existem na memória antes de prosseguir
check_login()
if 'df_Bi_Gastos_Resid' in st.session_state:
    df_dados = st.session_state['df_Bi_Gastos_Resid']
else:
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")

# ---------------------------------------------------------
# 📑 ESTRUTURA DE NAVEGAÇÃO (TABS)
# ---------------------------------------------------------
# 1. Cria as abas de 'Dados Brutos' e 'Inserção'
# 2. Aplica o arquivo de estilos CSS local
aba1, aba2 = st.tabs(['Visualização', 'Predição']) 
local_css("style.css")

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
    fig.add_trace(go.Scatter(
        x=df_tendencia['Mes/Ano'], 
        y=df_tendencia['Receita'],
        mode='lines+markers',
        name='Receita',
        line=dict(color='#2ECC71', width=3) # Verde
    ))

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

    st.divider()

    fig_bar = px.bar(
        df_tendencia, 
        x='Mes/Ano', 
        y='Saldo',
        color='Saldo',
        color_continuous_scale=[(0, 'red'), (0.5, 'yellow'), (1, 'green')],
        title="Saldo Líquido Mensal",
        text_auto=True
    )

    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        #paper_bgcolor='lightgray',
        title_x=0.5, 
        title_font_size=24, 
        showlegend=False,
        xaxis=dict(
            tickfont=dict(
                family="Arial",
                size=12,
                color="#000000"
            ),
            title_font=dict(size=18)
        ),
        yaxis=dict(
            tickfont=dict(
                family="Arial",
                size=12,
                color="#000000"
            ),
            title_font=dict(size=18)
        )
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
 
            fig = go.Figure()
            if opcao_analise == "Apenas Receitas":
                fig.add_trace(go.Scatter(x=df_ts.index, y=df_ts['Receita'], mode='lines+markers', name='Histórico', line=dict(color='#2ECC71', width=3)))
                fig.add_trace(go.Scatter(x=pred_mean_rec.index, y=pred_mean_rec, mode='lines', name='Previsão', line=dict(color='#2ECC71', width=3, dash='dash')))
                titulo = "Análise de Receita: Histórico vs Previsão"

            elif opcao_analise == "Apenas Despesas":
                fig.add_trace(go.Scatter(x=df_ts.index, y=df_ts['Despesa'], mode='lines+markers', name='Histórico', line=dict(color='#e74c3c', width=3)))
                fig.add_trace(go.Scatter(x=pred_mean_desp.index, y=pred_mean_desp, mode='lines', name='Previsão', line=dict(color='#e74c3c', width=3, dash='dash')))
                titulo = "Análise de Despesa: Histórico vs Previsão"

            elif opcao_analise == "Comparativo Geral":
                # Receitas
                fig.add_trace(go.Scatter(x=df_ts.index, y=df_ts['Receita'], mode='lines+markers', name='Hist. Receita', line=dict(color='#2ECC71', width=2)))
                fig.add_trace(go.Scatter(x=pred_mean_rec.index, y=pred_mean_rec, mode='lines', name='Prev. Receita', line=dict(color='#2ECC71', width=2, dash='dash')))
                # Despesas
                fig.add_trace(go.Scatter(x=df_ts.index, y=df_ts['Despesa'], mode='lines+markers', name='Hist. Despesa', line=dict(color='#e74c3c', width=2)))
                fig.add_trace(go.Scatter(x=pred_mean_desp.index, y=pred_mean_desp, mode='lines', name='Prev. Despesa', line=dict(color='#e74c3c', width=2, dash='dash')))
                titulo = "Comparativo Geral: Receitas vs Despesas"

            # Configuração Única de Layout
            fig.update_layout(
                title=titulo,
                xaxis_title="Data",
                yaxis_title="Valor (R$)",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=60, b=20), # Ajusta margens para ganhar espaço
                plot_bgcolor='rgba(0,0,0,0)', # Fundo transparente (opcional)
            )

            # Grade horizontal suave (estilo gráfico moderno)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(211, 211, 211, 0.3)')

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao calcular: {e}")