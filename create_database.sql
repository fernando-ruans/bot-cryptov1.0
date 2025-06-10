-- =============================================
-- CryptoNinja Database - Script de Criacao Completa
-- Cria o banco e todas as tabelas do zero
-- =============================================

-- PARA POSTGRESQL LOCAL:
-- Execute como superuser (postgres):
-- psql -U postgres -f create_database.sql

-- PARA CLOUD (Heroku/Supabase):
-- Pule a criacao do banco, apenas execute as tabelas

-- =============================================
-- CRIAR BANCO DE DADOS (apenas local)
-- =============================================

-- Terminar conexoes existentes (se houver)
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'cryptoninja_db'
  AND pid <> pg_backend_pid();

-- Remover banco se existir
DROP DATABASE IF EXISTS cryptoninja_db;

-- Criar novo banco
CREATE DATABASE cryptoninja_db
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Conectar ao novo banco
\c cryptoninja_db;

-- =============================================
-- CRIAR EXTENSÕES
-- =============================================

-- Extensao para UUID (caso precise no futuro)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extensao para JSON (caso precise no futuro)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================
-- REMOVER TABELAS EXISTENTES (se houver)
-- =============================================

DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS system_logs CASCADE;
DROP TABLE IF EXISTS market_data CASCADE;
DROP TABLE IF EXISTS trades CASCADE;
DROP TABLE IF EXISTS signals CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =============================================
-- CRIAR TABELAS
-- =============================================

-- Tabela de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    balance DECIMAL(15,2) DEFAULT 10000.00,
    total_trades INTEGER DEFAULT 0,
    total_pnl DECIMAL(15,2) DEFAULT 0.00,
    
    -- Constraints
    CONSTRAINT users_username_check CHECK (LENGTH(username) >= 3),
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_balance_check CHECK (balance >= 0)
);

-- Tabela de sessoes de usuario
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT sessions_expires_check CHECK (expires_at > created_at)
);

-- Tabela de sinais de trading
CREATE TABLE signals (
    id VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('BUY', 'SELL')),
    confidence DECIMAL(5,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    entry_price DECIMAL(15,8) NOT NULL CHECK (entry_price > 0),
    stop_loss DECIMAL(15,8) CHECK (stop_loss > 0),
    take_profit DECIMAL(15,8) CHECK (take_profit > 0),
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'executed', 'cancelled', 'expired')),
    reasons TEXT,
    user_id INTEGER REFERENCES users(id)
);

-- Tabela de trades
CREATE TABLE trades (
    id VARCHAR(50) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    signal_id VARCHAR(50) REFERENCES signals(id),
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10) NOT NULL CHECK (trade_type IN ('BUY', 'SELL')),
    entry_price DECIMAL(15,8) NOT NULL CHECK (entry_price > 0),
    exit_price DECIMAL(15,8) CHECK (exit_price > 0),
    quantity DECIMAL(20,8) NOT NULL CHECK (quantity > 0),
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    stop_loss DECIMAL(15,8),
    take_profit DECIMAL(15,8),
    pnl DECIMAL(15,2),
    pnl_percent DECIMAL(8,4),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed', 'cancelled')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_timestamp TIMESTAMP,
    exit_reason VARCHAR(50)
);

-- Tabela de dados de mercado
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(15,8) NOT NULL CHECK (open_price > 0),
    high_price DECIMAL(15,8) NOT NULL CHECK (high_price > 0),
    low_price DECIMAL(15,8) NOT NULL CHECK (low_price > 0),
    close_price DECIMAL(15,8) NOT NULL CHECK (close_price > 0),
    volume DECIMAL(20,2) NOT NULL CHECK (volume >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint para validar OHLC
    CONSTRAINT market_data_ohlc_check CHECK (
        high_price >= open_price AND 
        high_price >= close_price AND 
        low_price <= open_price AND 
        low_price <= close_price
    )
);

-- Tabela de logs do sistema
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    module VARCHAR(100),
    function_name VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSONB
);

-- Tabela de notificacoes
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- CRIAR INDICES PARA PERFORMANCE
-- =============================================

-- Indices da tabela users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_admin ON users(is_admin);

-- Indices da tabela sessions
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_active ON user_sessions(is_active);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);

-- Indices da tabela signals
CREATE INDEX idx_signals_symbol ON signals(symbol);
CREATE INDEX idx_signals_user ON signals(user_id);
CREATE INDEX idx_signals_status ON signals(status);
CREATE INDEX idx_signals_timestamp ON signals(timestamp);

-- Indices da tabela trades
CREATE INDEX idx_trades_user ON trades(user_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_trades_signal ON trades(signal_id);

-- Indices da tabela market_data
CREATE INDEX idx_market_symbol_time ON market_data(symbol, timeframe, timestamp);
CREATE INDEX idx_market_timestamp ON market_data(timestamp);

-- Indices da tabela logs
CREATE INDEX idx_logs_level ON system_logs(level);
CREATE INDEX idx_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_logs_module ON system_logs(module);

-- Indices da tabela notifications
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);

-- =============================================
-- INSERIR DADOS INICIAIS
-- =============================================

-- Usuario administrador
-- Senha: admin123
INSERT INTO users (username, email, password_hash, is_admin, is_active) 
VALUES ('admin', 'admin@cryptoninja.com', '$2b$12$QqsxH202qY/4bQa7SradTu0S8OPAuw7YfSNvGgOiPEqMcMdMwOP56', TRUE, TRUE);

-- Usuario demo
-- Senha: demo123
INSERT INTO users (username, email, password_hash, is_admin, is_active) 
VALUES ('demo', 'demo@cryptoninja.com', '$2b$12$QqsxH202qY/4bQa7SradTu0S8OPAuw7YfSNvGgOiPEqMcMdMwOP56', FALSE, TRUE);

-- Usuario trader
-- Senha: trader123
INSERT INTO users (username, email, password_hash, is_admin, is_active, balance, total_trades, total_pnl) 
VALUES ('trader', 'trader@cryptoninja.com', '$2b$12$QqsxH202qY/4bQa7SradTu0S8OPAuw7YfSNvGgOiPEqMcMdMwOP56', FALSE, TRUE, 15000.00, 25, 1250.75);

-- Exemplo de log inicial
INSERT INTO system_logs (level, message, module, function_name, data)
VALUES ('INFO', 'CryptoNinja Database initialized successfully', 'database', 'create_database', '{"version": "1.0", "timestamp": "' || CURRENT_TIMESTAMP || '"}');

-- Notificacao de boas-vindas para admin
INSERT INTO notifications (user_id, type, title, message, data)
VALUES (1, 'WELCOME', 'Bem-vindo ao CryptoNinja!', 'Seu sistema de trading foi configurado com sucesso. Acesse o painel administrativo para gerenciar usuários.', '{"feature": "admin_panel"}');

-- =============================================
-- COMENTARIOS E DOCUMENTACAO
-- =============================================

COMMENT ON TABLE users IS 'Usuarios do sistema CryptoNinja com autenticacao e dados de trading';
COMMENT ON TABLE user_sessions IS 'Sessoes ativas de usuarios para controle de login';
COMMENT ON TABLE trades IS 'Historico completo de trades de paper trading';
COMMENT ON TABLE signals IS 'Sinais de trading gerados pela IA';
COMMENT ON TABLE market_data IS 'Dados historicos do mercado financeiro';
COMMENT ON TABLE system_logs IS 'Logs de sistema para debugging e monitoramento';
COMMENT ON TABLE notifications IS 'Notificacoes para usuarios do sistema';

-- Comentarios das colunas importantes
COMMENT ON COLUMN users.password_hash IS 'Hash bcrypt da senha do usuario';
COMMENT ON COLUMN users.balance IS 'Saldo atual do paper trading em USD';
COMMENT ON COLUMN users.total_pnl IS 'P&L total acumulado do usuario';
COMMENT ON COLUMN trades.pnl_percent IS 'Percentual de lucro/prejuizo do trade';
COMMENT ON COLUMN signals.confidence IS 'Nivel de confianca do sinal (0-100)';

-- =============================================
-- FUNCOES UTEIS
-- =============================================

-- Funcao para limpar sessoes expiradas
CREATE OR REPLACE FUNCTION clean_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Funcao para calcular P&L de um usuario
CREATE OR REPLACE FUNCTION calculate_user_pnl(user_id_param INTEGER)
RETURNS DECIMAL(15,2) AS $$
DECLARE
    total_pnl DECIMAL(15,2);
BEGIN
    SELECT COALESCE(SUM(pnl), 0) INTO total_pnl 
    FROM trades 
    WHERE user_id = user_id_param AND status = 'closed';
    
    UPDATE users SET total_pnl = total_pnl WHERE id = user_id_param;
    
    RETURN total_pnl;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- VERIFICACOES FINAIS
-- =============================================

-- Verificar tabelas criadas
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    
    RAISE NOTICE 'Tabelas criadas: %', table_count;
    
    IF table_count = 7 THEN
        RAISE NOTICE '✅ Todas as 7 tabelas foram criadas com sucesso!';
    ELSE
        RAISE WARNING '⚠️  Esperado 7 tabelas, encontrado %', table_count;
    END IF;
END $$;

-- Verificar usuarios criados
SELECT 
    '✅ USUARIO CRIADO' as status,
    id, 
    username, 
    email, 
    CASE WHEN is_admin THEN 'ADMIN' ELSE 'USER' END as role,
    balance || ' USD' as balance,
    created_at
FROM users 
ORDER BY id;

-- Verificar indices criados
SELECT 
    '📊 INDICES' as info,
    COUNT(*) as total_indices
FROM pg_indexes 
WHERE schemaname = 'public';

-- Status final
SELECT 
    '🥷 CryptoNinja Database Setup Complete!' as status,
    CURRENT_TIMESTAMP as timestamp,
    CURRENT_DATABASE() as database_name,
    CURRENT_USER as connected_as;

-- Mostrar resumo das tabelas
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns,
    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = t.table_name) as indices
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;
