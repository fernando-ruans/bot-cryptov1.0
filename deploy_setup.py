#!/usr/bin/env python3
"""
CryptoNinja 🥷 - Setup de Deploy Universal
Script para criar usuários iniciais em qualquer plataforma

ATENÇÃO: Este script é LEGADO!
Use os novos scripts de banco:
- create_database.sql (local)
- schema_cloud.sql (cloud genérico) 
- schema_supabase.sql (supabase com RLS)

Todos já incluem usuários com hashes válidos!
"""

import os
import sys
from flask import Flask
from flask_bcrypt import Bcrypt

def generate_deployment_script():
    """Gerar script SQL com hashes válidos para deploy"""
    
    # Inicializar bcrypt
    bcrypt = Bcrypt()
    
    # Gerar hashes para senhas padrão
    admin_password = "ninja123"
    demo_password = "ninja123"
    
    admin_hash = bcrypt.generate_password_hash(admin_password).decode('utf-8')
    demo_hash = bcrypt.generate_password_hash(demo_password).decode('utf-8')
    
    # Script SQL para deploy
    sql_script = f"""-- CryptoNinja 🥷 - Setup de Deploy Universal
-- Execute este script APÓS criar o banco e tabelas

-- Limpar usuários existentes (se houver)
DELETE FROM user_sessions;
DELETE FROM users;

-- Inserir usuário admin com hash válido
INSERT INTO users (username, email, password_hash, is_admin, balance, total_trades, total_pnl) 
VALUES ('admin', 'admin@cryptoninja.com', '{admin_hash}', TRUE, 10000.00, 0, 0.00);

-- Inserir usuário demo com hash válido  
INSERT INTO users (username, email, password_hash, is_admin, balance, total_trades, total_pnl) 
VALUES ('demo', 'demo@cryptoninja.com', '{demo_hash}', FALSE, 10000.00, 0, 0.00);

-- Verificar usuários criados
SELECT id, username, email, is_admin, 
       LEFT(password_hash, 10) || '...' as hash_preview,
       LENGTH(password_hash) as hash_length,
       created_at 
FROM users 
ORDER BY id;

-- Mensagem de sucesso
SELECT 'CryptoNinja Deploy Setup Complete! ✅' as status;
"""
    
    # Salvar script de deploy
    with open('deploy_users.sql', 'w', encoding='utf-8') as f:
        f.write(sql_script)
    
    print("🎯 DEPLOY SCRIPT GERADO!")
    print("=" * 50)
    print(f"📄 Arquivo: deploy_users.sql")
    print(f"🔑 Admin: admin / {admin_password}")
    print(f"👤 Demo: demo / {demo_password}")
    print(f"🔐 Admin Hash: {admin_hash}")
    print(f"🔐 Demo Hash: {demo_hash}")
    print("=" * 50)
    
    return {
        'admin_hash': admin_hash,
        'demo_hash': demo_hash,
        'script_file': 'deploy_users.sql'
    }

def generate_env_template():
    """Gerar template .env para deploy"""
    
    env_template = """# CryptoNinja 🥷 - Configuração de Deploy
# Copie este arquivo para .env e ajuste as variáveis

# ============================================================================
# BANCO DE DADOS
# ============================================================================
# PostgreSQL Local (Desenvolvimento)
DATABASE_URL=postgresql://postgres:admin@localhost:5432/cryptoninja_db

# PostgreSQL Heroku (exemplo)
# DATABASE_URL=postgres://usuario:senha@host:5432/banco

# PostgreSQL AWS RDS (exemplo)  
# DATABASE_URL=postgresql://usuario:senha@endpoint.region.rds.amazonaws.com:5432/cryptoninja_db

# PostgreSQL Docker (exemplo)
# DATABASE_URL=postgresql://postgres:senha@db:5432/cryptoninja_db

# ============================================================================
# SEGURANÇA
# ============================================================================
SECRET_KEY=cryptoninja-secret-key-2025-change-in-production
FLASK_ENV=production

# ============================================================================
# USUÁRIOS PADRÃO
# ============================================================================
DEFAULT_ADMIN_PASSWORD=ninja123
DEFAULT_DEMO_PASSWORD=ninja123

# ⚠️ IMPORTANTE: Altere as senhas após o primeiro deploy!

# ============================================================================
# CONFIGURAÇÕES DE TRADING
# ============================================================================
DEFAULT_BALANCE=10000.00
MAX_CONCURRENT_TRADES=5
RISK_PERCENTAGE=2.0

# ============================================================================
# APIs EXTERNAS
# ============================================================================
BINANCE_API_URL=https://api.binance.com
REAL_TIME_UPDATES=true

# ============================================================================
# LOGS
# ============================================================================
LOG_LEVEL=INFO
LOG_TO_FILE=false

# ============================================================================
# CONFIGURAÇÕES DE DEPLOY
# ============================================================================
# Porta para deploy (Heroku usa PORT automaticamente)
PORT=5000

# Host (0.0.0.0 para aceitar conexões externas)
HOST=0.0.0.0
"""
    
    with open('env.template', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("📄 Template .env criado: env.template")

def generate_deployment_guide():
    """Gerar guia de deploy"""
    
    guide = """# 🥷 CryptoNinja - Guia de Deploy Universal

## 🚀 Deploy em Diferentes Plataformas

### 📋 **Pré-requisitos**
- PostgreSQL configurado
- Python 3.9+
- Dependências do requirements.txt instaladas

### 🔧 **Processo de Deploy**

#### **1. Configurar Banco de Dados**
```sql
-- Executar primeiro o schema principal
psql -f schema_simples.sql

-- Depois executar usuários com hashes válidos
psql -f deploy_users.sql
```

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

#### **6. Deploy AWS/Digital Ocean**
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
2. Testar login: admin / ninja123
3. Alterar senhas padrão
4. Verificar funcionalidades de trading
5. Testar painel administrativo

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
"""
    
    with open('GUIA_DEPLOY.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("📖 Guia de deploy criado: GUIA_DEPLOY.md")

def main():
    """Função principal"""
    print("🥷 CryptoNinja - Gerador de Scripts de Deploy")
    print("=" * 60)
    
    # Gerar script SQL com hashes válidos
    result = generate_deployment_script()
    
    # Gerar template de ambiente
    generate_env_template()
    
    # Gerar guia de deploy
    generate_deployment_guide()
    
    print("\n🎯 DEPLOY PACKAGE CRIADO!")
    print("=" * 60)
    print("📄 Arquivos gerados:")
    print("   • deploy_users.sql (usuários com hash válido)")
    print("   • env.template (template de configuração)")
    print("   • GUIA_DEPLOY.md (instruções completas)")
    print("\n🚀 Pronto para deploy em qualquer plataforma!")
    print("=" * 60)
    
    # Testar hash gerado
    try:
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        test_password = "ninja123"
        test_result = bcrypt.check_password_hash(result['admin_hash'], test_password)
        print(f"✅ Teste de hash: {'VÁLIDO' if test_result else 'INVÁLIDO'}")
    except Exception as e:
        print(f"⚠️ Erro no teste de hash: {e}")

if __name__ == "__main__":
    main()
