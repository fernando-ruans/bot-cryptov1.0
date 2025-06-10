# 🥷 CryptoNinja - Guia de Deploy Universal

## 🚀 Deploy em Diferentes Plataformas

### 📋 **Pré-requisitos**
- PostgreSQL configurado
- Python 3.9+
- Dependências do requirements.txt instaladas

### 🔧 **Processo de Deploy**

#### **1. Configurar Banco de Dados**
**Escolha o script apropriado para seu ambiente:**

```bash
# DESENVOLVIMENTO LOCAL (PostgreSQL instalado)
psql -U postgres -f create_database.sql

# HEROKU, RAILWAY, DIGITALOCEAN
heroku pg:psql -f schema_cloud.sql
# OU
psql $DATABASE_URL -f schema_cloud.sql

# SUPABASE (via SQL Editor)
# Cole o conteúdo de schema_supabase.sql no SQL Editor
```

**Scripts disponíveis:**
- `create_database.sql` - Cria banco + tabelas (local)
- `schema_cloud.sql` - Apenas tabelas (cloud genérico)  
- `schema_supabase.sql` - Supabase com RLS

**Todos incluem usuários de teste:**
- admin:admin123 (administrador)
- demo:demo123 (usuário normal)
- trader:trader123 (usuário com dados)

#### **2. Configurar Variáveis de Ambiente**
```bash
# Copiar template
cp env.template .env

# Editar .env com suas configurações
# Principalmente DATABASE_URL e SECRET_KEY
```

#### **3. Deploy Local**
```bash
python main.py
```

#### **4. Deploy Heroku**
```bash
# Instalar Heroku CLI
# Fazer login: heroku login

# Criar app
heroku create cryptoninja-app

# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:mini

# Configurar variáveis
heroku config:set SECRET_KEY="sua-chave-secreta"
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Executar setup do banco
heroku pg:psql < schema_simples.sql
heroku pg:psql < deploy_users.sql
```

#### **5. Deploy Docker**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: cryptoninja_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: admin
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./schema_simples.sql:/docker-entrypoint-initdb.d/1-schema.sql
      - ./deploy_users.sql:/docker-entrypoint-initdb.d/2-users.sql

  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://postgres:admin@db:5432/cryptoninja_db
    depends_on:
      - db

volumes:
  postgres_data:
```

#### **6. Deploy Supabase + Vercel**
```bash
# 1. Criar projeto Supabase
# Acesse https://supabase.com/dashboard
# Crie novo projeto

# 2. Configurar banco
# Acesse SQL Editor no Supabase
# Cole conteúdo de schema_supabase.sql
# Execute

# 3. Deploy Vercel
vercel deploy
vercel env add DATABASE_URL
vercel env add SUPABASE_URL  
vercel env add SUPABASE_ANON_KEY

# 4. Verificar
# Acesse URL do Vercel
# Login: admin / admin123
```

#### **7. Deploy AWS/Digital Ocean**
```bash
# Configurar servidor Ubuntu
sudo apt update
sudo apt install python3 python3-pip postgresql postgresql-contrib

# Configurar PostgreSQL
sudo -u postgres createdb cryptoninja_db
sudo -u postgres psql -f schema_simples.sql
sudo -u postgres psql -f deploy_users.sql

# Instalar app
pip3 install -r requirements.txt
python3 main.py
```

### 🔐 **Segurança para Produção**

#### **Alterar Senhas Padrão**
```sql
-- Conectar ao banco de produção
UPDATE users SET password_hash = 'novo_hash_bcrypt' WHERE username = 'admin';
```

#### **Gerar Hash Seguro**
```python
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
new_hash = bcrypt.generate_password_hash('nova_senha_super_segura').decode('utf-8')
print(new_hash)
```

### ✅ **Verificação Pós-Deploy**
1. Acessar aplicação via URL
2. Testar login com usuários de teste:
   - **Admin:** admin / admin123
   - **Demo:** demo / demo123  
   - **Trader:** trader / trader123
3. Alterar senhas padrão (IMPORTANTE!)
4. Verificar funcionalidades de trading
5. Testar painel administrativo
6. Verificar dados de mercado em tempo real

### 🆘 **Troubleshooting**

#### **Erro de Hash/Login**
```bash
# Regenerar usuários com hashes válidos
python3 deploy_setup.py
psql -f deploy_users.sql
```

#### **Erro de Conexão com Banco**
- Verificar DATABASE_URL no .env
- Testar conexão manual com psql
- Verificar credenciais e rede

#### **Erro de Dependências**
```bash
pip3 install --upgrade -r requirements.txt
```

---
**CryptoNinja 🥷 pronto para deploy em qualquer plataforma!**
