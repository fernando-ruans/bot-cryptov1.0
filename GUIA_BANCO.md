# 🥷 CryptoNinja - Guia de Configuração do Banco de Dados

## 📋 Scripts Disponíveis

Foram criados **3 scripts** diferentes para atender diferentes ambientes:

### 1. `create_database.sql` - PostgreSQL Local
**Para desenvolvimento local com PostgreSQL instalado**

```bash
# Executar como superuser (postgres)
psql -U postgres -f create_database.sql

# OU via pgAdmin
# 1. Conecte como postgres
# 2. Abra Query Tool
# 3. Cole o conteúdo do arquivo
# 4. Execute
```

**O que faz:**
- ✅ Cria o banco `cryptoninja_db` do zero
- ✅ Cria todas as 7 tabelas com constraints
- ✅ Cria índices para performance
- ✅ Insere usuários de teste
- ✅ Cria funções úteis
- ✅ Validações completas

### 2. `schema_cloud.sql` - Ambientes Cloud Genéricos
**Para Heroku, Railway, DigitalOcean, etc.**

```bash
# Heroku
heroku pg:psql -f schema_cloud.sql

# Railway
railway run psql -f schema_cloud.sql

# DigitalOcean
psql $DATABASE_URL -f schema_cloud.sql
```

**O que faz:**
- ✅ Não tenta criar banco (já existe)
- ✅ Cria apenas tabelas e estrutura
- ✅ Mesma funcionalidade do script local
- ✅ Compatível com a maioria dos clouds

### 3. `schema_supabase.sql` - Específico para Supabase
**Para Supabase com RLS (Row Level Security)**

```bash
# No Supabase Dashboard:
# 1. Acesse SQL Editor
# 2. Cole o conteúdo completo
# 3. Execute
```

**O que faz:**
- ✅ Cria tabelas otimizadas para Supabase
- ✅ Configura RLS (Row Level Security)
- ✅ Cria políticas de segurança
- ✅ Triggers automáticos
- ✅ Permissões específicas

## 🔐 Usuários de Teste Criados

Todos os scripts criam os mesmos usuários:

| Username | Email | Senha | Tipo | Saldo |
|----------|-------|-------|------|-------|
| `admin` | admin@cryptoninja.com | `admin123` | Admin | $10,000 |
| `demo` | demo@cryptoninja.com | `demo123` | User | $10,000 |
| `trader` | trader@cryptoninja.com | `trader123` | User | $15,000 |

## 🚀 Deploy por Ambiente

### 🏠 Desenvolvimento Local

1. **Instalar PostgreSQL:**
   ```bash
   # Windows (via Chocolatey)
   choco install postgresql
   
   # macOS (via Homebrew)
   brew install postgresql
   
   # Ubuntu
   sudo apt install postgresql postgresql-contrib
   ```

2. **Executar script:**
   ```bash
   psql -U postgres -f create_database.sql
   ```

3. **Configurar variáveis:**
   ```bash
   export DATABASE_URL="postgresql://postgres:password@localhost:5432/cryptoninja_db"
   ```

### ☁️ Heroku

1. **Criar app e addon:**
   ```bash
   heroku create cryptoninja-app
   heroku addons:create heroku-postgresql:hobby-dev
   ```

2. **Executar script:**
   ```bash
   heroku pg:psql -f schema_cloud.sql
   ```

3. **Variáveis já configuradas automaticamente**

### 🔥 Supabase

1. **Criar projeto no [Supabase](https://supabase.com)**

2. **Executar no SQL Editor:**
   - Acesse SQL Editor
   - Cole conteúdo de `schema_supabase.sql`
   - Execute

3. **Configurar variáveis no Vercel:**
   ```bash
   vercel env add DATABASE_URL
   vercel env add SUPABASE_URL
   vercel env add SUPABASE_ANON_KEY
   ```

### 🚄 Railway

1. **Criar projeto:**
   ```bash
   railway login
   railway init
   railway add postgresql
   ```

2. **Executar script:**
   ```bash
   railway run psql -f schema_cloud.sql
   ```

## 🔧 Configuração do Flask

Certifique-se que seu `main.py` tem:

```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco
if 'DATABASE_URL' in os.environ:
    # Produção (Heroku, Supabase, etc.)
    database_url = os.environ['DATABASE_URL']
    # Fix para psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Desenvolvimento local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/cryptoninja_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

## 🧪 Teste da Configuração

Após executar qualquer script, teste com:

```sql
-- Verificar tabelas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' ORDER BY table_name;

-- Verificar usuários
SELECT id, username, email, is_admin, created_at FROM users;

-- Testar função
SELECT clean_expired_sessions();
```

## 🆘 Troubleshooting

### Erro: "database does not exist"
**Solução:** Use `create_database.sql` para local ou `schema_cloud.sql` para cloud

### Erro: "permission denied"
**Solução:** Execute como superuser (`postgres`) ou use `schema_cloud.sql`

### Erro: "relation already exists"
**Solução:** Scripts têm `DROP TABLE IF EXISTS`, execute novamente

### Erro de conexão no Heroku
**Solução:** 
```bash
# Verificar URL do banco
heroku config:get DATABASE_URL

# Conectar manualmente
heroku pg:psql
```

### RLS não funciona no Supabase
**Solução:** Use `schema_supabase.sql` que configura RLS corretamente

## 📊 Estrutura do Banco

```
cryptoninja_db/
├── users (usuários)
├── user_sessions (sessões)
├── signals (sinais IA)
├── trades (histórico)
├── market_data (dados mercado)
├── system_logs (logs)
└── notifications (notificações)
```

## 🔄 Próximos Passos

1. ✅ Execute o script apropriado para seu ambiente
2. ✅ Configure variáveis de ambiente
3. ✅ Teste conexão com Flask
4. ✅ Deploy no Vercel
5. ✅ Faça login com `admin:admin123`

---

**🥷 Projeto pronto para produção com segurança e performance!**
