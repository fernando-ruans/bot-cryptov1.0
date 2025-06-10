# 🥷 CryptoNinja - Sistema de Login PostgreSQL ✅

## ✅ SETUP CONCLUÍDO COM SUCESSO!

### 🗄️ **Banco de Dados PostgreSQL**
- **Banco:** `cryptoninja_db`
- **Host:** `localhost:5432`
- **Usuário:** `postgres`
- **Senha:** `admin`

### 👥 **Usuários Criados**
1. **Admin:**
   - **Username:** `admin`
   - **Email:** `admin@cryptoninja.com`
   - **Senha:** `ninja123`
   - **Permissões:** Administrador ✨

2. **Demo:**
   - **Username:** `demo`
   - **Email:** `demo@cryptoninja.com`
   - **Senha:** `ninja123`
   - **Permissões:** Usuário padrão 👤

### 📊 **Tabelas Criadas**
- ✅ `users` - Usuários do sistema
- ✅ `user_sessions` - Sessões de login
- ✅ `signals` - Sinais de trading gerados pela IA
- ✅ `trades` - Histórico de trades (paper trading)
- ✅ `market_data` - Dados históricos do mercado
- ✅ `system_logs` - Logs do sistema
- ✅ `notifications` - Notificações para usuários

### 🔧 **Configuração**
- ✅ Arquivo `.env` configurado com DATABASE_URL
- ✅ Sistema de autenticação Flask-Login integrado
- ✅ Senhas criptografadas com bcrypt
- ✅ Índices de performance criados

## 🚀 **Como Usar**

### 1. **Iniciar o Sistema**
```bash
python main.py
```

### 2. **Acessar o Dashboard**
- **URL:** http://localhost:5000
- **Login:** `admin` / `ninja123`
- **Ou:** `demo` / `ninja123`

### 3. **Funcionalidades Disponíveis**
- 🎯 Dashboard principal com dados de mercado em tempo real
- 📈 Geração de sinais de trading via IA
- 💰 Sistema de paper trading completo
- 📊 Histórico de trades e estatísticas
- 🔔 Notificações em tempo real via WebSocket
- 🎨 Interface ninja-themed com animações

## ⚠️ **IMPORTANTE - Segurança**

### 🔐 **Alterar Senhas Padrão**
```sql
-- Conectar ao banco
\c cryptoninja_db;

-- Gerar nova senha hash (exemplo para 'nova_senha_segura')
-- Use o comando Python para gerar:
-- from flask_bcrypt import Bcrypt; bcrypt = Bcrypt(); print(bcrypt.generate_password_hash('nova_senha_segura').decode('utf-8'))

-- Atualizar senha do admin
UPDATE users SET password_hash = 'nova_hash_aqui' WHERE username = 'admin';
```

### 🌐 **Configuração para Produção**
1. **Alterar SECRET_KEY** no arquivo `.env`
2. **Configurar HTTPS**
3. **Firewall** para PostgreSQL
4. **Backup** automático do banco
5. **Logs de auditoria**

## 🎮 **Fluxo de Uso Típico**

1. **Login** → http://localhost:5000/auth/login
2. **Dashboard** → Visualizar mercado em tempo real
3. **Gerar Sinal** → Clicar em "Gerar Sinal" para símbolo desejado
4. **Confirmar Trade** → Aprovar sinal para abrir paper trade
5. **Monitorar** → Acompanhar trades ativos em tempo real
6. **Histórico** → Visualizar performance e estatísticas

## 🐛 **Troubleshooting**

### Problema: "Erro de conexão com banco"
```bash
# Verificar se PostgreSQL está rodando
Get-Service postgresql*

# Testar conexão
$env:PGPASSWORD="admin"; psql -h localhost -U postgres -c "SELECT 1;"
```

### Problema: "Usuário não encontrado"
```sql
-- Verificar usuários
SELECT * FROM users;

-- Recriar usuário admin se necessário
INSERT INTO users (username, email, password_hash, is_admin) 
VALUES ('admin', 'admin@cryptoninja.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBVpPI9nD.U2se', TRUE);
```

---

## 🎉 **Sistema Pronto!**

O CryptoNinja agora está totalmente configurado com:
- ✅ Sistema de login PostgreSQL funcional
- ✅ Interface ninja-themed moderna
- ✅ Trading bot com IA integrada
- ✅ Paper trading em tempo real
- ✅ Dados de mercado Binance ao vivo

**Próximos passos:** Fazer login e começar a usar o sistema! 🚀

---
*CryptoNinja 🥷 - Stealth Trading AI*
