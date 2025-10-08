import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth_check import check_login
from utils.db_connector import get_gspread_client, append_row, load_data

st.set_page_config(
    page_title="Visualização dos Dados | Gastos Residencias)",
    page_icon="🎲",
    layout="wide"
)

check_login()

# --- INICIALIZAÇÃO DO ESTADO DE SESSÃO ---
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

df_dados = st.session_state['df_Bi_Gastos_Resid']
if df_dados.empty:    
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")
    st.stop()

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

aba1, aba2 = st.tabs(['Dados Brutos', 'Inserindo Dados na base']) 

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
    st.markdown(f"O dataset possui :blue[{df_dados.shape[0]}] linhas e :blue[{df_dados.shape[1]}] colunas.")

    st.divider()

with aba2:
    # Obtemos a lista de categorias únicas e ordenadas a partir do nosso mapa
    tipos_categorias_disponiveis = sorted(df_dados['Categorias'].unique()) 

    # Conexão gspread (se ainda não estiver definida no topo)
    sheet_client, connected = get_gspread_client() 

    # --- Formulário ---
    with st.form("form_novo_gasto"):
        col_data, col_valor = st.columns(2)
        with col_data:
            # Recomendo usar st.date_input para garantir o tipo data
            select_data = st.date_input('Selecione a Data:', datetime.now().date())
        
        with col_valor:
            select_valor = st.number_input('Insira o valor R$:', min_value=0.01, format="%.2f", step=0.01)

        select_categoria = st.selectbox('Selecione qual a categoria:', tipos_categorias_disponiveis, index=None, placeholder='Escolha uma categoria...')
        
        # Adicione uma descrição, é fundamental para análise!
        select_descricao = st.text_input('Descrição (Opcional, mas Recomendado):', placeholder='Ex: Almoço no Centro, Pedágio, etc.')
        
        submit_button = st.form_submit_button('Adicionar novos valores')

    # --- Lógica de Submissão ---
    if submit_button:
        if not connected:
             st.error("❌ Conexão com o Google Sheets falhou. Tente novamente mais tarde.")
        elif not select_categoria:
            st.warning("⚠️ Por favor, selecione uma Categoria.")
        elif select_valor <= 0.0:
            st.warning("⚠️ O valor deve ser maior que zero.")
        else:
            # 1. Formatação da Linha
            # Se o seu Sheets espera [Data, Categorias, Valor], ajuste a lista abaixo.
            # O formato da data deve ser compatível com o que o Sheets espera:
            data_formatada = select_data.strftime("%d/%m/%Y") 
            
            nova_linha = [data_formatada, select_categoria, select_valor, select_descricao] 
            
            # 2. Chama a função de escrita (do db_connector.py)
            if append_row(nova_linha, sheet_client):
                st.success("✅ Novo valor adicionado com sucesso e salvo na planilha!")
                # 1. Incrementa a chave para forçar a limpeza do formulário
                st.session_state.form_key += 1
                # 3. Atualiza o DataFrame e Força o Recarregamento
                st.session_state['df_Bi_Gastos_Resid'] = load_data(
                    st.secrets["SHEET"]["SHEET_NAME"], sheet_client
                )

            else:
                st.error("❌ Falha ao salvar no Google Sheets. Verifique o console.")

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')