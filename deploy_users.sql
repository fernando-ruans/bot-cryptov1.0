-- CryptoNinja 🥷 - Setup de Deploy Universal
-- Execute este script APÓS criar o banco e tabelas

-- Limpar usuários existentes (se houver)
DELETE FROM user_sessions;
DELETE FROM users;

-- Inserir usuário admin com hash válido
INSERT INTO users (username, email, password_hash, is_admin, balance, total_trades, total_pnl) 
VALUES ('admin', 'admin@cryptoninja.com', '$2b$12$NZb9fC3Whw/LLZazml8PiOswx79tjc97WAuWEvmoPiTNSnl14YCE.', TRUE, 10000.00, 0, 0.00);

-- Inserir usuário demo com hash válido  
INSERT INTO users (username, email, password_hash, is_admin, balance, total_trades, total_pnl) 
VALUES ('demo', 'demo@cryptoninja.com', '$2b$12$FwENOUpYmQFL1A6xkM8XKu8b/Gg9zRnmolLOXZTQfSMGZY6Vl2t.G', FALSE, 10000.00, 0, 0.00);

-- Verificar usuários criados
SELECT id, username, email, is_admin, 
       LEFT(password_hash, 10) || '...' as hash_preview,
       LENGTH(password_hash) as hash_length,
       created_at 
FROM users 
ORDER BY id;

-- Mensagem de sucesso
SELECT 'CryptoNinja Deploy Setup Complete! ✅' as status;
