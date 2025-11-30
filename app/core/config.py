# app/core/config.py
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env que está na raiz do projeto
load_dotenv()

# --- Configuração de Conexão Direta ao Banco de Dados (para leitura/SQL) ---
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

# Validação para garantir que as variáveis de conexão direta foram carregadas
DATABASE_VARS = [DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT]
if not all(DATABASE_VARS):
    raise ValueError("Erro: As variáveis para conexão direta com o banco (DB_HOST, etc.) não estão definidas no .env.")

# URL do banco de dados para o LangChain SQL Agent (leitura)
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Configuração da API do Supabase (para escrita) ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validação para garantir que as variáveis da API do Supabase foram carregadas
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Erro: SUPABASE_URL ou SUPABASE_KEY não estão definidas no .env.")

# --- Configuração das Chaves de API dos LLMs ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validação para garantir que pelo menos uma chave de API de LLM foi fornecida
if not OPENAI_API_KEY and not GOOGLE_API_KEY:
    raise ValueError("Erro: Nenhuma chave de API de LLM (OPENAI_API_KEY ou GOOGLE_API_KEY) foi definida no .env.")