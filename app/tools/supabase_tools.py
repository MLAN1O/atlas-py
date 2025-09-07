# app/tools/supabase_tools.py
import traceback
from langchain_community.utilities import SQLDatabase
from app.core.config import DATABASE_URL, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client
from typing import Dict, Any

# --- Ferramenta de Leitura (para SQL Agent) ---

def get_database_connection():
    """
    Inicializa e retorna uma conexão de banco de dados LangChain para consultas SQL.
    """
    try:
        print("Estabelecendo conexão SQL (leitura)...")
        db = SQLDatabase.from_uri(DATABASE_URL)
        print("Conexão SQL (leitura) estabelecida.")
        return db
    except Exception as e:
        print(f"Erro fatal ao conectar via SQL: {e}")
        raise

# --- Ferramentas de Escrita (para Entry Agent) ---

# Inicializa o cliente da API do Supabase
try:
    print("Inicializando cliente da API do Supabase (escrita)...")
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Cliente da API do Supabase inicializado.")
except Exception as e:
    print(f"Erro fatal ao inicializar o cliente Supabase: {e}")
    raise

def insert_record(table_name: str, record: Dict[str, Any]) -> str:
    """
    Insere um único registro em uma tabela específica no Supabase.
    """
    try:
        print(f"Inserindo registro na tabela '{table_name}': {record}")
        data, count = supabase_client.table(table_name).insert(record).execute()
        
        print(f"Raw data from Supabase: {data}")
        print(f"Raw count from Supabase: {count}")

        if count > 0 and len(data) > 1 and data[1]:
            return f"Registro inserido com sucesso: {data[1][0]}"
        else:
            return "A operação de inserção foi executada, mas não retornou os dados esperados (verifique a RLS)."
    except Exception as e:
        traceback.print_exc() # Imprime o traceback completo
        return f"Falha ao inserir registro. Erro: {e}"

def update_record(table_name: str, record_id: Any, updates: Dict[str, Any]) -> str:
    """
    Atualiza um registro específico em uma tabela com base em seu ID.
    """
    try:
        print(f"Atualizando registro ID '{record_id}' na tabela '{table_name}' com os dados: {updates}")
        data, count = supabase_client.table(table_name).update(updates).eq('id', record_id).execute()
        if count > 0 and len(data) > 1 and data[1]:
            return f"Registro ID '{record_id}' atualizado com sucesso: {data[1][0]}"
        else:
            return f"Nenhum registro encontrado com o ID '{record_id}' para atualizar."
    except Exception as e:
        traceback.print_exc() # Imprime o traceback completo
        return f"Falha ao atualizar o registro ID '{record_id}'. Erro: {e}"

def delete_record(table_name: str, record_id: Any) -> str:
    """
    Deleta um registro específico em uma tabela com base em seu ID.
    """
    try:
        print(f"Deletando registro ID '{record_id}' da tabela '{table_name}'...")
        data, count = supabase_client.table(table_name).delete().eq('id', record_id).execute()
        if count > 0 and len(data) > 1 and data[1]:
            return f"Registro ID '{record_id}' deletado com sucesso: {data[1][0]}"
        else:
            return f"Nenhum registro encontrado com o ID '{record_id}' para deletar."
    except Exception as e:
        traceback.print_exc() # Imprime o traceback completo
        return f"Falha ao deletar o registro ID '{record_id}'. Erro: {e}"