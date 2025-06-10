# 🥷 CryptoNinja - Stealth Trading AI

## 🚀 Sistema de Trading Automatizado com IA

### ✨ Características
- 🤖 Trading Bot com IA integrada
- 📊 Análise técnica e de sentimento em tempo real
- 💰 Paper Trading para testes seguros
- 🔐 Sistema de autenticação PostgreSQL
- 🎨 Interface ninja-themed moderna
- 📱 Dados de mercado Binance ao vivo

### 🏗️ Arquitetura
- **Backend:** Flask + PostgreSQL
- **Frontend:** Bootstrap 5 + JavaScript
- **IA:** Modelos de machine learning personalizados
- **APIs:** Integração Binance para dados reais
- **Auth:** Flask-Login + bcrypt

### ⚡ Quick Start

#### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 2. Configurar Banco PostgreSQL
```bash
# Executar scripts de setup
psql -f schema_simples.sql
psql -f deploy_users.sql
```

#### 3. Configurar Ambiente
```bash
# Copiar template
cp env.template .env

# Editar .env com suas configurações
```

#### 4. Executar Aplicação
```bash
python main.py
```

#### 5. Acessar Sistema
- **URL:** http://localhost:5000
- **Login:** admin / ninja123
- **Demo:** demo / ninja123

### 🔧 Deploy

Para deploy em produção, consulte o [Guia de Deploy](GUIA_DEPLOY.md).

Plataformas suportadas:
- ✅ Heroku
- ✅ Docker
- ✅ AWS / Digital Ocean
- ✅ Qualquer VPS com PostgreSQL

### 📖 Documentação

- [📋 Guia de Deploy](GUIA_DEPLOY.md) - Instruções completas
- [🎯 Sistema Completo](SISTEMA_COMPLETO_FINAL.md) - Visão geral

### 🔐 Segurança

⚠️ **IMPORTANTE:** Altere as senhas padrão após o primeiro deploy!

### 🎯 Funcionalidades

#### Trading
- Geração automática de sinais
- Paper trading em tempo real
- Stop loss e take profit
- Histórico completo de trades

#### Administração
- Painel administrativo
- Gestão de usuários
- Estatísticas do sistema
- Monitoramento em tempo real

#### Interface
- Dashboard interativo
- Gráficos em tempo real
- Notificações WebSocket
- Design responsivo

### 🛠️ Tecnologias

- **Python 3.9+**
- **Flask** - Framework web
- **PostgreSQL** - Banco de dados
- **Bootstrap 5** - Interface
- **Chart.js** - Gráficos
- **WebSocket** - Tempo real
- **bcrypt** - Criptografia

---

**CryptoNinja 🥷 - Desenvolvido para traders que valorizam tecnologia e resultados.**
