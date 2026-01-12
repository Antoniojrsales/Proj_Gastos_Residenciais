# ---------------------------------------------------------
# 📚 BIBLIOTECAS E RECURSOS INTERNOS
# ---------------------------------------------------------
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth_check import check_login
from utils.db_connector import get_gspread_client, append_row, load_data

# ---------------------------------------------------------
# ⚙️ CONFIGURAÇÕES INICIAIS DA INTERFACE (STREAMLIT)
# ---------------------------------------------------------
# 1. Define o título da aba e o ícone da aplicação
# 2. Configura o layout como 'wide' para usar toda a largura da tela
# 3. Adiciona os créditos do desenvolvedor na barra lateral
st.set_page_config(
    page_title="Visualização dos Dados | Gastos Residencias)",
    page_icon="🎲",
    layout="wide"
)
st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

# ---------------------------------------------------------
# 🎨 ESTILIZAÇÃO E CABEÇALHO HTML
# ---------------------------------------------------------
# 1. Função para carregar arquivo CSS externo
# 2. Renderiza o título principal da página usando tags HTML/CSS personalizadas
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div style="
    padding: 5px;
    text-align: center;">
    <h2 style=" font-size: 40px; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif">
                Visualização dos Dados | Gastos Residencias</h2>
    <div id="chart-container" style="margin-bottom: 30px; color:'blue'"></div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🔐 SEGURANÇA E CONTROLE DE SESSÃO
# ---------------------------------------------------------
# 1. Verifica se o usuário está logado
# 2. Inicializa chaves de controle no session_state para reset de formulários
# 3. Valida se os dados necessários existem na memória antes de prosseguir
check_login()
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

df_dados = st.session_state['df_Bi_Gastos_Resid']
if df_dados.empty:    
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")
    st.stop()

# ---------------------------------------------------------
# 📑 ESTRUTURA DE NAVEGAÇÃO (TABS)
# ---------------------------------------------------------
# 1. Cria as abas de 'Dados Brutos' e 'Inserção'
# 2. Aplica o arquivo de estilos CSS local
aba1, aba2 = st.tabs(['Dados Brutos', 'Inserindo Dados na base'])
local_css("style.css")

# ---------------------------------------------------------
# 🔍 ABA 1: VISUALIZAÇÃO E FILTRAGEM
# ---------------------------------------------------------
# 1. Filtros laterais para selecionar colunas e tipo de visualização (Top/Bottom)
# 2. Aplica configurações de formatação de moeda (R$) na coluna de valores
# 3. Exibe o resumo quantitativo (linhas e colunas) do dataset
with aba1:
    with st.sidebar.expander("🔍 Visualizar colunas"):
        options = st.multiselect('Escolha a Coluna:', df_dados.columns, default=list(df_dados.columns))

    options_dados = st.sidebar.radio('Escolha qual o filtro de visualização:',
                            ['Todos', 'Head', 'Tail'])

    if options:
        df_filtrado = df_dados[options]

        # Adicione a formatação de moeda para a coluna Valor
        column_config = {
            "Valor": st.column_config.NumberColumn(
                "Valor",
                format="R$ %0.2f",
                help="Valor do gasto ou receita"
            )
        }
        if options_dados == 'Todos':
            st.dataframe(df_filtrado, column_config=column_config)
        elif options_dados == 'Head':
            st.dataframe(df_filtrado.head(10), column_config=column_config)
        else:
            st.dataframe(df_filtrado.tail(10), column_config=column_config)
    else:
        st.write('Por favor, selecione ao menos uma coluna.')

    st.divider()
    st.markdown("Dimensões do DataFrame:")
    st.markdown(f"Linhas: \t {df_dados.shape[0]}")
    st.markdown(f"Colunas: \t {df_dados.shape[1]}")
    st.divider()

# ---------------------------------------------------------
# 📝 ABA 2: FORMULÁRIO DE ENTRADA DE DADOS
# ---------------------------------------------------------
# 1. Prepara as categorias e estabelece conexão com Google Sheets
# 2. Constrói a interface do formulário (Data, Valor, Categoria, Descrição)
# 3. Aplica CSS customizado para o botão de submissão azul
with aba2:
    tipos_categorias_disponiveis = sorted(df_dados['Categorias'].unique()) 
    sheet_client, connected = get_gspread_client() 

    with st.form("form_novo_gasto"):
        col_data, col_valor = st.columns(2)
        with col_data:
            select_data = st.date_input('Selecione a Data:', datetime.now().date())
        
        with col_valor:
            select_valor = st.number_input('Insira o valor R$:', min_value=0.01, format="%.2f", step=0.01)

        select_categoria = st.selectbox('Selecione qual a categoria:', tipos_categorias_disponiveis, index=None, placeholder='Escolha uma categoria...')
        
        select_descricao = st.text_input('Descrição (Opcional, mas Recomendado):', placeholder='Ex: Almoço no Centro, Pedágio, etc.')
        
        submit_button = st.form_submit_button('Adicionar novos valores')
        st.markdown("""
        <style>
        /* Alvo específico para o botão de submit dentro do form */
        .stFormSubmitButton > button {
            background-color: #075eb2 !important;
            color: white !important;
            border-radius: 5px;
            border: none;
            height: auto;
            padding: 0.5em 1em;
        }
        
        /* Efeito de hover para não ficar estático */
        .stFormSubmitButton > button:hover {
            background-color: #004d9f !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 💾 LÓGICA DE PROCESSAMENTO E ENVIO
    # ---------------------------------------------------------
    # 1. Valida se os campos obrigatórios foram preenchidos
    # 2. Formata os dados para o padrão da planilha (DD/MM/AAAA)
    # 3. Envia para o DB e atualiza o estado global para refletir as mudanças
    if submit_button:
        if not connected:
             st.error("❌ Conexão com o Google Sheets falhou. Tente novamente mais tarde.")
        elif not select_categoria:
            st.warning("⚠️ Por favor, selecione uma Categoria.")
        elif select_valor <= 0.0:
            st.warning("⚠️ O valor deve ser maior que zero.")
        else:
            data_formatada = select_data.strftime("%d/%m/%Y") 
            
            nova_linha = [data_formatada, select_categoria, select_valor, select_descricao] 
            
            if append_row(nova_linha, sheet_client):
                st.success("✅ Novo valor adicionado com sucesso e salvo na planilha!")
                st.session_state.form_key += 1
                st.session_state['df_Bi_Gastos_Resid'] = load_data(
                    st.secrets["SHEET"]["SHEET_NAME"], sheet_client
                )

            else:
                st.error("❌ Falha ao salvar no Google Sheets. Verifique o console.")
