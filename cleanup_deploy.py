#!/usr/bin/env python3
"""
CryptoNinja 🥷 - Limpeza de Deploy
Remove arquivos de teste, debug e outros desnecessários para produção
"""

import os
import shutil
from pathlib import Path

def cleanup_for_deploy():
    """Limpar projeto para deploy"""
    
    print("🥷 CryptoNinja - Limpeza para Deploy")
    print("=" * 60)
    
    # Arquivos essenciais que devem ser mantidos
    keep_files = {
        # Aplicação principal
        'main.py',
        'requirements.txt',
        '.env',
        '.env.example',
        
        # Scripts de deploy
        'deploy_setup.py',
        'deploy_users.sql',
        'env.template',
        'schema_simples.sql',
        
        # Documentação essencial
        'README.md',
        'GUIA_DEPLOY.md',
        'SISTEMA_COMPLETO_FINAL.md',
        
        # Estrutura Git
        '.git',
        '.gitignore',
        
        # Pastas essenciais
        'src',
        'templates',
        'static',
        'logs',
        'data',
        'models',
        '__pycache__'
    }
    
    # Padrões de arquivos para remover
    remove_patterns = [
        'debug_*.py',
        'test_*.py',
        'step_debug*.py',
        'tech_debug*.py',
        'simple_debug*.py',
        'quick_test*.py',
        'final_system_test*.py',
        'full_test*.py',
        'simple_demo*.py',
        'demo_notifications*.py',
        'force_signal*.py',
        'fix_*.py',
        'validate_system*.py',
        'train_ai_model*.py',
        'calculate_usd_variations*.py',
        'change_app_name*.py',
        
        # Arquivos de saída/log
        '*.txt',
        '*.html',
        
        # Backups
        'main_backup.py',
        'main_simple.py',
        'setup_database.py',
        'setup_postgresql_schema.sql',
        
        # Relatórios antigos
        'RELATORIO_*.md',
        'RESUMO_*.md',
        'PAPER_TRADING_COMPLETO.md',
        'SETUP_POSTGRESQL.md',
        'SETUP_POSTGRESQL_CONCLUIDO.md',
        'CRYPTONINJA_FINAL_REPORT.md',
        'GUIA_DE_USO.md',
        'GUIA_USO_RAPIDO.md',
        'README_SIMPLIFICADO.md'
    ]
    
    # Contar arquivos removidos
    removed_count = 0
    kept_count = 0
    
    # Percorrer todos os arquivos no diretório raiz
    for item in os.listdir('.'):
        item_path = Path(item)
        
        # Pular diretórios essenciais
        if item in keep_files:
            kept_count += 1
            continue
            
        # Verificar se o arquivo deve ser removido
        should_remove = False
        
        for pattern in remove_patterns:
            if item_path.match(pattern):
                should_remove = True
                break
        
        if should_remove:
            try:
                if item_path.is_file():
                    os.remove(item)
                    print(f"🗑️  Removido: {item}")
                    removed_count += 1
                elif item_path.is_dir() and item not in keep_files:
                    # Não remover diretórios importantes
                    continue
            except Exception as e:
                print(f"❌ Erro ao remover {item}: {e}")
        else:
            kept_count += 1
    
    # Limpar __pycache__ recursivamente
    cleanup_pycache()
    
    print("=" * 60)
    print(f"✅ Limpeza concluída!")
    print(f"🗑️  Arquivos removidos: {removed_count}")
    print(f"📁 Arquivos mantidos: {kept_count}")
    print("=" * 60)
    
    # Mostrar estrutura final
    show_final_structure()

def cleanup_pycache():
    """Remover todos os diretórios __pycache__"""
    print("\n🧹 Limpando cache Python...")
    
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"🗑️  Removido: {pycache_path}")
            except Exception as e:
                print(f"❌ Erro ao remover {pycache_path}: {e}")

def show_final_structure():
    """Mostrar estrutura final do projeto"""
    print("\n📁 ESTRUTURA FINAL DO PROJETO:")
    print("=" * 40)
    
    # Listar apenas arquivos Python e principais
    important_files = []
    
    for item in sorted(os.listdir('.')):
        if os.path.isfile(item):
            if item.endswith(('.py', '.sql', '.md', '.txt', '.env', '.json', '.yml', '.yaml')):
                important_files.append(f"📄 {item}")
        elif os.path.isdir(item) and not item.startswith('.') and item != '__pycache__':
            important_files.append(f"📁 {item}/")
    
    for item in important_files[:20]:  # Mostrar apenas os primeiros 20
        print(item)
    
    if len(important_files) > 20:
        print(f"... e mais {len(important_files) - 20} itens")

def create_gitignore():
    """Criar .gitignore otimizado para produção"""
    gitignore_content = """# CryptoNinja 🥷 - .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local
.env.production
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/*.log
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db

# Testing (manter limpo para produção)
test_*.py
debug_*.py
*_test.py
*_debug.py

# Temporary files
*.tmp
*.temp
training_output.txt
debug_output.txt
debug_results*.txt

# Models (se muito grandes)
models/*.pkl
models/*.joblib
models/*.h5

# Cache
.cache/
.pytest_cache/
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("📝 .gitignore atualizado para produção")

def create_production_readme():
    """Criar README.md focado em produção"""
    readme_content = """# 🥷 CryptoNinja - Stealth Trading AI

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
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📖 README.md atualizado para produção")

def main():
    """Função principal"""
    try:
        # Confirmar limpeza
        print("🥷 CryptoNinja - Preparação para Deploy")
        print("=" * 60)
        print("⚠️  Esta operação removerá arquivos de teste e debug.")
        print("📁 Arquivos essenciais serão mantidos.")
        print()
        
        resposta = input("🤔 Continuar com a limpeza? (s/N): ").lower().strip()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            cleanup_for_deploy()
            create_gitignore()
            create_production_readme()
            
            print("\n🎉 PROJETO PRONTO PARA DEPLOY!")
            print("=" * 60)
            print("📦 Estrutura limpa e otimizada")
            print("📝 Documentação atualizada")
            print("🔐 .gitignore configurado")
            print()
            print("🚀 Próximos passos:")
            print("   1. Revisar arquivos mantidos")
            print("   2. Testar aplicação localmente")
            print("   3. Fazer commit das mudanças")
            print("   4. Executar deploy conforme GUIA_DEPLOY.md")
            
        else:
            print("❌ Limpeza cancelada pelo usuário")
            
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada")
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")

if __name__ == "__main__":
    main()
