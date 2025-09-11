# app/agents/report_agent.py
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser

def create_report_chain(llm: BaseLanguageModel) -> Runnable:
    """
    Cria uma LangChain Chain (Runnable) para formatar os resultados finais.

    Esta chain recebe a intenção original do usuário e o resultado da operação
    e formata uma resposta amigável em Markdown.

    Args:
        llm (BaseLanguageModel): O modelo de linguagem a ser usado.

    Returns:
        Runnable: A chain de formatação de relatório.
    """

    # O prompt é a instrução principal para o LLM. 
    # Ele contém o papel do agente, a tarefa, um exemplo claro do formato desejado,
    # e os dados de entrada (variáveis `user_intent` e `operation_result`).
    prompt_template = """
Você é um assistente de comunicação prestativo. Sua única tarefa é pegar o resultado de uma operação de banco de dados e a intenção original do usuário, e formatar uma resposta clara, completa e amigável em Markdown para ser enviada por um chat.

**Exemplo de Resposta Perfeita:**
> ✅ **Despesa Registrada com Sucesso!**
>
> Com base no seu pedido e no histórico de lançamentos, registrei a despesa com os seguintes detalhes:
>
>   * **Data:** `06/09/2025`
>   * **Descrição:** `Combustível`
>   * **Valor:** `R$ 200,00`
>   * **Categoria:** `Frota / Veículos Leves` (Classe: Variável)

--- 

**DADOS RECEBIDOS PARA O RELATÓRIO:**

*   **Intenção Original do Usuário:** "{user_intent}"
*   **Resultado da Operação (em formato JSON):** "{operation_result}"

--- 

**SUA RESPOSTA (APENAS O MARKDOWN FINAL):**
"""

    prompt = ChatPromptTemplate.from_template(prompt_template)

    # Uma "chain" em LangChain é uma sequência de componentes. 
    # Esta é uma chain simples:
    # 1. `prompt`: Formata a entrada do usuário no template de prompt.
    # 2. `llm`: Envia o prompt formatado para o modelo de linguagem.
    # 3. `StrOutputParser`: Extrai apenas o conteúdo de texto da resposta do LLM.
    chain = prompt | llm | StrOutputParser()

    print("Chain de relatório criada.")
    return chain
