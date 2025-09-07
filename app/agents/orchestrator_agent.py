# app/agents/orchestrator_agent.py
from typing import List
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable

# Importa o prompt que define a lógica do orquestrador
from app.prompts.orchestrator_prompts import OrchestratorPrompt

def create_orchestrator_agent_executor(
    llm: BaseLanguageModel,
    sql_agent_executor: AgentExecutor,
    entry_agent_executor: AgentExecutor,
    report_chain: Runnable
) -> AgentExecutor:
    """
    Cria o Agente Orquestrador principal.

    Este agente recebe os outros agentes/chains como ferramentas e usa um prompt
    especializado para orquestrar o fluxo de trabalho.

    Args:
        llm: O modelo de linguagem a ser usado pelo orquestrador.
        sql_agent_executor: O agente SQL (para leitura).
        entry_agent_executor: O agente de entrada (para escrita).
        report_chain: A chain de formatação de relatório.

    Returns:
        O executor do Agente Orquestrador.
    """

    # 1. Cria as ferramentas para o Orquestrador.
    # Cada ferramenta é um dos sub-agentes. O nome da ferramenta é crucial,
    # pois é como o prompt se refere a ela.
    tools: List[Tool] = [
        Tool(
            name="SQLQueryTool",
            func=sql_agent_executor.invoke,
            description="Use for any questions about reading or querying data from the database. Input should be a user's natural language question."
        ),
        Tool(
            name="WriteExecutionTool",
            func=entry_agent_executor.invoke,
            description="Use for any operation that writes to the database, including INSERT, UPDATE, or DELETE. The input must be a dictionary specifying the operation details."
        ),
        Tool(
            name="ReportFormattingTool",
            func=report_chain.invoke,
            description="Use at the end to format the final response. Input must be a dictionary with 'user_intent' and 'operation_result'."
        ),
    ]

    # 2. Cria o agente orquestrador usando o prompt e as ferramentas.
    agent = create_openai_tools_agent(
        llm=llm, 
        tools=tools, 
        prompt=OrchestratorPrompt
    )

    # 3. Cria e retorna o executor do agente.
    print("Criando executor do Agente Orquestrador...")
    orchestrator = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True
    )
    print("Executor do Agente Orquestrador criado.")

    return orchestrator
