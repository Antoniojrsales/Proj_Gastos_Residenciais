#-- Bibliotecas --#
import pandas as pd
import streamlit as st
import numpy as np
from typing import Tuple, List, Dict

# ====================================================================
# CONFIGURAÇÃO DE ENGENHARIA DE RECURSOS (Feature Engineering)
# ====================================================================
#-- Estrutura: 'Categoria Detalhada': ('Categoria Principal', 'Tipo' --#)
CATEGORY_MAP = {
    # Receitas
    'Receita': ('Receita', 'Receita'),
    
    # Moradia / Contas Fixas
    'Despesa Casa': ('Moradia/Contas', 'Despesa'),
    'Luz': ('Moradia/Contas', 'Despesa'),
    'Agua': ('Moradia/Contas', 'Despesa'),
    'Grafnet': ('Moradia/Contas', 'Despesa'),
    'Claro': ('Moradia/Contas', 'Despesa'),
    'Plano': ('Moradia/Contas', 'Despesa'),
    
    # Transporte / Veículo
    'Despesa Moto': ('Transporte', 'Despesa'),
    'Despesa Combustivel': ('Transporte', 'Despesa'),
    
    # Saúde
    'Despesa Remedio': ('Saúde', 'Despesa'),
    'Dentista': ('Saúde', 'Despesa'),
    
    # Lazer / Educação / Outros
    'Faculdade': ('Lazer/Educação', 'Despesa'),
    'Outros Laser/Festa/Reforma': ('Lazer/Outros', 'Despesa'),
    'Nubank': ('Financeiro/Dívidas', 'Despesa'), # Exemplo
}

# ====================================================================
# 1. FUNÇÕES DE LIMPEZA E ENRIQUECIMENTO DE DADOS (Processamento Core)
# ====================================================================

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa, converte tipos e adiciona colunas analíticas ao DataFrame.
    """
    if df.empty:
        return df

    # --- 1. LIMPEZA E CONVERSÃO DE TIPOS ---
    
    # A. Coluna 'Categorias': Limpeza inicial para garantir que o MAPA funcione
    if 'Categorias' in df.columns:
        df['Categorias'] = df['Categorias'].astype(str).str.strip().str.title()
        
    # B. Coluna 'Valor': Tratamento robusto para formato BR (milhar/decimal)
    if 'Valor' in df.columns:
        df['Valor'] = df['Valor'].astype(str).str.strip() # Garante que é string e remove espaços
        
        # 1. REMOVE TUDO QUE NÃO É DÍGITO OU VÍRGULA
        df['Valor'] = df['Valor'].str.replace(r'[^\d,]+', '', regex=True) 
        
        # 2. TROCA a VÍRGULA (separador decimal BR) por PONTO (separador decimal Python)
        df['Valor'] = df['Valor'].str.replace(',', '.', regex=False)

        # 3. Conversão segura para float
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    
    # B. Coluna 'Data': Conversão de String (DD/MM/AA) para DateTime
    if 'Data' in df.columns:
        # Use o formato correto da sua planilha, que parece ser DD/MM/AA
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%y', errors='coerce')        
        df.dropna(subset=['Data'], inplace=True)
    
    # Cria uma coluna Mês/Ano (para análise de tendências)
    if 'Data' in df.columns:
        df['Mes/Ano'] = df['Data'].dt.strftime('%b/%Y').astype(str)  # Formato: Jan/2024

    if 'Categorias' in df.columns:
        # Cria Categoria Principal e Tipo (usando o mapeamento)
        df['Categoria Principal'] = df['Categorias'].apply(
            lambda x: CATEGORY_MAP.get(x, ('Outros', 'Despesa'))[0]
        )
        df['Tipo'] = df['Categorias'].apply(
            lambda x: CATEGORY_MAP.get(x, ('Outros', 'Despesa'))[1]
        )

    return df.reset_index(drop=True)

# ====================================================================
# 2. FUNÇÕES DE CÁLCULO MODULARIZADAS (Para o Painel)
# ====================================================================
def calculate_balance(df: pd.DataFrame):
    """Calcula a Receita Total, Despesa Total e Saldo, usando a coluna 'Tipo'."""
    # Garante que as colunas críticas existem (pode remover se o process_data for robusto)
    if df.empty or 'Categorias' not in df.columns or 'Valor' not in df.columns:
        return 0.0, 0.0, 0.0 # Retorna zero se não houver dados

    receita = df[df['Categorias'] == 'Receita']['Valor'].sum()
    despesa = df[df['Categorias'] != 'Receita']['Valor'].sum()
    saldo = receita - despesa
    
    return receita, despesa, saldo

def get_available_months(df: pd.DataFrame) -> List[str]:
    """Gera uma lista de meses únicos (formatados) presentes no DataFrame."""
    if df.empty or 'Mes_Ano' not in df.columns:
        return ['Saldo Atual']
    
    # A lista já está em string (graças ao process_data), apenas pega os únicos
    meses_disponiveis = df['Mes_Ano'].unique().tolist()
    
    # Adiciona o filtro total e inverte a ordem (do mais recente para o mais antigo)
    return ['Saldo Atual'] + sorted(meses_disponiveis, reverse=True)

def calculate_monthly_balance(df: pd.DataFrame, target_month: str) -> Tuple[float, float, float]:
    """Filtra o DF para um mês específico e calcula o balanço."""
    
    if target_month == 'Saldo Atual':
        return calculate_balance(df) # Retorna o total se for Saldo Atual
        
    # Filtra o DataFrame pelo mês escolhido
    df_mes = df[df['Mes_Ano'] == target_month]
    
    # Reutiliza a função principal de balanço, agora no DF filtrado
    return calculate_balance(df_mes)

def calculate_average_by_category(df: pd.DataFrame, category: str) -> float:
    """Calcula a média de gastos para uma Categoria Principal."""
    df_filtered = df[df['Categorias'] == category]
    if df_filtered.empty:
        return 0.0

    return df_filtered['Valor'].mean() if not df_filtered.empty else 0.0

def calculate_average_by_detailed_category(df: pd.DataFrame, detailed_category: str) -> float:
    """Calcula a média de gastos para uma Categoria Detalhada específica (coluna 'Categorias')."""
    df_filtered = df[df['Categorias'] == detailed_category]
    if df_filtered.empty:
        return 0.0

    return df_filtered.groupby('Mes/Ano')['Valor'].sum().mean()

# ====================================================================
# 3. FUNÇÃO DE VISUALIZAÇÃO (Componente Reutilizável)
# ====================================================================
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
