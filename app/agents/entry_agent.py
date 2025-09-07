# app/agents/entry_agent.py
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.language_models import BaseLanguageModel
from langchain.tools import StructuredTool
from langchain import hub # Importa o hub para puxar prompts

# Importa o conjunto completo de ferramentas de escrita
from app.tools.supabase_tools import insert_record, update_record, delete_record

def create_entry_agent_executor(llm: BaseLanguageModel) -> AgentExecutor:
    """
    Cria um executor de agente focado em todas as operações de escrita:
    inserir, atualizar e deletar registros.
    """
    # 1. Define o conjunto completo de ferramentas que o agente poderá usar.
    tools = [
        StructuredTool.from_function(
            func=insert_record,
            name="InsertRecordTool",
            description="Use para inserir um novo registro em uma tabela. Forneça o nome da tabela e o registro (dicionário de dados) a ser inserido."
        ),
        StructuredTool.from_function(
            func=update_record,
            name="UpdateRecordTool",
            description="Use para atualizar um registro existente em uma tabela. Forneça o nome da tabela, o ID do registro e um dicionário com os campos a serem atualizados."
        ),
        StructuredTool.from_function(
            func=delete_record,
            name="DeleteRecordTool",
            description="Use para deletar um registro de uma tabela. Forneça o nome da tabela e o ID do registro a ser deletado."
        ),
    ]

    # 2. Puxa o prompt padrão e oficial para este tipo de agente do LangChain Hub.
    # Este prompt é projetado para funcionar corretamente com `create_structured_chat_agent`.
    prompt = hub.pull("hwchase17/structured-chat-agent")

    # 3. Cria o agente com o LLM, as ferramentas e o prompt correto.
    agent = create_structured_chat_agent(llm, tools, prompt)

    # 4. Retorna o AgentExecutor.
    print("Criando executor do Entry Agent com poderes de Insert, Update e Delete...")
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True
    )
    print("Executor do Entry Agent criado.")
    
    return agent_executor