# 1. Importações
import os
import psycopg2
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain import hub

# 2. Função de Execução de SQL (com correções)
def execute_sql_query(query: str) -> list:
    """
    Conecta-se a um banco de dados PostgreSQL, executa uma consulta SQL e retorna os resultados.
    """
    # Garante que as credenciais do DB sejam carregadas no contexto de execução da ferramenta.
    load_dotenv()

    # --- INÍCIO DA NOVA CORREÇÃO ---
    # Sanitização da query SQL gerada pelo LLM.
    # Modelos de linguagem podem, ocasionalmente, envolver a query em markdown (acentos graves)
    # ou aspas. Esta etapa remove esses caracteres, além de espaços em branco no início e
    # no fim, para evitar erros de sintaxe no banco de dados.
    # Ex: '`SELECT * FROM users;`' se torna 'SELECT * FROM users;'
    cleaned_query = query.strip().strip('`').strip('"').strip("'").strip()
    # --- FIM DA NOVA CORREÇÃO ---

    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()
        
        # Executa a query já limpa
        cur.execute(cleaned_query)
        
        # A verificação do tipo de comando também usa a string limpa
        if cleaned_query.strip().upper().startswith("SELECT"):
            column_names = [desc[0] for desc in cur.description]
            results = [dict(zip(column_names, row)) for row in cur.fetchall()]
            return results if results else ["Nenhum resultado encontrado."]
        else:
            conn.commit()
            return [f"Comando executado com sucesso. Linhas afetadas: {cur.rowcount}"]

    except Exception as e:
        return [f"Erro ao executar a query: {e}"]
    finally:
        if conn:
            conn.close()

# 3. Criar a Ferramenta LangChain
sql_tool = Tool(
    name="DatabaseQueryTool",
    func=execute_sql_query,
    description="""
    Use esta ferramenta para executar uma consulta SQL em um banco de dados PostgreSQL.
    A entrada para esta ferramenta deve ser uma consulta SQL completa e válida.
    A ferramenta retornará uma lista de resultados da consulta.
    Use-a sempre que precisar obter ou modificar dados no banco de dados para responder a uma pergunta.
    Exemplos de perguntas que exigem esta ferramenta:
    - Quantos usuários existem?
    - Qual é o email do usuário com ID 123?
    - Liste os 5 produtos mais recentes.
    """
)

tools = [sql_tool]

# 4. Inicializar o LLM
load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# 5. Criar o Agente
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 6. Loop Principal
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
