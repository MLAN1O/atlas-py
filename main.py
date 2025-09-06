# main.py
import os
from dotenv import load_dotenv

# Importar componentes necessários do LangChain
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def main():
    """
    Função principal para inicializar e interagir com o Agente de IA.
    """
    print("Iniciando o Agente de IA para Análise de Dados...")

    # 1. Configuração do Banco de Dados PostgreSQL (Supabase)
    # As variáveis de conexão do banco de dados devem ser carregadas de variáveis de ambiente
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_port = os.getenv("DB_PORT")

    # Verifica se todas as variáveis de ambiente necessárias estão definidas
    if not all([db_host, db_name, db_user, db_pass, db_port]):
        print("Erro: Uma ou mais variáveis de ambiente do banco de dados (DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT) não estão definidas.")
        print("Por favor, configure suas credenciais do Supabase no arquivo .env.")
        return

    # Constrói a string de conexão do PostgreSQL
    # Ex: postgresql+psycopg2://user:password@host:port/dbname
    database_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    try:
        # Inicializa a conexão com o banco de dados usando LangChain
        # LangChain pode inferir o esquema, mas um "mapa detalhado e customizado" [3]
        # pode ser fornecido através de ferramentas ou ajustes no prompt.
        db = SQLDatabase.from_uri(database_url)
        print("Conexão com o banco de dados PostgreSQL (Supabase) estabelecida.")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        print("Verifique suas variáveis de ambiente DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT e as credenciais.")
        return

    # Mensagem do sistema para instruir o LLM a não usar Markdown
    prompt_message = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=[],
            template='''
IMPORTANT: When providing a SQL query, you MUST NOT use any markdown formatting.
The SQL query must be a single, raw string. For example:
SELECT * FROM users;'''
        )
    )

    # --- Configuração OpenAI (Comentado) ---
    # # 2. Configuração do Modelo de IA (GPT-4o-mini)
    # # A chave da API OpenAI deve ser carregada de variáveis de ambiente
    # # Ex: OPENAI_API_KEY="sua_chave_aqui"
    # openai_api_key = os.getenv("OPENAI_API_KEY")
    # if not openai_api_key:
    #     print("Erro: A variável de ambiente OPENAI_API_KEY não está definida.")
    #     print("Por favor, configure sua chave da API OpenAI.")
    #     return
    # 
    # llm = ChatOpenAI(
    #     model="gpt-4o-mini",  # Conforme especificado na fonte [3]
    #     temperature=0,        # Geralmente 0 para tarefas baseadas em fatos como consultas SQL
    #     api_key=openai_api_key
    # )
    # print(f"Modelo de IA '{llm.model_name}' configurado.")
    # 
    # # 3. Criação do Agente SQL
    # # O LangChain fornece a função `create_sql_agent` para facilitar isso [5].
    # # O AgentType.OPENAI_FUNCTIONS é recomendado para modelos OpenAI.
    # # Verbose=True ajuda a ver os passos intermediários do agente.
    # agent_executor = create_sql_agent(
    #     llm=llm,
    #     db=db,
    #     agent_type=AgentType.OPENAI_FUNCTIONS,
    #     verbose=True,
    #     extra_prompt_messages=[prompt_message]
    # )
    # --- Fim da Configuração OpenAI ---

    # --- Configuração Google Gemini (Ativo) ---
    # 2. Configuração do Modelo de IA (Gemini)
    # A chave da API Google deve ser carregada de variáveis de ambiente
    # Ex: GOOGLE_API_KEY="sua_chave_aqui"
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("Erro: A variável de ambiente GOOGLE_API_KEY não está definida.")
        print("Por favor, configure sua chave da API Google.")
        return

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        google_api_key=google_api_key,
    )
    print(f"Modelo de IA 'gemini-2.5-flash-lite' configurado.")

    # 3. Criação do Agente SQL
    # Para o Gemini, não especificamos o agent_type, permitindo que o LangChain
    # utilize o suporte nativo a "tool calling" do modelo.
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        extra_prompt_messages=[prompt_message]
    )
    print("Agente de IA criado com sucesso. Você pode começar a conversar com seus dados.")
    print("Para sair, digite 'sair' ou 'exit'.")

    # 4. Loop Conversacional
    # Permite ao usuário "conversar" com os dados do banco de dados [1].
    while True:
        user_query = input("\nSua pergunta: ")
        if user_query.lower() in ["sair", "exit"]:
            print("Encerrando a conversa. Até mais!")
            break

        try:
            # Invoca o agente com a pergunta do usuário
            response = agent_executor.invoke({"input": user_query})
            # A resposta do agente é o resultado da consulta ao banco de dados
            print(f"Resposta: {response['output']}")
        except Exception as e:
            print(f"Ocorreu um erro ao processar sua pergunta: {e}")
            print("Por favor, tente novamente ou verifique as configurações do agente/banco de dados.")

if __name__ == "__main__":
    main()