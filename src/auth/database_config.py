# CryptoNinja 🥷 - Configuração do Banco PostgreSQL
# 
# INSTRUÇÕES DE CONFIGURAÇÃO:
# 
# 1. Instalar PostgreSQL:
#    - Windows: https://www.postgresql.org/download/windows/
#    - Criar banco de dados: cryptoninja_db
#    - Usuario padrão: postgres
#    - Senha padrão: admin
# 
# 2. Criar banco de dados:
#    psql -U postgres
#    CREATE DATABASE cryptoninja_db;
# 
# 3. Configurar variáveis de ambiente (opcional):
#    DATABASE_URL=postgresql://postgres:admin@localhost:5432/cryptoninja_db
#    SECRET_KEY=cryptoninja-secret-key-2025
# 
# 4. Instalar dependências Python:
#    pip install psycopg2-binary flask-login flask-bcrypt flask-sqlalchemy
# 
# 5. Inicializar banco (automático na primeira execução):
#    python main.py
# 
# CREDENCIAIS PADRÃO:
# - Usuario: admin
# - Senha: ninja123
# 
# ⚠️ IMPORTANTE: Altere a senha padrão após o primeiro login!
# 
# COMANDOS ÚTEIS PostgreSQL:
# 
# Conectar ao banco:
# psql -U postgres -d cryptoninja_db
# 
# Listar tabelas:
# \dt
# 
# Ver usuários:
# SELECT * FROM users;
# 
# Resetar senha admin:
# UPDATE users SET password_hash = '$2b$12$exemplo_hash_aqui' WHERE username = 'admin';
# 
# Backup do banco:
# pg_dump -U postgres cryptoninja_db > backup.sql
# 
# Restaurar backup:
# psql -U postgres cryptoninja_db < backup.sql

# Configurações do Flask para PostgreSQL
FLASK_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:admin@localhost:5432/cryptoninja_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': 'cryptoninja-secret-key-2025',
    'PERMANENT_SESSION_LIFETIME': 86400,  # 24 horas em segundos
}

# Configurações de segurança
SECURITY_CONFIG = {
    'PASSWORD_MIN_LENGTH': 6,
    'SESSION_TIMEOUT_HOURS': 24,
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION_MINUTES': 15,
}

# Configurações iniciais do usuário
DEFAULT_USER_CONFIG = {
    'INITIAL_BALANCE': 10000.0,
    'DEFAULT_ADMIN_USERNAME': 'admin',
    'DEFAULT_ADMIN_EMAIL': 'admin@cryptoninja.com',
    'DEFAULT_ADMIN_PASSWORD': 'ninja123',  # ⚠️ ALTERE APÓS PRIMEIRO LOGIN!
}

# SQL para criação manual das tabelas (se necessário)
CREATE_TABLES_SQL = """
-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    balance FLOAT DEFAULT 10000.0,
    total_trades INTEGER DEFAULT 0,
    total_pnl FLOAT DEFAULT 0.0
);

-- Tabela de sessões
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);

-- Inserir usuário admin padrão (se não existir)
INSERT INTO users (username, email, password_hash, is_admin)
SELECT 'admin', 'admin@cryptoninja.com', '$2b$12$exemplo_hash_aqui', TRUE
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');
"""

print("🥷 CryptoNinja - Configuração PostgreSQL carregada")
print("📖 Leia as instruções acima para configurar o banco de dados")
