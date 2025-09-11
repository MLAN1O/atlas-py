# app/agents/orchestrator_agent.py
from typing import List, Any
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable
from pydantic.v1 import BaseModel, Field


# Importa o prompt que define a lógica do orquestrador
from app.prompts.orchestrator_prompts import OrchestratorPrompt
# Importa as novas ferramentas de negócio
from app.tools.business_tools import business_toolkit

# Define o schema de entrada para a ReportFormattingTool
class ReportToolInput(BaseModel):
    user_intent: str = Field(description="The user's original request or intent.")
    operation_result: str = Field(description="The result of the previous tool's operation.")

def create_orchestrator_agent_executor(
    llm: BaseLanguageModel,
    sql_agent_executor: AgentExecutor,
    report_chain: Runnable,
    current_date: str,
    memory: Any
) -> AgentExecutor:
    """
    Cria o Agente Orquestrador principal.
    """

    # Formata o prompt do orquestrador com a data atual
    formatted_prompt = OrchestratorPrompt.partial(current_date=current_date)

    # Função adaptadora para a ferramenta de relatório.
    def report_chain_wrapper(user_intent: str, operation_result: str):
        return report_chain.invoke({
            "user_intent": user_intent,
            "operation_result": operation_result
        })

    # 1. Cria as ferramentas para o Orquestrador.
    # Ferramenta de leitura (SQL)
    sql_tool = Tool(
        name="SQLQueryTool",
        func=sql_agent_executor.invoke,
        description="Use for any questions about reading or querying data from the database. Input should be a user's natural language question."
    )
    
    # Ferramenta de formatação de relatório
    report_tool = StructuredTool(
        name="ReportFormattingTool",
        func=report_chain_wrapper,
        description="Use at the end to format the final response. This tool requires specific arguments.",
        args_schema=ReportToolInput
    )

    # Combina todas as ferramentas: leitura, escrita (negócio) e formatação
    all_tools = business_toolkit + [sql_tool, report_tool]

    # 2. Cria o agente orquestrador.
    agent = create_openai_tools_agent(
        llm=llm, 
        tools=all_tools, 
        prompt=formatted_prompt
    )

    # 3. Cria e retorna o executor do agente.
    print("Criando executor do Agente Orquestrador...")
    orchestrator = AgentExecutor(
        agent=agent, 
        tools=all_tools, 
        verbose=True,
        memory=memory,
        handle_parsing_errors=True
    )
    print("Executor do Agente Orquestrador criado.")

    return orchestrator
