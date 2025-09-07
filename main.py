# main.py
# Ponto de entrada principal da aplicação que monta e executa o Agente Orquestrador.

# Importa os componentes de configuração e ferramentas
from app.core.config import OPENAI_API_KEY, GOOGLE_API_KEY
from app.tools.supabase_tools import get_database_connection

# Importa os construtores de todos os agentes e chains
from app.agents.sql_agent import create_sql_agent_executor
from app.agents.entry_agent import create_entry_agent_executor
from app.agents.report_agent import create_report_chain
from app.agents.orchestrator_agent import create_orchestrator_agent_executor

# Importa os modelos de linguagem do LangChain
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def main():
    """
    Função principal que inicializa todos os componentes e inicia o loop de conversa.
    """
    print("--- Iniciando o Agente Financeiro Proativo ---")

    # 1. Inicializa o LLM (Modelo de Linguagem)
    # Usaremos o mesmo LLM para todos os agentes para consistência.
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=OPENAI_API_KEY)
    print(f"Usando o modelo: {llm.model_name}")

    # 2. Inicializa as ferramentas e sub-agentes
    try:
        db_connection = get_database_connection()
        sql_agent = create_sql_agent_executor(llm=llm, db=db_connection)
        entry_agent = create_entry_agent_executor(llm=llm)
        report_chain = create_report_chain(llm=llm)
    except Exception as e:
        print(f"Erro durante a inicialização dos componentes: {e}")
        return

    # 3. Cria o Agente Orquestrador, passando os outros agentes como ferramentas
    orchestrator = create_orchestrator_agent_executor(
        llm=llm,
        sql_agent_executor=sql_agent,
        entry_agent_executor=entry_agent,
        report_chain=report_chain
    )

    print("\n🤖 Agente Orquestrador pronto. Você pode começar a conversar.")
    print("Para sair, digite 'sair' ou 'exit'.")

    # 4. Loop Conversacional com o Orquestrador
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