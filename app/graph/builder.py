# app/graph/builder.py
import operator
from typing import Annotated, Sequence

from langchain_core.agents import AgentFinish
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.tools import Tool
from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from .state import GraphState


def should_continue(state: GraphState) -> str:
    """Decide se o grafo deve continuar ou terminar."""
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    return "tools"

def agent_node(state: GraphState, agent: Runnable, name: str):
    """Executa o nó do agente e retorna a resposta como uma mensagem AI."""
    result = agent.invoke(state)
    
    if isinstance(result, AgentFinish):
        content = result.return_values.get("output", "") 
        return {"messages": [AIMessage(content=content)]}

    actions = result if isinstance(result, list) else [result]
    tool_calls = [
        {
            "name": action.tool,
            "args": action.tool_input,
            "id": action.tool_call_id,
        }
        for action in actions
    ]
    
    return {"messages": [AIMessage(content="", tool_calls=tool_calls)]}

def create_graph_with_persistence(agent_runnable: Runnable, tools: Sequence[Tool], checkpointer):
    """
    Cria e compila o grafo com persistência.
    """
    workflow = StateGraph(GraphState)

    workflow.add_node("agent", lambda state: agent_node(state, agent_runnable, "agent"))

    tool_node = ToolNode(tools)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    workflow.add_edge("tools", "agent")

    graph = workflow.compile(checkpointer=checkpointer)
    print("Grafo compilado com persistência.")
    
    return graph
