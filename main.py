# 1. Importações
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

# 2. Carregar Variáveis de Ambiente
load_dotenv() 

# 3. Configurar a Conexão com o Banco de Dados
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

db_uri = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_uri)

# --- INÍCIO: DEFINIÇÃO DO SCHEMA CUSTOMIZADO E DETALHADO ---

# Dicionário com as definições precisas das tabelas para a IA.
# Os comentários (--) são dicas valiosas que a IA usará para entender melhor o negócio.
custom_table_info = {
    "custos": f"""
CREATE TABLE custos (
    id BIGINT PRIMARY KEY, -- Identificador único do custo
    descricao TEXT NOT NULL, -- Descrição do que foi o custo
    valor DECIMAL(15, 2) NOT NULL, -- Valor monetário do custo
    data_registro TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Data em que o custo foi inserido no sistema
    categoria TEXT, -- Categoria do custo (ex: 'ração', 'manutenção', 'salários')
    observacoes TEXT, -- Observações adicionais
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Data de criação do registro
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- Data da última atualização do registro
);
""",
    "abates": f"""
CREATE TABLE abates (
    id BIGINT PRIMARY KEY, -- Identificador único do abate
    data_abate TIMESTAMP WITH TIME ZONE NOT NULL, -- Data exata em que o abate ocorreu
    quantidade INTEGER NOT NULL, -- Número de animais abatidos
    peso_total DECIMAL(15, 2) NOT NULL, -- Peso total em kg dos animais abatidos
    peso_medio DECIMAL(15, 2) GENERATED ALWAYS AS (peso_total / NULLIF(quantidade, 0)) STORED, -- Peso médio por animal (calculado automaticamente)
    local_abate TEXT, -- Local onde o abate foi realizado
    observacoes TEXT, -- Observações adicionais sobre o lote ou processo
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Data de criação do registro
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- Data da última atualização do registro
);
""",
    "vendas": f"""
CREATE TABLE vendas (
    id BIGINT PRIMARY KEY, -- Identificador único da venda
    data_venda TIMESTAMP WITH TIME ZONE NOT NULL, -- Data exata em que a venda foi realizada
    cliente TEXT, -- Nome ou identificador do cliente que comprou
    quantidade INTEGER NOT NULL, -- Quantidade de itens/animais vendidos
    peso_total DECIMAL(15, 2) NOT NULL, -- Peso total em kg do que foi vendido
    valor_total DECIMAL(15, 2) NOT NULL, -- Valor monetário total da venda
    valor_por_kg DECIMAL(15, 2) GENERATED ALWAYS AS (valor_total / NULLIF(peso_total, 0)) STORED, -- Preço por kg (calculado automaticamente)
    forma_pagamento TEXT, -- Método de pagamento (ex: 'PIX', 'Boleto', 'Cartão')
    observacoes TEXT, -- Observações adicionais sobre a venda
    abate_id BIGINT REFERENCES abates(id), -- Chave estrangeira que conecta a venda ao abate correspondente
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Data de criação do registro
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- Data da última atualização do registro
);
"""
}

# --- FIM DA DEFINIÇÃO DO SCHEMA ---

# Passe o schema customizado para o objeto SQLDatabase
db = SQLDatabase(
    engine=engine,
    custom_table_info=custom_table_info
)

# 4. Inicializar o LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# 5. Criar o Agente de SQL
agent_executor = create_sql_agent(
    llm=llm, 
    db=db, 
    agent_type="openai-tools", 
    verbose=True
)

# 6. Loop Principal (sem alterações)
if __name__ == "__main__":
    print("Olá! Sou um agente de IA conectado a um banco de dados. Faça sua pergunta.")
    
    while True:
        try:
            user_question = input("Você: ")
            
            if user_question.lower() == "sair":
                print("Até mais!")
                break
            
            response = agent_executor.invoke({"input": user_question})
            
            print(f"Agente: {response['output']}")

        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            break