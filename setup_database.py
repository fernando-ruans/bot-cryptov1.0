#!/usr/bin/env python3
"""
CryptoNinja 🥷 - Setup do Banco PostgreSQL
Script para configurar automaticamente o banco de dados
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Exibir banner do CryptoNinja"""
    print("=" * 70)
    print("🥷 CRYPTONINJA - SETUP POSTGRESQL")
    print("=" * 70)
    print()

def check_postgresql():
    """Verificar se PostgreSQL está disponível"""
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ PostgreSQL encontrado: {version}")
            return True
        else:
            print("❌ PostgreSQL não encontrado no PATH")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ PostgreSQL não instalado ou não disponível")
        return False

def test_connection(host="localhost", port="5432", user="postgres", password="admin"):
    """Testar conexão com PostgreSQL"""
    print(f"🔗 Testando conexão: {user}@{host}:{port}")
    
    # Definir variável de ambiente para senha
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        result = subprocess.run([
            'psql', 
            f'-h', host,
            f'-p', port,
            f'-U', user,
            '-d', 'postgres',
            '-c', 'SELECT 1;'
        ], capture_output=True, text=True, timeout=15, env=env)
        
        if result.returncode == 0:
            print("✅ Conexão bem-sucedida!")
            return True
        else:
            print(f"❌ Erro na conexão: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout na conexão")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def run_sql_script(script_path, host="localhost", port="5432", user="postgres", password="admin"):
    """Executar script SQL"""
    print(f"📄 Executando script: {script_path}")
    
    if not os.path.exists(script_path):
        print(f"❌ Script não encontrado: {script_path}")
        return False
    
    # Definir variável de ambiente para senha
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        result = subprocess.run([
            'psql', 
            f'-h', host,
            f'-p', port,
            f'-U', user,
            '-d', 'postgres',
            '-f', script_path
        ], capture_output=True, text=True, timeout=120, env=env)
        
        if result.returncode == 0:
            print("✅ Script executado com sucesso!")
            if result.stdout:
                print("📋 Output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ Erro na execução: {result.stderr}")
            if result.stdout:
                print("📋 Output:")
                print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout na execução do script")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def setup_database_url():
    """Configurar URL do banco no arquivo .env"""
    env_path = Path('.env')
    database_url = "postgresql://postgres:admin@localhost:5432/cryptoninja_db"
    
    # Ler arquivo .env existente ou criar novo
    env_content = ""
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Adicionar ou atualizar DATABASE_URL
    lines = env_content.split('\n')
    found = False
    
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            lines[i] = f'DATABASE_URL={database_url}'
            found = True
            break
    
    if not found:
        lines.append(f'DATABASE_URL={database_url}')
    
    # Salvar arquivo .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Arquivo .env configurado com DATABASE_URL")

def verify_setup(host="localhost", port="5432", user="postgres", password="admin"):
    """Verificar se o setup foi bem-sucedido"""
    print("\n🔍 Verificando setup...")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    queries = [
        ("Banco cryptoninja_db", "SELECT current_database();"),
        ("Tabela users", "SELECT COUNT(*) FROM users;"),
        ("Tabela trades", "SELECT COUNT(*) FROM trades;"),
        ("Tabela signals", "SELECT COUNT(*) FROM signals;"),
        ("Usuário admin", "SELECT username FROM users WHERE is_admin = true;"),
    ]
    
    all_good = True
    
    for desc, query in queries:
        try:
            result = subprocess.run([
                'psql', 
                f'-h', host,
                f'-p', port,
                f'-U', user,
                '-d', 'cryptoninja_db',
                '-t', '-c', query
            ], capture_output=True, text=True, timeout=10, env=env)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                print(f"✅ {desc}: {output}")
            else:
                print(f"❌ {desc}: Erro")
                all_good = False
                
        except Exception as e:
            print(f"❌ {desc}: {e}")
            all_good = False
    
    return all_good

def main():
    """Função principal"""
    print_banner()
    
    # Configurações
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_USER = "postgres"
    DB_PASSWORD = "admin"
    
    # 1. Verificar PostgreSQL
    if not check_postgresql():
        print("\n💡 Para instalar PostgreSQL:")
        print("   Windows: https://www.postgresql.org/download/windows/")
        print("   Ubuntu: sudo apt install postgresql postgresql-contrib")
        print("   macOS: brew install postgresql")
        return False
    
    # 2. Testar conexão
    if not test_connection(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD):
        print("\n💡 Verifique se:")
        print("   • PostgreSQL está rodando")
        print("   • Usuário 'postgres' existe")
        print("   • Senha está correta (padrão: 'admin')")
        print("   • Porta 5432 está livre")
        return False
    
    # 3. Executar script SQL
    script_path = "setup_postgresql_schema.sql"
    if not run_sql_script(script_path, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD):
        print("\n❌ Falha na execução do script SQL")
        return False
    
    # 4. Configurar .env
    setup_database_url()
    
    # 5. Verificar setup
    if verify_setup(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD):
        print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print("📊 Banco de dados: cryptoninja_db")
        print("👤 Usuário admin: admin / ninja123")
        print("🎮 Usuário demo: demo / ninja123")
        print("⚠️  IMPORTANTE: Altere as senhas padrão!")
        print("=" * 70)
        print("\n🚀 Agora você pode executar o CryptoNinja:")
        print("   python main.py")
        return True
    else:
        print("\n❌ Problemas encontrados na verificação")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
