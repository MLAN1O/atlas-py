# app/tools/supabase_tools.py
from langchain_community.utilities import SQLDatabase
from app.core.config import DATABASE_URL

def get_database_connection():
    """
    Inicializa e retorna uma conexão com o banco de dados usando a URL configurada.

    Returns:
        SQLDatabase: Uma instância de SQLDatabase conectada ao banco de dados.
    """
    try:
        print("Estabelecendo conexão com o banco de dados...")
        db = SQLDatabase.from_uri(DATABASE_URL)
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return db
    except Exception as e:
        print(f"Erro fatal ao conectar ao banco de dados: {e}")
        print("Verifique a string de conexão e as credenciais no seu arquivo .env")
        # Em uma aplicação real, você poderia querer um tratamento de erro mais robusto,
        # mas para este caso, sair é uma opção segura.
        raise

# Nota sobre o entry_agent:
# No futuro, este arquivo também conterá as funções de escrita para o `entry_agent`.
# Por exemplo:
#
# def insert_expense(data: dict):
#     # Lógica para usar o cliente do Supabase e inserir um novo registro
#     print(f"Inserindo despesa: {data}")
#     # ... código de inserção ...
#     return result
