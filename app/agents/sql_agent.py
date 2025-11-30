# app/agents/sql_agent.py
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseLanguageModel

def create_sql_agent_graph(llm: BaseLanguageModel, db: SQLDatabase):
    """
    Cria um agente SQL usando LangGraph (create_react_agent).

    Args:
        llm (BaseLanguageModel): O modelo de linguagem.
        db (SQLDatabase): O banco de dados.

    Returns:
        CompiledGraph: O grafo do agente SQL.
    """
    
    # 1. Cria o toolkit SQL para obter as ferramentas
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    # 2. Define o System Prompt
    system_message = SystemMessage(content='''
IMPORTANT: You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct SQL query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST NOT use any markdown formatting in the SQL query itself (e.g., ```sql ... ```).
The SQL query must be a single, raw string passed to the tool.
''')

    print(f"Criando agente SQL (LangGraph) com o modelo: {llm.name if hasattr(llm, 'name') else 'LLM'}")

    # 3. Cria o agente usando a função pré-construída do LangGraph
    # create_react_agent já configura o grafo, o nó de ferramentas e o loop.
    graph = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_message
    )

    print("Grafo do agente SQL criado com sucesso.")
    return graph
