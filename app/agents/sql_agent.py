# app/agents/sql_agent.py
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseLanguageModel

def create_sql_agent_executor(llm: BaseLanguageModel, db: SQLDatabase):
    """
    Cria um executor de agente SQL.

    Args:
        llm (BaseLanguageModel): O modelo de linguagem a ser usado pelo agente.
        db (SQLDatabase): A conexão do banco de dados LangChain.

    Returns:
        AgentExecutor: O agente SQL criado.
    """
    # Mensagem do sistema para instruir o LLM a não usar Markdown na query
    prompt_message = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=[],
            template='''
IMPORTANT: When providing a SQL query, you MUST NOT use any markdown formatting.
The SQL query must be a single, raw string. For example:
SELECT * FROM users;'''
        )
    )

    print(f"Criando agente SQL com o modelo: {llm.__class__.__name__}")

    # Nota: O agent_type pode variar dependendo do modelo.
    # Para os modelos mais recentes da OpenAI e Google, não especificar o agent_type
    # geralmente permite que o LangChain escolha a melhor abordagem (tool calling).
    # Para outros, como `AgentType.OPENAI_FUNCTIONS`, pode ser necessário.
    # Vamos manter a lógica flexível.
    
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        # agent_type=AgentType.OPENAI_FUNCTIONS, # Opcional, dependendo do LLM
        verbose=True,
        extra_prompt_messages=[prompt_message]
    )

    print("Executor do agente SQL criado com sucesso.")
    return agent_executor
