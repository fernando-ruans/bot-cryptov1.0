#!/usr/bin/env python3
"""
🎯 Script Final de Preparação para Deploy
Prepara o projeto para qualquer plataforma de deploy gratuito
"""

import os
import shutil
import json
from datetime import datetime

def print_banner():
    """Banner inicial"""
    print("🥷" + "=" * 58 + "🥷")
    print("🚀           CRYPTONINJA - DEPLOY PREPARATION            🚀")
    print("🥷" + "=" * 58 + "🥷")
    print("📅 Data:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()

def backup_original_files():
    """Fazer backup dos arquivos originais"""
    print("📦 BACKUP DOS ARQUIVOS ORIGINAIS")
    print("-" * 40)
    
    backup_files = [
        ("main.py", "main_original.py"),
        ("requirements.txt", "requirements_original.txt")
    ]
    
    for original, backup in backup_files:
        if os.path.exists(original):
            try:
                shutil.copy2(original, backup)
                print(f"✅ Backup criado: {original} -> {backup}")
            except Exception as e:
                print(f"⚠️ Erro no backup {original}: {e}")
        else:
            print(f"ℹ️ Arquivo {original} não encontrado")
    print()

def prepare_vercel():
    """Preparar para Vercel"""
    print("🔷 PREPARANDO PARA VERCEL")
    print("-" * 30)
    
    # Copiar app otimizada
    if os.path.exists("vercel_app.py"):
        print("📋 Copiando vercel_app.py -> main.py")
        shutil.copy2("vercel_app.py", "main.py")
    
    # Copiar requirements otimizados
    if os.path.exists("requirements_vercel.txt"):
        print("📋 Copiando requirements_vercel.txt -> requirements.txt")
        shutil.copy2("requirements_vercel.txt", "requirements.txt")
    
    # Verificar vercel.json
    if os.path.exists("vercel.json"):
        print("✅ vercel.json configurado")
    else:
        print("❌ vercel.json não encontrado!")
    
    print("✅ Preparação Vercel concluída")
    print()

def prepare_railway():
    """Preparar para Railway"""
    print("🚂 PREPARANDO PARA RAILWAY")
    print("-" * 30)
    
    # Criar railway.json se não existir
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python main.py",
            "healthcheckPath": "/api/health",
            "restartPolicyType": "ON_FAILURE"
        }
    }
    
    if not os.path.exists("railway.json"):
        with open("railway.json", "w", encoding="utf-8") as f:
            json.dump(railway_config, f, indent=2)
        print("✅ railway.json criado")
    else:
        print("✅ railway.json já existe")
    
    print("✅ Preparação Railway concluída")
    print()

def prepare_render():
    """Preparar para Render"""
    print("🟢 PREPARANDO PARA RENDER")
    print("-" * 30)
    
    # Verificar arquivos Render
    render_files = [
        ("render.yaml", "Configuração Render"),
        ("Procfile", "Procfile para Render")
    ]
    
    for filename, description in render_files:
        if os.path.exists(filename):
            print(f"✅ {description} encontrado")
        else:
            print(f"⚠️ {description} não encontrado")
    
    print("✅ Preparação Render concluída")
    print()

def check_project_structure():
    """Verificar estrutura do projeto"""
    print("🔍 VERIFICANDO ESTRUTURA DO PROJETO")
    print("-" * 40)
    
    required_files = [
        ("main.py", "Aplicação principal"),
        ("requirements.txt", "Dependências Python"),
        ("templates/dashboard.html", "Template principal"),
        ("static/js/dashboard.js", "JavaScript do frontend"),
        ("static/css/", "Estilos CSS"),
        ("src/", "Código fonte")
    ]
    
    all_ok = True
    for item, description in required_files:
        if os.path.exists(item):
            print(f"✅ {description}: {item}")
        else:
            print(f"❌ {description}: {item} - NÃO ENCONTRADO")
            all_ok = False
    
    print()
    if all_ok:
        print("🎉 Estrutura do projeto está completa!")
    else:
        print("⚠️ Alguns arquivos estão faltando. Verifique antes do deploy.")
    print()

def show_deploy_instructions():
    """Mostrar instruções de deploy"""
    print("📋 INSTRUÇÕES DE DEPLOY")
    print("-" * 25)
    
    platforms = [
        {
            "name": "🔷 VERCEL (Recomendado)",
            "commands": [
                "npm install -g vercel",
                "vercel login",
                "vercel --prod"
            ],
            "url": "https://vercel.com"
        },
        {
            "name": "🚂 RAILWAY",
            "commands": [
                "npm install -g @railway/cli",
                "railway login",
                "railway init",
                "railway up"
            ],
            "url": "https://railway.app"
        },
        {
            "name": "🟢 RENDER",
            "commands": [
                "# Deploy via Git:",
                "git add .",
                "git commit -m 'Deploy'",
                "git push origin main"
            ],
            "url": "https://render.com"
        }
    ]
    
    for platform in platforms:
        print(f"\n{platform['name']}")
        print(f"🌐 {platform['url']}")
        for cmd in platform['commands']:
            print(f"   {cmd}")
    
    print()

def create_deployment_checklist():
    """Criar checklist de deploy"""
    print("📝 CRIANDO CHECKLIST DE DEPLOY")
    print("-" * 35)
    
    checklist = """# 🚀 CHECKLIST DE DEPLOY - CRYPTONINJA

## ✅ PRÉ-DEPLOY
- [ ] Projeto testado localmente (`python main.py`)
- [ ] Arquivos de configuração criados
- [ ] Requirements.txt atualizado
- [ ] Código commitado no Git
- [ ] Variáveis de ambiente definidas

## 🔷 VERCEL
- [ ] Node.js instalado
- [ ] Vercel CLI instalado (`npm install -g vercel`)
- [ ] Login no Vercel (`vercel login`)
- [ ] Deploy (`vercel --prod`)
- [ ] Configurar variáveis de ambiente no dashboard

## 🚂 RAILWAY
- [ ] Railway CLI instalado
- [ ] Login no Railway (`railway login`)
- [ ] Projeto criado (`railway init`)
- [ ] Deploy (`railway up`)
- [ ] PostgreSQL configurado (opcional)

## 🟢 RENDER
- [ ] Repositório conectado no Render
- [ ] Web Service criado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy automático ativo

## 🗄️ BANCO DE DADOS (Opcional)
- [ ] Supabase: Projeto criado e DATABASE_URL configurada
- [ ] Railway: PostgreSQL addon adicionado
- [ ] Render: PostgreSQL service criado

## 🧪 PÓS-DEPLOY
- [ ] App acessível via URL
- [ ] Health check funcionando (`/api/health`)
- [ ] Dashboard carregando
- [ ] APIs respondendo (`/api/price/BTCUSDT`)
- [ ] Logs verificados

## 🔧 TROUBLESHOOTING
- [ ] Verificar logs da plataforma
- [ ] Testar endpoints individualmente
- [ ] Verificar variáveis de ambiente
- [ ] Conferir timeouts e limites

🎉 SEU BOT ESTÁ ONLINE!
"""
    
    with open("DEPLOY_CHECKLIST.md", "w", encoding="utf-8") as f:
        f.write(checklist)
    
    print("✅ Checklist criado: DEPLOY_CHECKLIST.md")
    print()

def main():
    """Função principal"""
    print_banner()
    
    print("🤔 Escolha a preparação:")
    print("1. 🔷 Vercel (Recomendado)")
    print("2. 🚂 Railway")
    print("3. 🟢 Render")
    print("4. 📦 Preparação completa (todas)")
    print("0. ❌ Cancelar")
    
    choice = input("\n👉 Digite sua escolha (1-4): ").strip()
    
    if choice == "0":
        print("❌ Cancelado pelo usuário")
        return
    
    # Sempre fazer backup e verificar estrutura
    backup_original_files()
    check_project_structure()
    
    if choice == "1":
        prepare_vercel()
    elif choice == "2":
        prepare_railway()
    elif choice == "3":
        prepare_render()
    elif choice == "4":
        prepare_vercel()
        prepare_railway()
        prepare_render()
    else:
        print("❌ Opção inválida")
        return
    
    create_deployment_checklist()
    show_deploy_instructions()
    
    print("🎉" + "=" * 58 + "🎉")
    print("🚀        PROJETO PRONTO PARA DEPLOY!                   🚀")
    print("📝        Siga o DEPLOY_CHECKLIST.md                   📝")
    print("🥷        Boa sorte com seu bot de trading!            🥷")
    print("🎉" + "=" * 58 + "🎉")

if __name__ == "__main__":
    main()
