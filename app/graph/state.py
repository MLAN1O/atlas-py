from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator


class GraphState(TypedDict):
    """
    Representa o estado do nosso grafo.

    Atributos:
        input: A entrada do usuário.
        messages: O histórico da conversa.
        current_date: A data atual para o contexto do agente.
        intermediate_steps: A lista de passos intermediários (ações e observações de ferramentas).
    """
    input: str
    messages: Annotated[List[BaseMessage], operator.add]
    current_date: str
    intermediate_steps: list
