# app/agents/orchestrator_agent.py
from typing import List
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable
from pydantic.v1 import BaseModel, Field

# Importa o prompt que define a lógica do orquestrador
from app.prompts.orchestrator_prompts import OrchestratorPrompt

# Define o schema de entrada para a ReportFormattingTool
class ReportToolInput(BaseModel):
    user_intent: str = Field(description="The user's original request or intent.")
    operation_result: str = Field(description="The result of the previous tool's operation.")

def create_orchestrator_agent_executor(
    llm: BaseLanguageModel,
    sql_agent_executor: AgentExecutor,
    entry_agent_executor: AgentExecutor,
    report_chain: Runnable
) -> AgentExecutor:
    """
    Cria o Agente Orquestrador principal.
    """

    # Função adaptadora para a ferramenta de relatório.
    # Ela recebe os argumentos da StructuredTool e os formata no dicionário
    # que a report_chain.invoke espera.
    def report_chain_wrapper(user_intent: str, operation_result: str):
        return report_chain.invoke({
            "user_intent": user_intent,
            "operation_result": operation_result
        })

    # 1. Cria as ferramentas para o Orquestrador.
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
        StructuredTool(
            name="ReportFormattingTool",
            func=report_chain_wrapper, # Usa a função adaptadora
            description="Use at the end to format the final response. This tool requires specific arguments.",
            args_schema=ReportToolInput
        ),
    ]

    # 2. Cria o agente orquestrador.
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
