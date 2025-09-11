# main.py
# Ponto de entrada principal da aplicação que monta e executa o Agente Orquestrador.

import datetime
import uuid

# Importa os componentes de configuração e ferramentas
from app.core.config import OPENAI_API_KEY, GOOGLE_API_KEY, DATABASE_URL
from app.tools.supabase_tools import get_database_connection

# Importa os construtores de todos os agentes e chains
from app.agents.sql_agent import create_sql_agent_executor
from app.agents.report_agent import create_report_chain
from app.agents.orchestrator_agent import create_orchestrator_agent_executor

# Importa os modelos de linguagem do LangChain
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Importa os componentes de memória
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory

def main():
    """
    Função principal que inicializa todos os componentes e inicia o loop de conversa.
    """
    print("--- Iniciando o Agente Financeiro Proativo ---")

    # 1. Define a data atual para ser usada no prompt do orquestrador
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Data atual definida como: {current_date}")

    # Gera um ID de sessão único para a conversa atual
    session_id = str(uuid.uuid4())
    print(f"ID da Sessão: {session_id}")

    # 2. Inicializa o LLM (Modelo de Linguagem)
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=OPENAI_API_KEY)
    print(f"Usando o modelo: {llm.model_name}")

    # 3. Configura o histórico de mensagens persistente
    try:
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection_string=DATABASE_URL,
            table_name="chat_messages" # Nome da tabela para o histórico
        )
        # Cria a memória com janela de 5 interações
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            chat_memory=message_history,
            k=5, # Mantém as últimas 5 interações
            return_messages=True
        )
        print("Histórico de mensagens e memória configurados com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar o histórico de mensagens: {e}")
        return

    # 4. Inicializa as ferramentas e sub-agentes
    try:
        db_connection = get_database_connection()
        sql_agent = create_sql_agent_executor(llm=llm, db=db_connection)
        report_chain = create_report_chain(llm=llm)
    except Exception as e:
        print(f"Erro durante a inicialização dos componentes: {e}")
        return

    # 5. Cria o Agente Orquestrador, passando os outros agentes, a data e a memória
    orchestrator = create_orchestrator_agent_executor(
        llm=llm,
        sql_agent_executor=sql_agent,
        report_chain=report_chain,
        current_date=current_date,
        memory=memory
    )

    print("\n🤖 Agente Orquestrador pronto. Você pode começar a conversar.")
    print("Para sair, digite 'sair' ou 'exit'.")

    # 6. Loop Conversacional com o Orquestrador
    while True:
        try:
            user_query = input("\nSua pergunta: ")
            if user_query.lower() in ["sair", "exit"]:
                print("Encerrando a conversa. Até mais!")
                break

            # Invoca o orquestrador com a pergunta do usuário
            response = orchestrator.invoke({"input": user_query})
            
            # A resposta final já deve vir formatada pelo report_agent
            print(f"\nResposta:\n{response['output']}")

        except KeyboardInterrupt:
            print("\nExecução interrompida pelo usuário. Encerrando...")
            break
        except Exception as e:
            print(f"Ocorreu um erro durante a execução: {e}")

if __name__ == "__main__":
    main()
