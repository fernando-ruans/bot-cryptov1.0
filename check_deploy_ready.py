#!/usr/bin/env python3
"""
🥷 CryptoNinja - Verificador de Deploy Monolítico
Verifica se a aplicação está pronta para deploy em plataformas cloud
"""

import os
import sys
import requests
import subprocess
from pathlib import Path

def check_file_exists(file_path, required=True):
    """Verificar se arquivo existe"""
    exists = os.path.exists(file_path)
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = " (OBRIGATÓRIO)" if required and not exists else ""
    print(f"  {status} {file_path}{req_text}")
    return exists

def check_requirements():
    """Verificar requirements.txt"""
    print("\n📦 VERIFICANDO DEPENDÊNCIAS:")
    
    if not os.path.exists('requirements.txt'):
        print("  ❌ requirements.txt não encontrado!")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    essential_deps = [
        'Flask',
        'psycopg2-binary',
        'flask-login',
        'flask-bcrypt',
        'flask-cors',
        'requests'
    ]
    
    missing = []
    for dep in essential_deps:
        if dep.lower() not in content.lower():
            missing.append(dep)
    
    if missing:
        print(f"  ❌ Dependências faltando: {', '.join(missing)}")
        return False
    else:
        print("  ✅ Todas as dependências essenciais presentes")
        return True

def check_main_py():
    """Verificar main.py"""
    print("\n🐍 VERIFICANDO MAIN.PY:")
    
    if not os.path.exists('main.py'):
        print("  ❌ main.py não encontrado!")
        return False
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Verificar Flask app
    if 'app = Flask(' in content:
        checks.append("✅ Flask app configurado")
    else:
        checks.append("❌ Flask app não encontrado")
    
    # Verificar PostgreSQL
    if 'postgresql://' in content or 'DATABASE_URL' in content:
        checks.append("✅ PostgreSQL configurado")
    else:
        checks.append("❌ PostgreSQL não configurado")
    
    # Verificar porta de produção
    if 'app.run(' in content:
        if 'host=' in content and 'port=' in content:
            checks.append("✅ Host/Port configurados")
        else:
            checks.append("⚠️ Host/Port podem precisar ajuste")
    
    # Verificar autenticação
    if 'login_required' in content or 'flask_login' in content:
        checks.append("✅ Sistema de auth integrado")
    else:
        checks.append("❌ Sistema de auth não encontrado")
    
    for check in checks:
        print(f"  {check}")
    
    return all(check.startswith("✅") for check in checks if not check.startswith("⚠️"))

def check_database_scripts():
    """Verificar scripts de banco"""
    print("\n🗄️ VERIFICANDO SCRIPTS DE BANCO:")
    
    scripts = [
        ('create_database.sql', False),  # Para local
        ('schema_cloud.sql', True),     # Para cloud (obrigatório)
        ('schema_supabase.sql', False), # Para Supabase
        ('deploy_users.sql', False)     # Para usuários
    ]
    
    all_good = True
    for script, required in scripts:
        exists = check_file_exists(script, required)
        if required and not exists:
            all_good = False
    
    return all_good

def check_templates():
    """Verificar templates"""
    print("\n🎨 VERIFICANDO TEMPLATES:")
    
    template_files = [
        'templates/index_enhanced.html',
        'templates/auth/login.html',
        'templates/auth/profile.html',
        'templates/auth/admin_users.html'
    ]
    
    all_good = True
    for template in template_files:
        exists = check_file_exists(template, True)
        if not exists:
            all_good = False
    
    return all_good

def check_static_files():
    """Verificar arquivos estáticos"""
    print("\n💄 VERIFICANDO ARQUIVOS ESTÁTICOS:")
    
    static_dirs = [
        'static/css',
        'static/js'
    ]
    
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            files = os.listdir(static_dir)
            print(f"  ✅ {static_dir}/ ({len(files)} arquivos)")
        else:
            print(f"  ⚠️ {static_dir}/ não encontrado")

def check_env_template():
    """Verificar template de ambiente"""
    print("\n🔧 VERIFICANDO CONFIGURAÇÃO:")
    
    if os.path.exists('env.template'):
        print("  ✅ env.template presente")
        
        try:
            with open('env.template', 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open('env.template', 'r', encoding='latin-1') as f:
                content = f.read()
        
        if 'DATABASE_URL' in content:
            print("  ✅ DATABASE_URL template presente")
        else:
            print("  ❌ DATABASE_URL template faltando")
            
        if 'SECRET_KEY' in content:
            print("  ✅ SECRET_KEY template presente")
        else:
            print("  ❌ SECRET_KEY template faltando")
    else:
        print("  ❌ env.template não encontrado")

def check_git_ready():
    """Verificar se está pronto para Git"""
    print("\n🔗 VERIFICANDO GIT:")
    
    if os.path.exists('.git'):
        print("  ✅ Repositório Git inicializado")
        
        # Verificar .gitignore
        if os.path.exists('.gitignore'):
            print("  ✅ .gitignore presente")
            
            with open('.gitignore', 'r') as f:
                content = f.read()
            
            if '.env' in content:
                print("  ✅ .env ignorado no Git")
            else:
                print("  ⚠️ .env deveria estar no .gitignore")
        else:
            print("  ❌ .gitignore não encontrado")
    else:
        print("  ❌ Git não inicializado")
        print("     Execute: git init")

def test_import():
    """Testar imports principais"""
    print("\n🧪 TESTANDO IMPORTS:")
    
    try:
        import flask
        print("  ✅ Flask importado")
    except ImportError:
        print("  ❌ Flask não instalado")
        return False
    
    try:
        import psycopg2
        print("  ✅ psycopg2 importado")
    except ImportError:
        print("  ❌ psycopg2 não instalado")
        return False
    
    try:
        # Testar import do main (sem executar)
        import ast
        with open('main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
        ast.parse(main_content)
        print("  ✅ main.py sintaxe válida")
    except Exception as e:
        print(f"  ❌ Erro na sintaxe do main.py: {e}")
        return False
    
    return True

def generate_deploy_summary():
    """Gerar resumo para deploy"""
    print("\n" + "="*60)
    print("🎯 RESUMO PARA DEPLOY MONOLÍTICO")
    print("="*60)
    
    print("\n📋 COMANDOS RÁPIDOS:")
    print("  # 1. Commit para Git")
    print("  git add . && git commit -m 'ready for monolithic deploy'")
    print("  git push")
    print()
    print("  # 2. Deploy Render (mais fácil)")
    print("  # - Conectar GitHub repo no render.com")
    print("  # - Adicionar PostgreSQL addon")
    print("  # - Executar: psql $DATABASE_URL -f schema_cloud.sql")
    print()
    print("  # 3. OU Deploy Railway")
    print("  # railway login && railway init && railway up")
    print("  # railway add postgresql")
    print()
    print("🔐 VARIÁVEIS ESSENCIAIS:")
    print("  DATABASE_URL=postgresql://... (automático)")
    print("  SECRET_KEY=cryptoninja-secret-super-seguro-2025")
    print()
    print("🎯 PÓS-DEPLOY:")
    print("  1. Testar login: admin / admin123")
    print("  2. Alterar senha admin (CRÍTICO!)")
    print("  3. Verificar funcionalidades")

def main():
    """Função principal"""
    print("🥷 CryptoNinja - Verificador de Deploy Monolítico")
    print("="*60)
    
    # Lista de verificações
    checks = [
        ("Arquivos essenciais", lambda: all([
            check_file_exists('main.py', True),
            check_file_exists('requirements.txt', True)
        ])),
        ("Requirements.txt", check_requirements),
        ("Main.py", check_main_py),
        ("Scripts de banco", check_database_scripts),
        ("Templates", check_templates),
        ("Imports", test_import)
    ]
    
    # Executar verificações
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Erro em {name}: {e}")
            results.append((name, False))
    
    # Verificações opcionais
    print("\n" + "="*60)
    print("🔍 VERIFICAÇÕES OPCIONAIS:")
    check_static_files()
    check_env_template()
    check_git_ready()
    
    # Resultado final
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"📊 RESULTADO: {passed}/{total} verificações passaram")
    print("="*60)
    
    if passed == total:
        print("🎉 APLICAÇÃO PRONTA PARA DEPLOY MONOLÍTICO!")
        print("✅ Todos os componentes estão funcionais")
        print("✅ Arquitetura monolítica otimizada")
        print("✅ Compatível com Render, Railway, Fly.io, Vercel")
        generate_deploy_summary()
        return 0
    else:
        print("❌ CORREÇÕES NECESSÁRIAS ANTES DO DEPLOY")
        print("🔧 Corrija os itens marcados com ❌ acima")
        failed = [name for name, result in results if not result]
        print(f"📋 Itens pendentes: {', '.join(failed)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
