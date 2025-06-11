#!/usr/bin/env python3
"""
🥷 CryptoNinja - Verificação Final para Deploy
Verifica se todas as dependências e configurações estão corretas.
"""

import sys
import importlib
import os
from pathlib import Path

def check_dependencies():
    """Verifica todas as dependências críticas."""    critical_deps = [
        'flask', 'flask_cors', 'flask_login', 'flask_sqlalchemy', 
        'flask_bcrypt', 'flask_socketio', 'psycopg2', 'sqlalchemy',
        'dotenv', 'requests', 'ccxt', 'pandas', 'numpy',
        'ta', 'psutil', 'sklearn', 'xgboost', 'lightgbm', 'textblob',
        'joblib', 'eventlet', 'werkzeug'
    ]
    
    print("🔍 Verificando dependências críticas...")
    
    for dep in critical_deps:        try:
            # Correção específica para alguns módulos
            if dep == 'flask_cors':
                module = importlib.import_module('flask_cors')
            elif dep == 'dotenv':
                module = importlib.import_module('dotenv')
            else:
                module = importlib.import_module(dep.replace('_', '.'))
                
            if hasattr(module, '__version__'):
                version = module.__version__
            else:
                version = "✓"
            print(f"  ✅ {dep}: {version}")
        except ImportError as e:
            print(f"  ❌ {dep}: FALTANDO - {e}")
            return False
    
    return True

def check_files():
    """Verifica se todos os arquivos necessários existem."""
    required_files = [
        'main.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'src/ai_engine.py',
        'src/database.py',
        'src/config.py',
        'templates/index.html',
        'static/css',
        'static/js'
    ]
    
    print("\n📁 Verificando arquivos necessários...")
    
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}: FALTANDO")
            return False
    
    return True

def check_env_vars():
    """Verifica variáveis de ambiente necessárias."""
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'FLASK_ENV'
    ]
    
    print("\n🔧 Verificando variáveis de ambiente...")
    
    # Carrega .env se existir
    if Path('.env').exists():
        from dotenv import load_dotenv
        load_dotenv()
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mostra apenas os primeiros caracteres por segurança
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ⚠️  {var}: NÃO DEFINIDA (será definida no deploy)")
            missing_vars.append(var)
    
    return len(missing_vars) == 0 or input(f"\nContinuar sem {missing_vars}? (y/n): ").lower() == 'y'

def test_ai_engine():
    """Testa o AI Engine."""
    print("\n🤖 Testando AI Engine...")
      try:
        sys.path.append('src')
        from ai_engine import AITradingEngine
        from config import Config
        
        config = Config()
        engine = AITradingEngine(config)
        print("  ✅ AI Engine criado com sucesso")
        
        # Teste básico de geração de sinal
        signal = engine.generate_signal('BTCUSDT', test_mode=True)
        if signal and 'signal' in signal:
            print(f"  ✅ Sinal gerado: {signal['signal_type']} (confiança: {signal['confidence']})")
        else:
            print("  ⚠️  Sinal gerado mas sem dados válidos")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no AI Engine: {e}")
        return False

def main():
    """Executa todas as verificações."""
    print("🥷 CryptoNinja - Verificação Final para Deploy")
    print("=" * 50)
    
    checks = [
        ("Dependências", check_dependencies),
        ("Arquivos", check_files),
        ("Variáveis de Ambiente", check_env_vars),
        ("AI Engine", test_ai_engine)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erro em {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DAS VERIFICAÇÕES:")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 PRONTO PARA DEPLOY!")
        print("\nPróximos passos:")
        print("1. Commit as alterações: git add . && git commit -m 'Fix: Added missing dependencies'")
        print("2. Deploy no Render ou plataforma escolhida")
        print("3. Configure as variáveis de ambiente na plataforma")
    else:
        print("⚠️  PROBLEMAS ENCONTRADOS - Corrija antes do deploy")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
