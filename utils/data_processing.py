import pandas as pd

# Mapeamento para criar a coluna de Categoria Principal e o Tipo (Receita/Despesa)
CATEGORY_MAP = {
    # Receitas
    'Receita': ('Receita', 'Receita'),
    
    # Despesas de Moradia/Contas
    'Luz': ('Despesa/Moradia', 'Despesa'),
    'Agua': ('Despesa/Moradia', 'Despesa'),
    'Grafnet': ('Despesa/Moradia', 'Despesa'),
    'Claro': ('Despesa/Moradia', 'Despesa'),
    'Plano': ('Despesa/Moradia', 'Despesa'),
    'Despesa Casa': ('Despesa/Moradia', 'Despesa'),
    'Natacao': ('Despesa/Moradia', 'Despesa'),
    'Nubank': ('Despesa/Moradia', 'Despesa'),
    'Dentista': ('Despesa/Moradia', 'Despesa'),
    'Faculdade': ('Despesa/Moradia', 'Despesa'),
    
    # Despesas de Transporte
    'Despesa Moto': ('Despesa Moto', 'Despesa'),
    'Despesa Combustivel': ('Despesa Combustivel', 'Despesa'),
    
    # Outros
    'Despesa Remedio': ('Despesa Remedio', 'Despesa'),    
    'Outros Laser/Festa/Reforma': ('Lazer/Outros', 'Despesa')    

    # Adicione suas outras categorias aqui...
}

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa, converte tipos e adiciona colunas analíticas ao DataFrame.
    """
    if df.empty:
        return df

    # --- 1. CONVERSÃO CRÍTICA DE TIPOS ---
    
    # A. Coluna 'Valor': Remove R$, substitui vírgulas por pontos e converte para float
    if 'Valor' in df.columns:
        df['Valor'] = df['Valor'].astype(str).str.replace('R$', '', regex=False).str.replace(',', '.', regex=False)
        # Força o tipo numérico. 'coerce' transforma erros em NaN para tratamento posterior
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce') 
        # Remove linhas com Valor inválido ou zero, para análise (opcional)
        df.dropna(subset=['Valor'], inplace=True)
    
    # B. Coluna 'Data': Conversão de String (DD/MM/AA) para DateTime
    if 'Data' in df.columns:
        # Use o formato correto da sua planilha, que parece ser DD/MM/AA
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%y', errors='coerce')
        df.dropna(subset=['Data'], inplace=True)
    
    # --- 2. ENGENHARIA DE RECURSOS (Hierarquia e Tipo) ---
    if 'Categorias' in df.columns:
        # Cria as colunas analíticas a partir do mapeamento
        df['Categoria Principal'] = df['Categorias'].apply(
            lambda x: CATEGORY_MAP.get(x, ('Outros', 'Despesa'))[0] # Pega o primeiro item (Principal)
        )
        df['Tipo'] = df['Categorias'].apply(
            lambda x: CATEGORY_MAP.get(x, ('Outros', 'Despesa'))[1] # Pega o segundo item (Tipo)
        )
    
    # Cria uma coluna Mês/Ano (para análise de tendências)
    if 'Data' in df.columns:
        df['Mes_Ano'] = df['Data'].dt.to_period('M')

    return df.reset_index(drop=True)