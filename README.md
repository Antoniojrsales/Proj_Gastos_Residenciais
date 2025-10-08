# 🏠 Projeto: Gastos Residenciais - Análise Financeira com Streamlit e Google Sheets

Este projeto é uma ferramenta interativa desenvolvida em Streamlit para registrar, analisar e visualizar de forma eficiente as despesas e receitas residenciais. Ele utiliza o Google Sheets como backend de dados, demonstrando habilidades em integração de API e visualização de dados em tempo real.

## ✅ Etapas de Inicialização

- Estruturação do projeto em pastas
- Criação do ambiente virtual
- Definição das bibliotecas principais (via `requirements.txt`)
- Configuração do `.gitignore`
- Primeiros arquivos adicionados ao controle de versão

## 📁 Estrutura Inicial de Pastas

```
Proj_Gastos_Residenciais/
├── .streamlit/
│   └── secrets.toml  
├── analysis/
│   └── exploration.ipynb  
├── pages/
│   ├── 1_🔑_login.py      
│   ├── 2_🏠_painel.py      
│   ├── 3_🎲_dados.py      
│   └── 4_📊_graficos.py    
├── utils/
│   ├── data_processing.py 
│   └── db_connector.py    
├── venv/
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## ✨ Funcionalidades Principais

| Recurso | Descrição | Habilidades Demonstradas |
| :--- | :--- | :--- |
| **Registro e Categorização** | Entrada rápida e validada de despesas e receitas, utilizando uma hierarquia de categorias (ex: Moradia > Luz, Água). | UX/UI, Validação de Dados, Estruturação de Dados. |
| **Dashboard de Balanço** | Visualização de métricas-chave (Receita Total, Despesa Total e Saldo) em tempo real. | Streamlit Metrics, Análise Financeira. |
| **Gráficos Interativos** | Análise da distribuição de gastos por categoria e tendências históricas mês a mês, utilizando Plotly para interatividade. | Plotly, Pandas, Visualização de Dados. |
| **Modularidade** | Separação da lógica de dados (db_connector) e processamento (data_processing) do frontend Streamlit. | Engenharia de Software, Modularidade, Boas Práticas. |

## 🛠 Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes ferramentas e bibliotecas:

* **Python 3.x**
* **Streamlit:** Para a criação da interface web interativa.
* **Pandas:** Para manipulação e processamento de dados.
* **Plotly:** Para a geração de gráficos de alta qualidade e interativos.
* **Google Sheets API:** Para persistência e leitura dos dados em nuvem.

## ⚙️ Como Instalar e Rodar o Projeto
Para executar a aplicação em sua máquina local, siga os passos abaixo:

1. Clonagem e Configuração do Ambiente
```
# Clone o repositório
git clone [SEU_LINK_DO_REPOSITORIO]
cd Proj_Gastos_Residenciais

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

2. Configuração do Google Sheets API
Crie um arquivo de serviço JSON para acessar sua planilha do Google Sheets.

Crie o arquivo .streamlit/secrets.toml e adicione suas credenciais e a key do arquivo JSON conforme a documentação do Streamlit.

3. Execução da Aplicação
Após configurar as credenciais, inicie o Streamlit:

```
streamlit run 1_login.py
```

## 🔐 Detalhe Técnico: Sistema de Login
O sistema de login foi implementado com foco em segurança e modularidade, utilizando as seguintes práticas:

* **Autenticação Segura:** As credenciais de usuário são armazenadas no arquivo seguro .streamlit/secrets.toml e as senhas são criptografadas utilizando o algoritmo SHA256.

* **Gerenciamento de Estado:** Utilizamos st.session_state para rastrear o estado do usuário (logged_in), garantindo que a aplicação saiba se o acesso deve ser permitido.

* **Proteção de Páginas:** Uma função de validação (utils/auth_check.py) verifica o estado de login no início de cada página, impedindo o acesso não autorizado ao dashboard e aos dados.

## ✨ Funcionalidades Principais (3_🎲_dados)

Recurso	Descrição |	Habilidades | Demonstradas
| :--- | :--- | :--- |
* **Registro de Gastos (CRUD):** | Formulário robusto para inserção de dados, com validações em tempo real e uso do CATEGORY_MAP para garantir a consistência das entradas. |	CRUD (Create), Validação de Dados, Python/Pandas.
* **Arquitetura do Formulário:** | Utiliza o st.form com gerenciamento de estado (st.session_state) para limpar o formulário e gerenciar o cache (st.cache_data.clear()) de forma eficiente após a submissão. | Engenharia de Software, Gerenciamento de Cache, UX em Streamlit.
* **Visualização Detalhada:** |	Exibe dados brutos em uma tabela interativa (st.dataframe) com filtros de colunas, formatação de moeda (R$) e opções de visualização (Todos, Head, Tail). |	Visualização de Dados, st.column_config, Pandas.