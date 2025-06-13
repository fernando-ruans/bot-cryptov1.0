#!/usr/bin/env python3
"""
🚀 Script Automatizado de Deploy para Vercel
Prepara e faz deploy do CryptoNinja Trading Bot
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_step(step_num, description):
    """Imprimir passo colorido"""
    print(f"\n🚀 PASSO {step_num}: {description}")
    print("=" * 50)

def run_command(command, description):
    """Executar comando e mostrar resultado"""
    print(f"▶️ {description}")
    print(f"💻 Executando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sucesso!")
            if result.stdout:
                print(f"📤 Output: {result.stdout}")
        else:
            print(f"❌ Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False
    
    return True

def check_file_exists(filepath, description):
    """Verificar se arquivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {description} encontrado: {filepath}")
        return True
    else:
        print(f"❌ {description} não encontrado: {filepath}")
        return False

def setup_vercel_files():
    """Configurar arquivos para Vercel"""
    print_step(1, "Preparando arquivos para Vercel")
    
    # Verificar arquivos necessários
    files_check = [
        ("vercel.json", "Configuração Vercel"),
        ("vercel_app.py", "App otimizada para Vercel"),
        ("requirements_vercel.txt", "Requirements otimizados"),
        ("templates/dashboard.html", "Template principal"),
        ("static/js/dashboard.js", "JavaScript do dashboard")
    ]
    
    all_files_ok = True
    for filepath, description in files_check:
        if not check_file_exists(filepath, description):
            all_files_ok = False
    
    if not all_files_ok:
        print("❌ Alguns arquivos necessários estão faltando!")
        return False
    
    # Copiar arquivos otimizados
    if os.path.exists("vercel_app.py"):
        print("📋 Copiando vercel_app.py -> main.py")
        with open("vercel_app.py", "r", encoding="utf-8") as f:
            content = f.read()
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content)
    
    if os.path.exists("requirements_vercel.txt"):
        print("📋 Copiando requirements_vercel.txt -> requirements.txt")
        with open("requirements_vercel.txt", "r", encoding="utf-8") as f:
            content = f.read()
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(content)
    
    print("✅ Arquivos preparados com sucesso!")
    return True

def check_vercel_cli():
    """Verificar se Vercel CLI está instalado"""
    print_step(2, "Verificando Vercel CLI")
    
    try:
        result = subprocess.run("vercel --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI instalado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI não encontrado")
            print("📦 Instalando Vercel CLI...")
            return run_command("npm install -g vercel", "Instalar Vercel CLI")
    except:
        print("❌ Node.js/npm não encontrado")
        print("📝 Por favor, instale Node.js primeiro: https://nodejs.org")
        return False

def vercel_login():
    """Fazer login no Vercel"""
    print_step(3, "Login no Vercel")
    
    print("🔑 Iniciando login no Vercel...")
    print("📝 Uma página do navegador será aberta para autenticação")
    
    return run_command("vercel login", "Login no Vercel")

def deploy_to_vercel():
    """Fazer deploy no Vercel"""
    print_step(4, "Deploy no Vercel")
    
    print("🚀 Iniciando deploy em produção...")
    print("⏳ Isso pode levar alguns minutos...")
    
    return run_command("vercel --prod", "Deploy em produção")

def setup_environment_variables():
    """Configurar variáveis de ambiente"""
    print_step(5, "Configurando variáveis de ambiente")
    
    env_vars = [
        ("SECRET_KEY", "cryptoninja-vercel-prod-2025"),
        ("FLASK_ENV", "production")
    ]
    
    for var_name, var_value in env_vars:
        print(f"🔧 Configurando {var_name}")
        # Note: Vercel CLI will prompt for the value
        if not run_command(f'echo "{var_value}" | vercel env add {var_name} production', f"Adicionar {var_name}"):
            print(f"⚠️ Erro ao configurar {var_name}. Configure manualmente no dashboard do Vercel.")

def main():
    """Função principal"""
    print("🥷 CryptoNinja Trading Bot - Deploy Automático para Vercel")
    print("=" * 60)
    print("📋 Este script irá:")
    print("   1. Preparar arquivos para Vercel")
    print("   2. Verificar/instalar Vercel CLI")
    print("   3. Fazer login no Vercel")
    print("   4. Fazer deploy em produção")
    print("   5. Configurar variáveis de ambiente")
    print()
    
    # Confirmação do usuário
    response = input("🤔 Deseja continuar? (s/n): ").lower().strip()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Deploy cancelado pelo usuário")
        return
    
    # Verificar se estamos na pasta correta
    if not os.path.exists("main.py") and not os.path.exists("vercel_app.py"):
        print("❌ Execute este script na pasta raiz do projeto!")
        return
    
    # Executar steps
    steps = [
        setup_vercel_files,
        check_vercel_cli,
        vercel_login,
        deploy_to_vercel,
        setup_environment_variables
    ]
    
    for step_func in steps:
        if not step_func():
            print(f"❌ Falha no passo: {step_func.__name__}")
            print("🛠️ Corrija o erro e tente novamente")
            return
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
    print("🌍 Seu bot está online e acessível no mundo todo!")
    print("📊 Acesse o dashboard no URL fornecido pelo Vercel")
    print("🔧 Configure variáveis adicionais no dashboard do Vercel se necessário")
    print("📱 Teste as APIs: /api/health, /api/price/BTCUSDT, /api/signal/ETHUSDT")
    print("=" * 60)

if __name__ == "__main__":
    main()
