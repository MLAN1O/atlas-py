# main.py
# Ponto de entrada principal da aplicação que monta e executa o Agente Orquestrador com LangGraph.

import datetime
import uuid

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver

# Importa os componentes de configuração e ferramentas
from app.core.config import OPENAI_API_KEY
from app.tools.supabase_tools import get_database_connection

# Importa os construtores de agentes e do grafo
from app.agents.sql_agent import create_sql_agent_executor
from app.agents.report_agent import create_report_chain
from app.agents.orchestrator_agent import create_orchestrator_agent_runnable
from app.graph.builder import create_graph_with_persistence

def main():
    """
    Função principal que inicializa todos os componentes e inicia o loop de conversa.
    """
    print("--- Iniciando o Agente Financeiro Proativo com LangGraph ---")

    # Gera um ID de sessão (thread) único para a conversa atual
    thread_id = str(uuid.uuid4())
    print(f"ID da Conversa (Thread ID): {thread_id}")

    # 1. Inicializa o LLM
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, api_key=OPENAI_API_KEY)
    print(f"Usando o modelo: {llm.model_name}")

    # 2. Inicializa as ferramentas e sub-agentes
    try:
        db_connection = get_database_connection()
        sql_agent = create_sql_agent_executor(llm=llm, db=db_connection)
        report_chain = create_report_chain(llm=llm)
    except Exception as e:
        print(f"Erro durante a inicialização dos componentes: {e}")
        return

    # 3. Cria o agente executável e as ferramentas
    agent_runnable, tools = create_orchestrator_agent_runnable(
        llm=llm,
        sql_agent_executor=sql_agent,
        report_chain=report_chain,
    )

    # 4. Configura a persistência (checkpointer) e compila o grafo
    # Usando SQLite em memória para simplicidade. O bloco `with` gerencia a conexão.
    with SqliteSaver.from_conn_string(":memory:") as checkpointer:
        # 5. Cria e compila o grafo com a persistência
        graph = create_graph_with_persistence(agent_runnable, tools, checkpointer)

        print("\n🤖 Agente Orquestrador (LangGraph) pronto. Você pode começar a conversar.")
        print("Para sair, digite 'sair' ou 'exit'.")

        # 6. Loop Conversacional com o Grafo
        while True:
            try:
                user_query = input("\nSua pergunta: ")
                if user_query.lower() in ["sair", "exit"]:
                    print("Encerrando a conversa. Até mais!")
                    break

                # Define a data atual para o contexto do agente
                current_date = datetime.date.today().strftime("%Y-%m-%d")

                # Define a entrada para o grafo
                inputs = {
                    "input": user_query, # Adiciona a chave 'input'
                    "messages": [HumanMessage(content=user_query)],
                    "current_date": current_date,
                    "intermediate_steps": []
                }
                
                # Configuração para a execução do grafo, especificando o ID da thread
                config = {"configurable": {"thread_id": thread_id}}

                # Executa o grafo e faz o stream da resposta
                final_response = None
                print("\nResposta:")
                for event in graph.stream(inputs, config, stream_mode="values"):
                    # O `stream` retorna o estado completo do grafo a cada passo.
                    # A resposta final estará na última mensagem.
                    final_response = event["messages"][-1]
                
                if final_response:
                    print(final_response.content)

            except KeyboardInterrupt:
                print("\nExecução interrompida pelo usuário. Encerrando...")
                break
            except Exception as e:
                print(f"Ocorreu um erro durante a execução: {e}")

if __name__ == "__main__":
    main()