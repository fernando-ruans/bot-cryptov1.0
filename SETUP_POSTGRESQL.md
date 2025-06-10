# 🥷 CryptoNinja - Setup PostgreSQL

Este guia explica como configurar o banco de dados PostgreSQL para o CryptoNinja.

## 📋 Pré-requisitos

### Windows
1. **Baixar PostgreSQL**: https://www.postgresql.org/download/windows/
2. **Instalar** com as configurações padrão
3. **Definir senha** do usuário `postgres` como `admin`
4. **Porta padrão**: 5432

### Ubuntu/Linux
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Configurar senha do postgres
sudo -u postgres psql
ALTER USER postgres PASSWORD 'admin';
\q
```

### macOS
```bash
brew install postgresql
brew services start postgresql

# Configurar senha
psql postgres
ALTER USER postgres PASSWORD 'admin';
\q
```

## 🚀 Setup Automático

### Opção 1: Script Python (Recomendado)
```bash
python setup_database.py
```

Este script irá:
- ✅ Verificar se PostgreSQL está instalado
- ✅ Testar conexão com o banco
- ✅ Criar o banco `cryptoninja_db`
- ✅ Criar todas as tabelas
- ✅ Inserir dados iniciais
- ✅ Configurar arquivo `.env`

### Opção 2: Manual via psql
```bash
psql -U postgres -h localhost -f setup_postgresql_schema.sql
```

## 📊 Estrutura do Banco

### Tabelas Principais

#### `users` - Usuários do Sistema
```sql
- id (SERIAL PRIMARY KEY)
- username (VARCHAR UNIQUE)
- email (VARCHAR UNIQUE)
- password_hash (VARCHAR)
- is_admin (BOOLEAN)
- balance (DECIMAL) -- Saldo paper trading
- total_trades (INTEGER)
- total_pnl (DECIMAL)
```

#### `trades` - Trades Executados
```sql
- id (UUID PRIMARY KEY)
- symbol (VARCHAR) -- Ex: BTCUSDT
- trade_type (VARCHAR) -- buy/sell
- entry_price, exit_price (DECIMAL)
- stop_loss, take_profit (DECIMAL)
- status (VARCHAR) -- open/closed
- realized_pnl, unrealized_pnl (DECIMAL)
```

#### `signals` - Sinais de Trading
```sql
- id (UUID PRIMARY KEY)
- symbol, signal_type (VARCHAR)
- confidence (DECIMAL 0-1)
- entry_price, stop_loss, take_profit (DECIMAL)
- timeframe (VARCHAR)
- ai_prediction, technical_analysis (JSONB)
```

### Índices Otimizados
- Consultas por usuário
- Filtros por símbolo e data
- Performance em queries frequentes

## 👤 Usuários Padrão

### Administrador
- **Username**: `admin`
- **Email**: `admin@cryptoninja.com`
- **Senha**: `ninja123`
- **Permissões**: Completas

### Demo
- **Username**: `demo`
- **Email**: `demo@cryptoninja.com`
- **Senha**: `ninja123`
- **Permissões**: Usuário normal

⚠️ **IMPORTANTE**: Altere as senhas padrão em produção!

## 🔧 Configuração no CryptoNinja

O script automaticamente configura o arquivo `.env`:

```env
DATABASE_URL=postgresql://postgres:admin@localhost:5432/cryptoninja_db
```

## ✅ Verificação do Setup

### 1. Verificar Conexão
```bash
psql -U postgres -h localhost -d cryptoninja_db -c "SELECT current_database();"
```

### 2. Verificar Tabelas
```bash
psql -U postgres -h localhost -d cryptoninja_db -c "\dt"
```

### 3. Verificar Usuários
```bash
psql -U postgres -h localhost -d cryptoninja_db -c "SELECT username, is_admin FROM users;"
```

## 🔧 Configurações Avançadas

### Performance
```sql
-- Configurações para melhor performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
SELECT pg_reload_conf();
```

### Backup Automático
```bash
# Criar backup diário
pg_dump -U postgres -h localhost cryptoninja_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U postgres -h localhost -d cryptoninja_db < backup_20250610.sql
```

## 🛠️ Solução de Problemas

### Erro: "Peer authentication failed"
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Alterar 'peer' para 'md5' na linha do postgres
sudo systemctl restart postgresql
```

### Erro: "Connection refused"
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Iniciar se necessário
sudo systemctl start postgresql
```

### Erro: "Database does not exist"
```bash
# Criar banco manualmente
psql -U postgres -c "CREATE DATABASE cryptoninja_db;"
```

### Erro: "Permission denied"
```bash
# Verificar permissões do usuário postgres
psql -U postgres -c "ALTER USER postgres WITH SUPERUSER;"
```

## 📚 Views e Funções Úteis

### Estatísticas de Trading
```sql
SELECT * FROM user_trading_stats WHERE username = 'admin';
```

### Performance por Símbolo
```sql
SELECT * FROM symbol_performance ORDER BY total_pnl DESC;
```

### Limpeza de Dados Antigos
```sql
SELECT cleanup_old_data();
```

## 🔒 Segurança

### Row Level Security (RLS)
- Usuários só veem seus próprios dados
- Admins têm acesso completo
- Logs de auditoria automáticos

### Backup de Segurança
```bash
# Backup completo
pg_dumpall -U postgres > backup_completo.sql

# Backup apenas do CryptoNinja
pg_dump -U postgres cryptoninja_db > backup_cryptoninja.sql
```

## 📞 Suporte

Se encontrar problemas:

1. **Verificar logs**: `/var/log/postgresql/`
2. **Testar conexão**: `pg_isready -U postgres`
3. **Verificar configuração**: `psql -U postgres -c "SHOW config_file;"`

## 🚀 Próximos Passos

Após o setup bem-sucedido:

1. Execute o CryptoNinja: `python main.py`
2. Acesse: http://localhost:5000
3. Faça login com `admin` / `ninja123`
4. **Altere a senha padrão!**

---

🥷 **CryptoNinja - Stealth Trading AI**
