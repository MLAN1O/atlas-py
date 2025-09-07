# main.py
# Ponto de entrada principal da aplicação

# Importa as funções e classes necessárias dos módulos refatorados
from app.core.config import OPENAI_API_KEY, GOOGLE_API_KEY
from app.tools.supabase_tools import get_database_connection
from app.agents.sql_agent import create_sql_agent_executor

# Importa os modelos de linguagem do LangChain
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def main():
    """
    Função principal para inicializar e executar o Agente de IA.
    """
    print("--- Iniciando o Agente Financeiro Proativo ---")

    # 1. Inicializa a conexão com o banco de dados usando a ferramenta dedicada
    try:
        db_connection = get_database_connection()
    except Exception:
        # A função get_database_connection já imprime o erro detalhado.
        print("--- Encerramento devido a erro de conexão ---")
        return

    # 2. Configuração do Modelo de IA (LLM)
    # A lógica para escolher ou configurar o LLM fica aqui, no ponto de entrada.
    
    # --- Configuração OpenAI (Padrão) ---
    if not OPENAI_API_KEY:
        print("Erro: OPENAI_API_KEY não encontrada. Verifique seu arquivo .env")
        return
    
    llm = ChatOpenAI(
        model="gpt-4.1-mini", 
        temperature=0,
        api_key=OPENAI_API_KEY
    )
    print(f"Usando o modelo: {llm.model_name}")
    # --- Fim da Configuração OpenAI ---

    # --- Configuração Google Gemini (Alternativa) ---
    # Para usar o Gemini, comente o bloco OpenAI acima e descomente este.
    # if not GOOGLE_API_KEY:
    #     print("Erro: GOOGLE_API_KEY não encontrada. Verifique seu arquivo .env")
    #     return
    #
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-1.5-flash-latest",
    #     temperature=0,
    #     google_api_key=GOOGLE_API_KEY,
    # )
    # print(f"Usando o modelo: {llm.model}")
    # --- Fim da Configuração Google Gemini ---

    # 3. Criação do Agente SQL
    # A função de criação do agente é chamada, passando o LLM e o DB já prontos.
    sql_agent_executor = create_sql_agent_executor(llm=llm, db=db_connection)

    print("\nAgente pronto para uso. Converse com seus dados!")
    print("Para sair, digite 'sair' ou 'exit'.")

    # 4. Loop Conversacional
    # O loop de interação com o usuário fica no ponto de entrada da aplicação.
    while True:
        try:
            user_query = input("\nSua pergunta: ")
            if user_query.lower() in ["sair", "exit"]:
                print("Encerrando a conversa. Até mais!")
                break

            # Invoca o agente com a pergunta do usuário
            response = sql_agent_executor.invoke({"input": user_query})
            print(f"Resposta: {response['output']}")

        except KeyboardInterrupt:
            print("\nExecução interrompida pelo usuário. Encerrando...")
            break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
