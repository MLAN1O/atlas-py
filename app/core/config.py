# app/core/config.py
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env que está na raiz do projeto
# A função find_dotenv() localiza o arquivo .env automaticamente
load_dotenv()

# --- Configuração do Banco de Dados ---
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

# Validação para garantir que as variáveis do banco de dados foram carregadas
DATABASE_VARS = [DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT]
if not all(DATABASE_VARS):
    raise ValueError("Erro: Uma ou mais variáveis de ambiente do banco de dados (DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT) não estão definidas. Verifique seu arquivo .env.")

# Constrói a URL do banco de dados para o LangChain
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Configuração das Chaves de API ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validação para garantir que pelo menos uma chave de API foi fornecida
if not OPENAI_API_KEY and not GOOGLE_API_KEY:
    raise ValueError("Erro: Nenhuma chave de API (OPENAI_API_KEY ou GOOGLE_API_KEY) foi definida. Verifique seu arquivo .env.")
