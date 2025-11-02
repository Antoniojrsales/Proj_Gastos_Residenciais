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

## 🔐 Funcionalidades Principais (1_🗝️_login)
O sistema de login foi implementado com foco em segurança e modularidade, utilizando as seguintes práticas:

* **Autenticação Segura:** As credenciais de usuário são armazenadas no arquivo seguro .streamlit/secrets.toml e as senhas são criptografadas utilizando o algoritmo SHA256.

* **Gerenciamento de Estado:** Utilizamos st.session_state para rastrear o estado do usuário (logged_in), garantindo que a aplicação saiba se o acesso deve ser permitido.

* **Proteção de Páginas:** Uma função de validação (utils/auth_check.py) verifica o estado de login no início de cada página, impedindo o acesso não autorizado ao dashboard e aos dados.

## ✨ Funcionalidades Principais (2_🏠_painel)

Recurso	| Descrição	| Habilidades Demonstradas
| :--- | :--- | :--- |
| **Arquitetura Modular (DRY):** | Todos os cálculos (Receita, Despesa, Saldos e Médias) são isolados em funções no utils/data_processing.py, garantindo que o Painel seja apenas uma camada de apresentação. | Modularidade, Princípio DRY, Engenharia de Software.|
| **Filtro Temporal Dinâmico:** | O Painel permite alternar entre o Balanço Total e o Balanço Mensal (mês a mês), utilizando funções modularizadas (calculate_monthly_balance) para filtrar e recalcular as métricas em tempo real. | Manipulação de Séries Temporais, UX/UI, Gerenciamento de Filtros.|
| **Gráfico de Distribuição:** | Apresenta a distribuição percentual dos gastos agrupados por 'Categoria Principal' (recurso criado via Feature Engineering), fornecendo uma visão de alto nível do orçamento. | Visualização de Dados (Plotly), Análise de Alto Nível.|
| **Métricas Detalhadas:** | Exibe cartões de média de gastos por Categoria Detalhada (ex: Despesa Casa, Despesa Moto), utilizando uma função específica (calculate_average_by_detailed_category) para precisão analítica. | Flexibilidade Analítica, Manipulação Avançada de Pandas.|

## ✨ Funcionalidades Principais (3_🎲_dados)

Recurso	Descrição |	Habilidades | Demonstradas
| :--- | :--- | :--- |
| **Registro de Gastos (CRUD):** | Formulário robusto para inserção de dados, com validações em tempo real e uso do CATEGORY_MAP para garantir a consistência das entradas. |	CRUD (Create), Validação de Dados, Python/Pandas.|
| **Arquitetura do Formulário:** | Utiliza o st.form com gerenciamento de estado (st.session_state) para limpar o formulário e gerenciar o cache (st.cache_data.clear()) de forma eficiente após a submissão. | Engenharia de Software, Gerenciamento de Cache, UX em Streamlit.|
| **Visualização Detalhada:** | Exibe dados brutos em uma tabela interativa (st.dataframe) com filtros de colunas, formatação de moeda (R$) e opções de visualização (Todos, Head, Tail). | Visualização de Dados, st.column_config, Pandas.|

## ✨ Funcionalidades Principais (4_📊_Gráficos)

Recurso | Descrição | Habilidades Demonstradas
| :--- | :--- | :--- |
| **Gráfico de Tendência Histórica:** | Gráfico de linha interativo que traça a evolução mensal da Receita e da Despesa. O eixo temporal é ordenado corretamente usando manipulação de strings Pandas (%Y-%m). | Série Temporal, Visualização de Tendência, Manipulação de Eixo Cronológico.|
| **Análise de Balanço Mensal:** | Gráfico de barras que exibe o Saldo (Receita - Despesa) para cada mês. As barras são coloridas dinamicamente (Verde para Saldo Positivo, Vermelho para Negativo). | Plotly Avançado, Mapeamento de Cores Dinâmicas, Análise de Fluxo de Caixa.|
| **Agregação Modular:** | O DataFrame é pré-agregado por mês/tipo de forma eficiente por uma função única (aggregate_monthly_data), garantindo que o Plotly receba dados prontos para visualização. | Engenharia de Dados (Aggregation), Desempenho.|