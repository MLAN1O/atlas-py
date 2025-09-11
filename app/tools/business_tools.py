# app/tools/business_tools.py
from datetime import date
from langchain_core.tools import tool
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# Importa as funções genéricas que já existem e funcionam
from .supabase_tools import insert_record, update_record, delete_record, supabase_client

# --- Modelos de Dados de Negócio (Validação Automática) ---
class CustoInput(BaseModel):
    """Modelo para registrar um novo custo. Espelha a estrutura da tabela 'custos'."""
    data: str = Field(description="Data do custo no formato AAAA-MM-DD")
    descricao: str = Field(description="Descrição detalhada do que foi o custo")
    total: float = Field(description="O valor total do custo. Este campo é obrigatório.")
    
    # Mapeamento para as colunas reais e opcionais do banco de dados
    classe: str | None = Field(None, description="A classe do custo, ex: 'custo operacional'")
    categoria: str | None = Field(None, description="A categoria principal do custo, ex: 'Transporte'")
    sub_categoria: str | None = Field(None, description="A subcategoria específica, ex: 'combustivel'")
    quantidade: float | None = Field(None, description="A quantidade de itens, se aplicável")
    preco_unitario: float | None = Field(None, description="O preço por unidade, se aplicável")
    beneficiario: str | None = Field(None, description="Para quem ou onde o pagamento foi feito")
    forma_pagamento: str | None = Field(None, description="Método de pagamento, ex: 'Dinheiro', 'Pix'")
    lote: str | None = Field(None, description="Lote associado ao custo, se houver")
    observacoes: str | None = Field(None, description="Qualquer observação adicional")

class VendaInput(BaseModel):
    """Modelo para registrar uma nova venda. Espelha a estrutura da tabela 'vendas'."""

    # Campos obrigatórios (NOT NULL)
    data: str = Field(description="Data da venda no formato AAAA-MM-DD")
    cliente: str = Field(description="Nome ou identificação do cliente")
    estabelecimento: str = Field(
        "", description="Nome ou código do estabelecimento onde a venda ocorreu (use '' se não houver)"
    )
    produto: Literal["Caranha", "Pintado"] = Field(description="Produto vendido: 'Caranha' ou 'Pintado'")
    tipo_produto: Literal["cortado", "cortada", "inteiro", "inteira", "cabeça", "retalho"] = Field(
        description="Tipo do produto: 'cortado/a', 'inteiro/a', 'cabeça' ou 'retalho'"
    )
    quantidade_kg: float = Field(description="Quantidade vendida em quilogramas (> 0)")
    preco_por_kg: float = Field(description="Preço unitário por quilograma (> 0)")
    total: float = Field(description="Valor total da venda (quantidade_kg * preco_por_kg)")
    status_venda: Literal["pago", "doacao", "pendente"] = Field(
        description="Situação da venda: 'pago', 'doacao' ou 'pendente'"
    )
    lote: str = Field(description="Identificação do lote ao qual a venda está vinculada")

    # Campos opcionais
    forma_pagamento: Optional[str] = Field(
        None, description="Método de pagamento (ex.: 'Dinheiro', 'Pix', 'Cartão débito')"
    )
    observacao: Optional[str] = Field(None, description="Observação livre sobre a venda")

class AbateInput(BaseModel):
    """Modelo para registrar um novo abate. Espelha a estrutura da tabela 'abates'."""

    # Campos obrigatórios (NOT NULL)
    data: str = Field(description="Data do abate no formato AAAA-MM-DD")
    especie: str = Field(description="Espécie do peixe abatido")
    lote: str = Field(description="Código do lote associado ao abate")
    quantidade_peixes: int = Field(description="Número de peixes abatidos (deve ser > 0)")
    quantidade_kg: Decimal = Field(description="Peso total abatido em kg (deve ser > 0)")
    tanque_gaiola: str = Field(description="Tanque ou gaiola onde ocorreu o abate")
    peso_medio: Decimal = Field(description="Peso médio por peixe (kg, deve ser > 0)")

    # Campo opcional
    observacao: str | None = Field(None, description="Observação livre sobre o abate")

# --- Toolkit de Ferramentas de Negócio ---
@tool
def registrar_custo(custo: CustoInput) -> str:
    """
    Use esta ferramenta para registrar uma nova despesa ou custo no sistema.
    """
    # Usa .model_dump(exclude_none=True) para enviar ao Supabase apenas os campos que foram preenchidos pelo LLM.
    record_dict = custo.model_dump(exclude_none=True)
    table_name = "custos"
    return insert_record(table_name=table_name, record=record_dict)

@tool
def registrar_venda(venda: VendaInput) -> str:
    """
    Use esta ferramenta para registrar uma nova venda de peixes no sistema.
    """
    record_dict = venda.model_dump(exclude_none=True)
    table_name = "vendas" # Lógica de negócio encapsulada.
    # AQUI poderíamos adicionar validações extras antes de chamar insert_record
    return insert_record(table_name=table_name, record=record_dict)

@tool
def registrar_abate(abate: AbateInput) -> str:
    """
    Use esta ferramenta para registrar um novo abate de peixes no sistema.
    """
    record_dict = abate.model_dump(exclude_none=True)
    table_name = "abates"
    return insert_record(table_name=table_name, record=record_dict)

# Exemplo de ferramenta de UPDATE
@tool
def atualizar_status_abate(id_abate: int, novo_status: str) -> str:
    """Use esta ferramenta para atualizar o status de um abate específico."""
    table_name = "abates"
    updates = {"status": novo_status}
    return update_record(table_name=table_name, record_id=id_abate, updates=updates)

# --- NOVAS FERRAMENTAS DE BUSCA PROATIVA ---
@tool
def buscar_custos_similares(termo_busca: str) -> dict | None:
    """Busca o registro de custo mais recente e completo semelhante ao termo_busca para preenchimento automático."""
    try:
        response = supabase_client.table('custos').select('*') \
            .or_(f'descricao.ilike.%{termo_busca}%,categoria.ilike.%{termo_busca}%') \
            .order('data', desc=True).limit(1).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        return {"error": f"Erro ao buscar custos similares: {str(e)}"}

@tool
def buscar_vendas_similares(cliente: str = "", estabelecimento: str = "") -> list[dict] | None:
    """
    Busca até 3 vendas mais recentes cujo cliente ou estabelecimento seja semelhante aos parâmetros.
    """
    try:
        query = supabase_client.table('vendas').select('*')

        # Aplicar filtros somente se vierem valores
        filtros = []
        if cliente:
            filtros.append(f"cliente.ilike.%{cliente}%")
        if estabelecimento:
            filtros.append(f"estabelecimento.ilike.%{estabelecimento}%")

        if filtros:
            # Se houver mais de um filtro, usar OR
            query = query.or_(",".join(filtros)) if len(filtros) > 1 else query.ilike(
                "cliente" if cliente else "estabelecimento", filtros[0].split(".ilike.")[1].strip("%")
            )

        response = query.order('data', desc=True).limit(3).execute()
        return response.data if response.data else None

    except Exception as e:
        return {"error": f"Erro ao buscar vendas similares: {str(e)}"}


@tool
def buscar_abates_similares(id_lote: int = None) -> dict | None:
    """Busca o abate mais recente, opcionalmente filtrando por lote, para inferir padrões."""
    try:
        query = supabase_client.table('abates').select('*')
        if id_lote:
            query = query.eq('id_lote', id_lote)
        
        response = query.order('data_abate', desc=True).limit(1).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        return {"error": f"Erro ao buscar abates similares: {str(e)}"}


# Criar uma lista com todas as ferramentas para fácil importação pelo Orquestrador
business_toolkit: List[callable] = [
    registrar_custo,
    registrar_venda,
    registrar_abate,
    atualizar_status_abate,
    buscar_custos_similares,
    buscar_vendas_similares,
    buscar_abates_similares,
]
