-- =============================================
-- CryptoNinja Database - Schema para Supabase
-- Inclui RLS (Row Level Security) e politicas
-- =============================================

-- INSTRUCOES PARA SUPABASE:
-- 1. Acesse seu projeto Supabase
-- 2. Va para SQL Editor
-- 3. Cole e execute este script
-- 4. Configure as variaveis de ambiente no Vercel

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

-- Tabela de dados de mercado (publica)
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
-- CONFIGURAR RLS (Row Level Security)
-- =============================================

-- Habilitar RLS para tabelas sensiveis
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Market data e logs sao publicos (sem RLS)
ALTER TABLE market_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs DISABLE ROW LEVEL SECURITY;

-- =============================================
-- CRIAR POLITICAS RLS
-- =============================================

-- Politicas para users (usuarios podem ver apenas seus dados)
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (id = current_setting('app.current_user_id')::INTEGER);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (id = current_setting('app.current_user_id')::INTEGER);

-- Politicas para sessions (usuarios podem ver apenas suas sessoes)
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR ALL USING (user_id = current_setting('app.current_user_id')::INTEGER);

-- Politicas para trades (usuarios podem ver apenas seus trades)
CREATE POLICY "Users can view own trades" ON trades
    FOR ALL USING (user_id = current_setting('app.current_user_id')::INTEGER);

-- Politicas para signals (usuarios podem ver apenas seus sinais)
CREATE POLICY "Users can view own signals" ON signals
    FOR ALL USING (user_id = current_setting('app.current_user_id')::INTEGER);

-- Politicas para notifications (usuarios podem ver apenas suas notificacoes)
CREATE POLICY "Users can view own notifications" ON notifications
    FOR SELECT USING (user_id = current_setting('app.current_user_id')::INTEGER);

CREATE POLICY "Users can update own notifications" ON notifications
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::INTEGER);

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
VALUES ('INFO', 'CryptoNinja Database initialized on Supabase', 'database', 'create_database', '{"version": "1.0", "environment": "supabase"}');

-- Notificacao de boas-vindas para admin
INSERT INTO notifications (user_id, type, title, message, data)
VALUES (1, 'WELCOME', 'Bem-vindo ao CryptoNinja!', 'Seu sistema de trading foi configurado com sucesso no Supabase. Acesse o painel administrativo para gerenciar usuários.', '{"feature": "admin_panel", "platform": "supabase"}');

-- =============================================
-- FUNCOES UTEIS PARA SUPABASE
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
$$ LANGUAGE plpgsql SECURITY DEFINER;

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
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funcao para autenticar usuario (para uso com RLS)
CREATE OR REPLACE FUNCTION authenticate_user(username_param VARCHAR, password_hash_param VARCHAR)
RETURNS TABLE(user_id INTEGER, is_admin BOOLEAN, is_active BOOLEAN) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.is_admin, u.is_active
    FROM users u
    WHERE u.username = username_param 
      AND u.password_hash = password_hash_param
      AND u.is_active = TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================
-- CRIAR TRIGGERS UTEIS
-- =============================================

-- Trigger para atualizar last_login automaticamente
CREATE OR REPLACE FUNCTION update_last_login()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_last_login
    AFTER INSERT ON user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_last_login();

-- Trigger para atualizar total_trades automaticamente
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users 
        SET total_trades = total_trades + 1
        WHERE id = NEW.user_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' AND OLD.status != 'closed' AND NEW.status = 'closed' THEN
        UPDATE users 
        SET total_pnl = total_pnl + COALESCE(NEW.pnl, 0)
        WHERE id = NEW.user_id;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_stats
    AFTER INSERT OR UPDATE ON trades
    FOR EACH ROW
    EXECUTE FUNCTION update_user_stats();

-- =============================================
-- CONFIGURAR PERMISSOES PUBLICAS
-- =============================================

-- Permitir acesso publico para market_data (apenas leitura)
GRANT SELECT ON market_data TO anon;
GRANT SELECT ON market_data TO authenticated;

-- Permitir acesso publico para system_logs (apenas leitura)
GRANT SELECT ON system_logs TO authenticated;

-- =============================================
-- VERIFICACOES FINAIS
-- =============================================

-- Verificar tabelas criadas
SELECT 
    '🥷 CryptoNinja Supabase Database Setup Complete!' as status,
    COUNT(*) as total_tables
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

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

-- Verificar RLS habilitado
SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Status final detalhado
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name AND table_schema = 'public') as columns,
    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = t.table_name AND schemaname = 'public') as indices
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- =============================================
-- INSTRUCOES PARA VARIAVEIS DE AMBIENTE
-- =============================================

/*
CONFIGURE NO VERCEL AS SEGUINTES VARIAVEIS:

DATABASE_URL=postgresql://[username]:[password]@[host]:[port]/[database]
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_ANON_KEY=[sua-anon-key]
SUPABASE_SERVICE_ROLE_KEY=[sua-service-role-key]

Para encontrar essas informacoes:
1. Va para Settings > API no seu projeto Supabase
2. Copie a URL e as chaves
3. Para DATABASE_URL, va para Settings > Database > Connection string
*/
