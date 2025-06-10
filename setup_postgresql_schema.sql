-- =============================================================================
-- CRYPTONINJA 🥷 - SCHEMA POSTGRESQL
-- Script para criação do banco de dados e tabelas
-- =============================================================================

-- Conectar como superusuário e criar o banco
-- psql -U postgres -h localhost

-- Criar o banco de dados
DROP DATABASE IF EXISTS cryptoninja_db;
CREATE DATABASE cryptoninja_db;

-- Conectar ao banco criado
\c cryptoninja_db;

-- Criar extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- TABELAS DE AUTENTICAÇÃO
-- =============================================================================

-- Tabela de usuários
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Campos específicos para trading
    balance DECIMAL(15,2) DEFAULT 10000.00,
    total_trades INTEGER DEFAULT 0,
    total_pnl DECIMAL(15,2) DEFAULT 0.00
);

-- Tabela de sessões de usuário
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- =============================================================================
-- TABELAS DE TRADING
-- =============================================================================

-- Tabela de sinais de trading
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('buy', 'sell', 'hold')),
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    entry_price DECIMAL(15,8) NOT NULL,
    stop_loss DECIMAL(15,8),
    take_profit DECIMAL(15,8),
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'executed', 'expired', 'cancelled')),
    
    -- Dados de análise (JSON)
    reasons JSONB,
    ai_prediction JSONB,
    technical_analysis JSONB,
    market_context JSONB,
    
    -- Índices para performance
    INDEX idx_signals_symbol (symbol),
    INDEX idx_signals_timestamp (timestamp),
    INDEX idx_signals_status (status),
    INDEX idx_signals_user (user_id)
);

-- Tabela de trades (paper trading)
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    signal_id UUID REFERENCES signals(id) ON DELETE SET NULL,
    
    -- Dados básicos do trade
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10) NOT NULL CHECK (trade_type IN ('buy', 'sell')),
    quantity DECIMAL(20,8) NOT NULL,
    entry_price DECIMAL(15,8) NOT NULL,
    exit_price DECIMAL(15,8),
    
    -- Níveis de risco
    stop_loss DECIMAL(15,8),
    take_profit DECIMAL(15,8),
    
    -- Status e timestamps
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_timestamp TIMESTAMP,
    exit_reason VARCHAR(20) CHECK (exit_reason IN ('manual', 'stop_loss', 'take_profit', 'expired')),
    
    -- Preços para tracking
    current_price DECIMAL(15,8),
    max_price DECIMAL(15,8),
    min_price DECIMAL(15,8),
    
    -- P&L
    unrealized_pnl DECIMAL(15,2) DEFAULT 0.00,
    realized_pnl DECIMAL(15,2) DEFAULT 0.00,
    pnl_percent DECIMAL(8,4) DEFAULT 0.00,
    
    -- Metadados
    signal_confidence DECIMAL(5,4),
    timeframe VARCHAR(10),
    
    -- Índices para performance
    INDEX idx_trades_symbol (symbol),
    INDEX idx_trades_user (user_id),
    INDEX idx_trades_status (status),
    INDEX idx_trades_timestamp (timestamp),
    INDEX idx_trades_signal (signal_id)
);

-- =============================================================================
-- TABELAS DE ANÁLISE E LOGS
-- =============================================================================

-- Tabela de dados de mercado históricos
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- OHLCV
    open_price DECIMAL(15,8) NOT NULL,
    high_price DECIMAL(15,8) NOT NULL,
    low_price DECIMAL(15,8) NOT NULL,
    close_price DECIMAL(15,8) NOT NULL,
    volume DECIMAL(20,4) NOT NULL,
    
    -- Indicadores técnicos (JSON para flexibilidade)
    indicators JSONB,
    
    -- Índices compostos
    UNIQUE(symbol, timeframe, timestamp),
    INDEX idx_market_data_symbol_time (symbol, timeframe, timestamp),
    INDEX idx_market_data_timestamp (timestamp)
);

-- Tabela de logs do sistema
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    module VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB,
    
    INDEX idx_logs_level (level),
    INDEX idx_logs_module (module),
    INDEX idx_logs_timestamp (timestamp),
    INDEX idx_logs_user (user_id)
);

-- Tabela de notificações
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('signal', 'trade', 'system', 'alert')),
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_notifications_user (user_id),
    INDEX idx_notifications_type (type),
    INDEX idx_notifications_timestamp (timestamp),
    INDEX idx_notifications_read (is_read)
);

-- =============================================================================
-- VIEWS ÚTEIS
-- =============================================================================

-- View para estatísticas de usuário
CREATE VIEW user_trading_stats AS
SELECT 
    u.id,
    u.username,
    u.balance,
    u.total_trades,
    u.total_pnl,
    COUNT(t.id) FILTER (WHERE t.status = 'open') as active_trades,
    COUNT(t.id) FILTER (WHERE t.status = 'closed' AND t.realized_pnl > 0) as winning_trades,
    COUNT(t.id) FILTER (WHERE t.status = 'closed' AND t.realized_pnl < 0) as losing_trades,
    CASE 
        WHEN COUNT(t.id) FILTER (WHERE t.status = 'closed') > 0 
        THEN ROUND(
            (COUNT(t.id) FILTER (WHERE t.status = 'closed' AND t.realized_pnl > 0)::DECIMAL / 
             COUNT(t.id) FILTER (WHERE t.status = 'closed')) * 100, 2
        )
        ELSE 0 
    END as win_rate_percent,
    COALESCE(SUM(t.realized_pnl), 0) as total_realized_pnl,
    COALESCE(SUM(t.unrealized_pnl) FILTER (WHERE t.status = 'open'), 0) as total_unrealized_pnl
FROM users u
LEFT JOIN trades t ON u.id = t.user_id
GROUP BY u.id, u.username, u.balance, u.total_trades, u.total_pnl;

-- View para análise de performance por símbolo
CREATE VIEW symbol_performance AS
SELECT 
    symbol,
    COUNT(*) as total_trades,
    COUNT(*) FILTER (WHERE realized_pnl > 0) as winning_trades,
    COUNT(*) FILTER (WHERE realized_pnl < 0) as losing_trades,
    AVG(realized_pnl) as avg_pnl,
    SUM(realized_pnl) as total_pnl,
    CASE 
        WHEN COUNT(*) > 0 
        THEN ROUND((COUNT(*) FILTER (WHERE realized_pnl > 0)::DECIMAL / COUNT(*)) * 100, 2)
        ELSE 0 
    END as win_rate_percent,
    AVG(EXTRACT(EPOCH FROM (exit_timestamp - timestamp))/3600) as avg_duration_hours
FROM trades 
WHERE status = 'closed'
GROUP BY symbol
ORDER BY total_pnl DESC;

-- View para sinais por timeframe
CREATE VIEW signals_by_timeframe AS
SELECT 
    timeframe,
    signal_type,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence,
    COUNT(*) FILTER (WHERE status = 'executed') as executed_count
FROM signals
GROUP BY timeframe, signal_type
ORDER BY timeframe, signal_type;

-- =============================================================================
-- FUNÇÕES ÚTEIS
-- =============================================================================

-- Função para calcular estatísticas de trading
CREATE OR REPLACE FUNCTION calculate_user_stats(user_id_param INTEGER)
RETURNS TABLE (
    total_trades BIGINT,
    active_trades BIGINT,
    closed_trades BIGINT,
    winning_trades BIGINT,
    losing_trades BIGINT,
    win_rate DECIMAL,
    total_pnl DECIMAL,
    unrealized_pnl DECIMAL,
    realized_pnl DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(t.id) as total_trades,
        COUNT(t.id) FILTER (WHERE t.status = 'open') as active_trades,
        COUNT(t.id) FILTER (WHERE t.status = 'closed') as closed_trades,
        COUNT(t.id) FILTER (WHERE t.status = 'closed' AND t.realized_pnl > 0) as winning_trades,
        COUNT(t.id) FILTER (WHERE t.status = 'closed' AND t.realized_pnl < 0) as losing_trades,
        CASE 
            WHEN COUNT(t.id) FILTER (WHERE t.status = 'closed') > 0 
            THEN ROUND(
                (COUNT(t.id) FILTER (WHERE t.status = 'closed' AND t.realized_pnl > 0)::DECIMAL / 
                 COUNT(t.id) FILTER (WHERE t.status = 'closed')) * 100, 2
            )
            ELSE 0 
        END as win_rate,
        COALESCE(SUM(t.realized_pnl), 0) + COALESCE(SUM(t.unrealized_pnl) FILTER (WHERE t.status = 'open'), 0) as total_pnl,
        COALESCE(SUM(t.unrealized_pnl) FILTER (WHERE t.status = 'open'), 0) as unrealized_pnl,
        COALESCE(SUM(t.realized_pnl), 0) as realized_pnl
    FROM trades t
    WHERE t.user_id = user_id_param;
END;
$$ LANGUAGE plpgsql;

-- Função para limpar dados antigos
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Limpar sessões expiradas (mais de 30 dias)
    DELETE FROM user_sessions 
    WHERE expires_at < NOW() - INTERVAL '30 days';
    
    -- Limpar logs antigos (mais de 90 dias)
    DELETE FROM system_logs 
    WHERE timestamp < NOW() - INTERVAL '90 days' 
    AND level IN ('DEBUG', 'INFO');
    
    -- Limpar notificações lidas antigas (mais de 30 dias)
    DELETE FROM notifications 
    WHERE is_read = true 
    AND timestamp < NOW() - INTERVAL '30 days';
    
    -- Limpar dados de mercado antigos (mais de 1 ano para timeframes curtos)
    DELETE FROM market_data 
    WHERE timestamp < NOW() - INTERVAL '1 year' 
    AND timeframe IN ('1m', '3m', '5m');
    
    RAISE NOTICE 'Limpeza de dados antigos concluída';
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger para atualizar estatísticas do usuário quando um trade é fechado
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'closed' AND OLD.status = 'open' THEN
        UPDATE users 
        SET 
            total_trades = total_trades + 1,
            total_pnl = total_pnl + NEW.realized_pnl
        WHERE id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_stats
    AFTER UPDATE ON trades
    FOR EACH ROW
    EXECUTE FUNCTION update_user_stats();

-- Trigger para log de atividades importantes
CREATE OR REPLACE FUNCTION log_important_activities()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'trades' THEN
        IF NEW.status = 'closed' AND OLD.status = 'open' THEN
            INSERT INTO system_logs (level, module, message, user_id, extra_data)
            VALUES (
                'INFO', 
                'TRADING', 
                'Trade fechado: ' || NEW.symbol || ' P&L: $' || NEW.realized_pnl,
                NEW.user_id,
                jsonb_build_object(
                    'trade_id', NEW.id,
                    'symbol', NEW.symbol,
                    'pnl', NEW.realized_pnl,
                    'exit_reason', NEW.exit_reason
                )
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_trade_activities
    AFTER UPDATE ON trades
    FOR EACH ROW
    EXECUTE FUNCTION log_important_activities();

-- =============================================================================
-- DADOS INICIAIS
-- =============================================================================

-- Criar usuário administrador
INSERT INTO users (username, email, password_hash, is_admin, balance) 
VALUES (
    'admin', 
    'admin@cryptoninja.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LqB2JOY3GH.6.8e1.',  -- senha: ninja123
    true,
    10000.00
) ON CONFLICT (username) DO NOTHING;

-- Criar usuário demo
INSERT INTO users (username, email, password_hash, is_admin, balance) 
VALUES (
    'demo', 
    'demo@cryptoninja.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LqB2JOY3GH.6.8e1.',  -- senha: ninja123
    false,
    10000.00
) ON CONFLICT (username) DO NOTHING;

-- =============================================================================
-- ÍNDICES ADICIONAIS PARA PERFORMANCE
-- =============================================================================

-- Índices compostos para queries frequentes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trades_user_status_timestamp 
ON trades(user_id, status, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_signals_symbol_status_timestamp 
ON signals(symbol, status, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_market_data_symbol_timeframe_timestamp 
ON market_data(symbol, timeframe, timestamp DESC);

-- Índices para JSON fields
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_signals_reasons_gin 
ON signals USING GIN (reasons);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trades_metadata_gin 
ON trades USING GIN ((jsonb_build_object('timeframe', timeframe, 'signal_confidence', signal_confidence)));

-- =============================================================================
-- POLÍTICAS DE SEGURANÇA (RLS - Row Level Security)
-- =============================================================================

-- Habilitar RLS nas tabelas principais
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Política para trades: usuários só veem seus próprios trades
CREATE POLICY trades_user_policy ON trades
    FOR ALL
    TO PUBLIC
    USING (user_id = current_setting('app.current_user_id')::INTEGER OR current_setting('app.is_admin')::BOOLEAN = true);

-- Política para sinais: usuários só veem seus próprios sinais
CREATE POLICY signals_user_policy ON signals
    FOR ALL
    TO PUBLIC
    USING (user_id = current_setting('app.current_user_id')::INTEGER OR current_setting('app.is_admin')::BOOLEAN = true);

-- Política para notificações: usuários só veem suas próprias notificações
CREATE POLICY notifications_user_policy ON notifications
    FOR ALL
    TO PUBLIC
    USING (user_id = current_setting('app.current_user_id')::INTEGER OR current_setting('app.is_admin')::BOOLEAN = true);

-- =============================================================================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO
-- =============================================================================

COMMENT ON DATABASE cryptoninja_db IS 'CryptoNinja 🥷 - Sistema de Trading Bot com IA';

COMMENT ON TABLE users IS 'Usuários do sistema com informações de trading';
COMMENT ON TABLE user_sessions IS 'Sessões ativas de usuários para controle de acesso';
COMMENT ON TABLE signals IS 'Sinais de trading gerados pela IA';
COMMENT ON TABLE trades IS 'Trades executados (paper trading)';
COMMENT ON TABLE market_data IS 'Dados históricos de mercado com indicadores';
COMMENT ON TABLE system_logs IS 'Logs do sistema para auditoria';
COMMENT ON TABLE notifications IS 'Notificações para os usuários';

-- =============================================================================
-- ANÁLISE DE PERFORMANCE
-- =============================================================================

-- Vacuum e analyze automático
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET track_activities = on;
ALTER SYSTEM SET track_counts = on;

-- =============================================================================
-- BACKUP E MANUTENÇÃO
-- =============================================================================

-- Criar função para backup automático
CREATE OR REPLACE FUNCTION create_backup_tables()
RETURNS void AS $$
BEGIN
    -- Backup diário das tabelas principais
    EXECUTE format('CREATE TABLE IF NOT EXISTS trades_backup_%s AS SELECT * FROM trades WHERE timestamp::date = CURRENT_DATE - 1', 
                   to_char(CURRENT_DATE - 1, 'YYYY_MM_DD'));
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS signals_backup_%s AS SELECT * FROM signals WHERE timestamp::date = CURRENT_DATE - 1', 
                   to_char(CURRENT_DATE - 1, 'YYYY_MM_DD'));
    
    RAISE NOTICE 'Backup tables created for %', CURRENT_DATE - 1;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FINALIZAÇÃO
-- =============================================================================

-- Atualizar estatísticas das tabelas
ANALYZE;

-- Mostrar informações do banco
SELECT 
    schemaname,
    tablename,
    attname as column_name,
    typename as data_type
FROM pg_stats ps
JOIN pg_type pt ON ps.stanullfrac IS NOT NULL
WHERE schemaname = 'public'
ORDER BY schemaname, tablename, attname;

-- Verificar tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

RAISE NOTICE '🥷 CryptoNinja Database Setup Complete!';
RAISE NOTICE '📊 Admin user: admin / ninja123';
RAISE NOTICE '🎮 Demo user: demo / ninja123';
RAISE NOTICE '⚠️ IMPORTANTE: Altere as senhas padrão em produção!';
