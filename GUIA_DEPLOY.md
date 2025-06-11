# 🥷 CryptoNinja - Guia de Deploy Monolítico

## 🚀 Deploy em Plataformas Otimizadas para Apps Monolíticos

### 💡 **Por que Monólito é Melhor?**
Seu CryptoNinja é uma **aplicação monolítica perfeita** que:
- ✅ **Frontend + Backend** na mesma porta (5000)
- ✅ **Deploy único** sem complexidade de microsserviços
- ✅ **Custo baixo** - uma única instância
- ✅ **Zero configuração CORS** - tudo na mesma origem
- ✅ **Ideal para Render, Vercel, Railway, Heroku**

### 📋 **Pré-requisitos**
- PostgreSQL configurado
- Python 3.9+
- Dependências do requirements.txt instaladas

### 🔧 **Processo de Deploy Simplificado**

#### **🥇 Plataformas Recomendadas (Deploy em 1 Clique)**

##### **1️⃣ RENDER (MAIS FÁCIL) ⭐**
```bash
# 1. Conectar repositório GitHub no Render
# 2. Auto-detecta Python + Flask
# 3. Build automático: pip install -r requirements.txt
# 4. Start automático: python main.py

# Variáveis de ambiente necessárias:
DATABASE_URL=postgresql://...
SECRET_KEY=sua-chave-super-secreta
```

##### **2️⃣ RAILWAY (SEGUNDO MAIS FÁCIL) ⭐**
```bash
# Deploy direto do GitHub
railway login
railway link
railway up

# Adicionar PostgreSQL
railway add postgresql

# Configurar variáveis automaticamente
railway variables set SECRET_KEY="sua-chave"
```

##### **3️⃣ FLY.IO (CONTAINERS) ⭐**
```bash
# Auto-detecta Flask
flyctl launch
flyctl deploy

# PostgreSQL integrado
flyctl postgres create
flyctl postgres attach
```

##### **4️⃣ VERCEL (SERVERLESS) ⭐**
```bash
# Para Flask + Supabase
vercel --prod

# Variáveis necessárias:
vercel env add DATABASE_URL
vercel env add SUPABASE_URL
vercel env add SECRET_KEY
```

#### **📊 CONFIGURAÇÃO UNIVERSAL DO BANCO**
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

#### **⚡ DEPLOY SUPER-RÁPIDO (3 comandos)**
```bash
# 1. Configure banco (escolha um)
psql $DATABASE_URL -f schema_cloud.sql

# 2. Configure variáveis (apenas DATABASE_URL)
export DATABASE_URL="postgresql://user:pass@host:5432/db"

# 3. Deploy! (escolha a plataforma)
git push  # Render/Railway auto-deploy
# OU
vercel --prod  # Vercel
# OU  
flyctl deploy  # Fly.io
```
python main.py
```

#### **🔧 DEPLOY AVANÇADO (quando necessário)**

##### **🐳 Docker (Para VPS/AWS/GCP)**
```dockerfile
# Dockerfile (já otimizado)
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]
```

```bash
# Deploy com Docker
docker build -t cryptoninja .
docker run -p 5000:5000 -e DATABASE_URL="postgresql://..." cryptoninja
```

##### **☁️ Digital Ocean/AWS (VPS Manual)**
```bash
# Configurar servidor Ubuntu
sudo apt update && sudo apt install python3 python3-pip postgresql

# Clonar e configurar
git clone seu-repo
cd cryptoninja
pip3 install -r requirements.txt

# Configurar banco
sudo -u postgres psql -f schema_cloud.sql

# Executar
python3 main.py
```

### 🎯 **Comparação de Plataformas Monolíticas**

| Plataforma | Dificuldade | Custo/mês | Auto-Deploy | PostgreSQL | Tempo Setup |
|------------|-------------|-----------|-------------|------------|-------------|
| **Render** | ⭐ (Fácil) | $7-25 | ✅ GitHub | ✅ Incluído | 5 min |
| **Railway** | ⭐ (Fácil) | $5-20 | ✅ GitHub | ✅ Incluído | 3 min |
| **Fly.io** | ⭐⭐ (Médio) | $5-30 | ✅ Git | ✅ Integrado | 10 min |
| **Vercel** | ⭐⭐ (Médio) | $0-20 | ✅ GitHub | ⚠️ Supabase | 15 min |
| **Heroku** | ⭐⭐⭐ (Difícil) | $7-25 | ✅ Git | ✅ Addon | 20 min |
| **DigitalOcean** | ⭐⭐⭐ (Manual) | $5-40 | ❌ Manual | ✅ Manual | 30 min |

### 💰 **Recomendação de Custo-Benefício**

#### **Para Iniciantes (Mais Fácil):**
1. **Render** - Deploy automático + PostgreSQL incluído
2. **Railway** - Interface moderna + setup rápido

#### **Para Avançados (Mais Controle):**
1. **Fly.io** - Containers + preço competitivo
2. **DigitalOcean** - VPS próprio + máximo controle

### 🔐 **Segurança Simplificada**

#### **🔑 Variáveis Essenciais (Apenas 2-3)**
```bash
# OBRIGATÓRIAS (todas as plataformas)
DATABASE_URL=postgresql://user:pass@host:5432/cryptoninja_db
SECRET_KEY=sua-chave-super-secreta-minimo-32-chars

# OPCIONAL (para Supabase apenas)
SUPABASE_URL=https://projeto.supabase.co
SUPABASE_ANON_KEY=sua-chave-publica
```

#### **🛡️ Alterar Senhas Pós-Deploy (CRÍTICO)**
```sql
-- EMERGÊNCIA: Alterar senha admin
UPDATE users SET password_hash = '$2b$12$NovoHashAqui' WHERE username = 'admin';
```

#### **⚡ Gerar Nova Senha**
```python
# Execute no terminal Python
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
hash_novo = bcrypt.generate_password_hash('MinhaSenhaSegura123!').decode('utf-8')
print(f"Novo hash: {hash_novo}")
```

### ✅ **Checklist Pós-Deploy Monolítico**

#### **🎯 Teste Básico (2 minutos)**
1. ✅ **URL funciona:** https://seu-app.render.com
2. ✅ **Login admin:** admin / admin123  
3. ✅ **Dashboard carrega:** Gráficos + dados aparecem
4. ✅ **Trading funciona:** Botões geram sinais

#### **🔒 Segurança (5 minutos)**
1. ✅ **Alterar senha admin** (CRÍTICO!)
2. ✅ **Verificar HTTPS** ativo
3. ✅ **DATABASE_URL** não vazou nos logs
4. ✅ **SECRET_KEY** é única (não a padrão)

#### **📊 Performance (opcional)**
1. ✅ **Tempo de carregamento** < 3 segundos
2. ✅ **APIs respondem** em < 1 segundo  
3. ✅ **WebSocket conecta** (dados tempo real)
4. ✅ **Mobile funciona** (responsivo)

### 🆘 **Troubleshooting Monolítico**

#### **❌ App não inicia**
```bash
# Verificar logs da plataforma
render logs  # Render
railway logs  # Railway
flyctl logs  # Fly.io

# Causa comum: DATABASE_URL mal configurada
```

#### **❌ Erro 500 (Database)**
```bash
# Testar conexão manual
psql $DATABASE_URL -c "SELECT version();"

# Re-executar schema se necessário
psql $DATABASE_URL -f schema_cloud.sql
```

#### **❌ Login não funciona**
```bash
# Verificar usuários no banco
psql $DATABASE_URL -c "SELECT username, LEFT(password_hash, 10) FROM users;"

# Regenerar usuários se necessário
python deploy_setup.py
```

#### **❌ Deploy falha (Build)**
```bash
# Verificar Python version no requirements.txt
echo "python-3.9.x" >> runtime.txt  # Heroku
# OU configurar nas plataformas

# Limpar cache
git commit --allow-empty -m "trigger rebuild"
git push
```

### 🎊 **Sucesso! App Monolítico no Ar**

Parabéns! Seu **CryptoNinja** está funcionando como uma aplicação monolítica perfeita:

- ✅ **Uma única URL** serve frontend + backend
- ✅ **Zero configuração CORS** 
- ✅ **Deploy simples** em qualquer plataforma
- ✅ **Custo otimizado** - uma instância só
- ✅ **Manutenção fácil** - código unificado

**Agora é só focar no trading! 🥷💰**

---
**🥷 CryptoNinja - Aplicação Monolítica Perfeita para Deploy Simples!**
