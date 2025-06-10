-- CryptoNinja Database Schema - Versao Simples
-- Conectar ao banco cryptoninja_db

\c cryptoninja_db;

-- Remover tabelas se existirem (para recriar)
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS system_logs CASCADE;
DROP TABLE IF EXISTS market_data CASCADE;
DROP TABLE IF EXISTS trades CASCADE;
DROP TABLE IF EXISTS signals CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Criar tabela de usuarios
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
    total_pnl DECIMAL(15,2) DEFAULT 0.00
);

-- Criar tabela de sessoes
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Criar tabela de sinais
CREATE TABLE signals (
    id VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    entry_price DECIMAL(15,8) NOT NULL,
    stop_loss DECIMAL(15,8),
    take_profit DECIMAL(15,8),
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    reasons TEXT,
    user_id INTEGER REFERENCES users(id)
);

-- Criar tabela de trades
CREATE TABLE trades (
    id VARCHAR(50) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    signal_id VARCHAR(50) REFERENCES signals(id),
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    entry_price DECIMAL(15,8) NOT NULL,
    exit_price DECIMAL(15,8),
    quantity DECIMAL(20,8) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    stop_loss DECIMAL(15,8),
    take_profit DECIMAL(15,8),
    pnl DECIMAL(15,2),
    pnl_percent DECIMAL(8,4),
    status VARCHAR(20) DEFAULT 'open',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_timestamp TIMESTAMP,
    exit_reason VARCHAR(50)
);

-- Criar tabela de dados de mercado
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(15,8) NOT NULL,
    high_price DECIMAL(15,8) NOT NULL,
    low_price DECIMAL(15,8) NOT NULL,
    close_price DECIMAL(15,8) NOT NULL,
    volume DECIMAL(20,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de logs do sistema
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(100),
    function_name VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSONB
);

-- Criar tabela de notificacoes
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar indices para performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_signals_symbol ON signals(symbol);
CREATE INDEX idx_signals_user ON signals(user_id);
CREATE INDEX idx_trades_user ON trades(user_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_market_symbol_time ON market_data(symbol, timeframe, timestamp);
CREATE INDEX idx_logs_level ON system_logs(level);
CREATE INDEX idx_notifications_user ON notifications(user_id);

-- Inserir usuario admin
INSERT INTO users (username, email, password_hash, is_admin) 
VALUES ('admin', 'admin@cryptoninja.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBVpPI9nD.U2se', TRUE);

-- Inserir usuario demo
INSERT INTO users (username, email, password_hash, is_admin) 
VALUES ('demo', 'demo@cryptoninja.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBVpPI9nD.U2se', FALSE);

-- Comentarios das tabelas
COMMENT ON TABLE users IS 'Usuarios do sistema CryptoNinja';
COMMENT ON TABLE trades IS 'Historico de trades de paper trading';
COMMENT ON TABLE signals IS 'Sinais gerados pela IA';
COMMENT ON TABLE market_data IS 'Dados historicos do mercado';

-- Verificar tabelas criadas
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- Verificar usuarios criados
SELECT id, username, email, is_admin, created_at FROM users;

-- Mensagem final
SELECT 'CryptoNinja Database Setup Complete!' as status;
