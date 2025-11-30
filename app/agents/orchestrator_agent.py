# app/agents/orchestrator_agent.py
from typing import List, Tuple
from langchain.agents import Tool, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

# Importa o prompt que define a lógica do orquestrador
from app.prompts.orchestrator_prompts import OrchestratorPrompt
# Importa as novas ferramentas de negócio
from app.tools.business_tools import business_toolkit

# Define o schema de entrada para a ReportFormattingTool
class ReportToolInput(BaseModel):
    user_intent: str = Field(description="The user's original request or intent.")
    operation_result: str = Field(description="The result of the previous tool's operation.")

def create_orchestrator_agent_runnable(
    llm: BaseLanguageModel,
    sql_agent_graph: Runnable,
    report_chain: Runnable,
) -> Tuple[Runnable, List[Tool]]:
    """
    Cria o agente orquestrador e as ferramentas que ele pode usar.
    Retorna uma tupla contendo o agente executável e a lista de ferramentas.
    """

    # Função adaptadora para a ferramenta de relatório.
    def report_chain_wrapper(user_intent: str, operation_result: str):
        return report_chain.invoke({
            "user_intent": user_intent,
            "operation_result": operation_result
        })

    # Função adaptadora para o agente SQL (LangGraph)
    def sql_agent_wrapper(query: str):
        # O grafo espera um estado com 'messages'
        result = sql_agent_graph.invoke({"messages": [HumanMessage(content=query)]})
        # O resultado é o estado final. A resposta do agente está na última mensagem.
        return result["messages"][-1].content

    # 1. Cria as ferramentas para o Orquestrador.
    sql_tool = Tool(
        name="SQLQueryTool",
        func=sql_agent_wrapper,
        description="Use for any questions about reading or querying data from the database. Input should be a user's natural language question."
    )
    
    report_tool = StructuredTool(
        name="ReportFormattingTool",
        func=report_chain_wrapper,
        description="Use at the end to format the final response. This tool requires specific arguments.",
        args_schema=ReportToolInput
    )

    # Combina todas as ferramentas
    all_tools = business_toolkit + [sql_tool, report_tool]

    # 2. Cria o agente orquestrador executável.
    # O prompt será preenchido com a data atual no grafo.
    agent_runnable = create_openai_tools_agent(
        llm=llm, 
        tools=all_tools, 
        prompt=OrchestratorPrompt
    )

    print("Agente orquestrador e ferramentas criados.")
    return agent_runnable, all_tools