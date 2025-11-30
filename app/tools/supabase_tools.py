# app/tools/supabase_tools.py
from langchain_community.utilities import SQLDatabase
from app.core.config import DATABASE_URL, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client
from typing import Dict, Any, List

# --- Configuração do Cliente Supabase ---

try:
    print("Inicializando cliente da API do Supabase...")
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Cliente da API do Supabase inicializado.")
except Exception as e:
    print(f"Erro fatal ao inicializar o cliente Supabase: {e}")
    raise

# --- Funções de Metadados ---

def get_all_table_names() -> List[str]:
    """Busca e retorna os nomes das tabelas visíveis no schema 'public'."""
    try:
        logger.info("Buscando esquemas de tabelas via RPC...")
        response = supabase_client.rpc('get_table_names', {}).execute()
        if response.data:
            table_names = [item['table_name'] for item in response.data]
            logger.info(f"Tabelas encontradas: {table_names}")
            return table_names
        else:
            logger.warning("RPC sem retorno. Usando lista de fallback.")
    except Exception as e:
        logger.error(f"Erro ao buscar nomes das tabelas: {e}")

    # Fallback final
    return ["custos", "vendas", "abates"]


# --- Ferramenta de Leitura (para SQL Agent) ---

def get_database_connection():
    """
    Inicializa e retorna uma conexão de banco de dados LangChain, 
    incluindo o esquema de todas as tabelas disponíveis.
    """
    try:
        print("Estabelecendo conexão SQL (leitura)...")
        table_names = get_all_table_names()
        db = SQLDatabase.from_uri(DATABASE_URL, include_tables=table_names)
        print("Conexão SQL (leitura) estabelecida com esquemas.")
        return db
    except Exception as e:
        print(f"Erro fatal ao conectar via SQL: {e}")
        raise

# app/tools/supabase_tools.py
import psycopg2
import logging
from langchain_community.utilities import SQLDatabase
from app.core.config import (
    DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, 
    DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
)
from supabase import create_client, Client
from typing import Dict, Any, List

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuração do Cliente Supabase ---

try:
    logger.info("Inicializando cliente da API do Supabase...")
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Cliente da API do Supabase inicializado.")
except Exception as e:
    logger.error(f"Erro fatal ao inicializar o cliente Supabase: {e}")
    raise

# --- Funções de Metadados ---

def get_all_table_names() -> List[str]:
    """
    Busca e retorna uma lista com os nomes de todas as tabelas base (excluindo views)
    visíveis no schema 'public' usando uma conexão SQL direta.
    """
    logger.info("Buscando esquemas de tabelas (excluindo views) via conexão SQL direta...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        cursor.close()
        conn.close()
        logger.info(f"Tabelas encontradas: {table_names}")
        return table_names
    except Exception as e:
        logger.error(f"Erro crítico ao buscar nomes de tabelas com SQL: {e}")
        raise

# --- Ferramenta de Leitura (para SQL Agent) ---

def get_database_connection():
    """
    Inicializa e retorna uma conexão de banco de dados LangChain.
    """
    try:
        logger.info("Estabelecendo conexão SQL (leitura)...")
        table_names = get_all_table_names()
        db = SQLDatabase.from_uri(DATABASE_URL, include_tables=table_names)
        logger.info("Conexão SQL (leitura) estabelecida com esquemas.")
        return db
    except Exception as e:
        logger.error(f"Erro fatal ao conectar via SQL: {e}")
        raise

# --- Ferramentas de Escrita (para Entry Agent) ---

def insert_record(table_name: str, record: Dict[str, Any]) -> str:
    """
    Insere um único registro em uma tabela específica no Supabase.
    """
    logger.info(f"Iniciando inserção na tabela '{table_name}' com o registro: {record}")
    try:
        response = supabase_client.table(table_name).insert(record).execute()
        logger.info(f"Resposta da API Supabase (insert): {response}")

        # Verificação robusta da resposta
        if response.data and len(response.data) > 0:
            # O Supabase retorna uma lista de registros inseridos. Pegamos o primeiro.
            inserted_record = response.data[0]
            return f"Registro inserido com sucesso: {inserted_record}"
        else:
            logger.warning(f"A operação de inserção na tabela '{table_name}' não retornou dados. Resposta: {response}")
            return "A operação de inserção foi executada, mas não retornou dados para confirmação."

    except StopIteration:
        logger.error("Erro de StopIteration capturado durante a inserção. Isso pode indicar um problema com o stream de resposta do Supabase.")
        return "Erro crítico: Ocorreu um StopIteration ao tentar inserir o registro."
    except Exception as e:
        logger.error(f"Falha ao inserir registro na tabela '{table_name}'. Erro: {e}")
        return f"Falha ao inserir registro. Erro: {e}"

def update_record(table_name: str, record_id: Any, updates: Dict[str, Any]) -> str:
    """
    Atualiza um registro específico em uma tabela com base em seu ID.
    """
    logger.info(f"Iniciando atualização na tabela '{table_name}' para o ID '{record_id}' com os dados: {updates}")
    try:
        response = supabase_client.table(table_name).update(updates).eq('id', record_id).execute()
        logger.info(f"Resposta da API Supabase (update): {response}")

        if response.data and len(response.data) > 0:
            updated_record = response.data[0]
            return f"Registro ID '{record_id}' atualizado com sucesso: {updated_record}"
        else:
            logger.warning(f"Nenhum registro encontrado com o ID '{record_id}' para atualizar na tabela '{table_name}'.")
            return f"Nenhum registro encontrado com o ID '{record_id}' para atualizar."

    except Exception as e:
        logger.error(f"Falha ao atualizar o registro ID '{record_id}'. Erro: {e}")
        return f"Falha ao atualizar o registro. Erro: {e}"

def delete_record(table_name: str, record_id: Any) -> str:
    """
    Deleta um registro específico em uma tabela com base em seu ID.
    """
    logger.info(f"Iniciando deleção na tabela '{table_name}' para o ID '{record_id}'...")
    try:
        response = supabase_client.table(table_name).delete().eq('id', record_id).execute()
        logger.info(f"Resposta da API Supabase (delete): {response}")

        if response.data and len(response.data) > 0:
            deleted_record = response.data[0]
            return f"Registro ID '{record_id}' deletado com sucesso: {deleted_record}"
        else:
            logger.warning(f"Nenhum registro encontrado com o ID '{record_id}' para deletar na tabela '{table_name}'.")
            return f"Nenhum registro encontrado com o ID '{record_id}' para deletar."

    except Exception as e:
        logger.error(f"Falha ao deletar o registro ID '{record_id}'. Erro: {e}")
        return f"Falha ao deletar o registro. Erro: {e}"

