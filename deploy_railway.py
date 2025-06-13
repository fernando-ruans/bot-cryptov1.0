#!/usr/bin/env python3
"""
🚂 Script Automatizado de Deploy para Railway
Prepara e faz deploy do CryptoNinja Trading Bot
"""

import os
import sys
import subprocess
import json

def print_step(step_num, description):
    """Imprimir passo colorido"""
    print(f"\n🚂 PASSO {step_num}: {description}")
    print("=" * 50)

def create_railway_config():
    """Criar configuração Railway"""
    print_step(1, "Criando configuração Railway")
    
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
    
    try:
        with open("railway.json", "w", encoding="utf-8") as f:
            json.dump(railway_config, f, indent=2)
        print("✅ railway.json criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar railway.json: {e}")
        return False

def check_railway_cli():
    """Verificar Railway CLI"""
    print_step(2, "Verificando Railway CLI")
    
    try:
        result = subprocess.run("railway --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI instalado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI não encontrado")
            print("📦 Instalando Railway CLI...")
            install_cmd = "npm install -g @railway/cli"
            return subprocess.run(install_cmd, shell=True).returncode == 0
    except:
        print("❌ Node.js/npm não encontrado")
        print("📝 Instale Node.js primeiro: https://nodejs.org")
        print("📝 Ou instale Railway CLI manualmente:")
        print("   curl -fsSL https://railway.app/install.sh | sh")
        return False

def railway_login():
    """Login Railway"""
    print_step(3, "Login Railway")
    
    print("🔑 Iniciando login no Railway...")
    result = subprocess.run("railway login", shell=True)
    return result.returncode == 0

def create_railway_project():
    """Criar projeto Railway"""
    print_step(4, "Criando projeto Railway")
    
    print("📝 Criando novo projeto...")
    result = subprocess.run("railway init", shell=True)
    return result.returncode == 0

def deploy_railway():
    """Deploy Railway"""
    print_step(5, "Deploy Railway")
    
    print("🚀 Fazendo deploy...")
    result = subprocess.run("railway up", shell=True)
    return result.returncode == 0

def setup_railway_database():
    """Configurar banco PostgreSQL Railway"""
    print_step(6, "Configurando banco PostgreSQL")
    
    print("🗄️ Adicionando PostgreSQL...")
    result = subprocess.run("railway add postgresql", shell=True)
    
    if result.returncode == 0:
        print("✅ PostgreSQL adicionado com sucesso!")
        print("📝 DATABASE_URL será configurada automaticamente")
        return True
    else:
        print("⚠️ Erro ao adicionar PostgreSQL. Pode adicionar manualmente no dashboard.")
        return True  # Não bloquear o deploy

def main():
    """Função principal"""
    print("🚂 CryptoNinja Trading Bot - Deploy Railway")
    print("=" * 50)
    print("📋 Este script irá:")
    print("   1. Criar configuração Railway")
    print("   2. Verificar/instalar Railway CLI")
    print("   3. Fazer login no Railway")
    print("   4. Criar projeto")
    print("   5. Fazer deploy")
    print("   6. Configurar banco PostgreSQL")
    print()
    
    response = input("🤔 Deseja continuar? (s/n): ").lower().strip()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Deploy cancelado")
        return
    
    # Verificar pasta do projeto
    if not os.path.exists("main.py"):
        print("❌ Execute na pasta raiz do projeto!")
        return
    
    # Executar steps
    steps = [
        create_railway_config,
        check_railway_cli,
        railway_login,
        create_railway_project,
        deploy_railway,
        setup_railway_database
    ]
    
    for step_func in steps:
        if not step_func():
            print(f"❌ Falha no passo: {step_func.__name__}")
            return
    
    print("\n" + "=" * 50)
    print("🎉 DEPLOY RAILWAY CONCLUÍDO!")
    print("🌍 Bot online em Railway!")
    print("📊 Acesse: railway open")
    print("🔧 Configure variáveis: railway variables")
    print("=" * 50)

if __name__ == "__main__":
    main()
