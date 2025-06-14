#!/usr/bin/env python3
"""
🔍 RELATÓRIO DOS MOTORES DE IA DISPONÍVEIS
Analisa quais engines de IA estão disponíveis no projeto
"""

import os
import sys
from pathlib import Path

def analyze_ai_engines():
    """Analisa os diferentes motores de IA disponíveis"""
    
    print("🧠 ANÁLISE DOS MOTORES DE IA DISPONÍVEIS")
    print("=" * 60)
    
    # Localizar todos os arquivos de engine
    ai_engines = [
        {"file": "src/ai_engine.py", "name": "AI Engine Principal", "class": "AITradingEngine"},
        {"file": "src/ai_engine_deploy.py", "name": "AI Engine Deploy", "class": "AITradingEngine"},
        {"file": "src/ai_engine_original.py", "name": "AI Engine Original", "class": "AITradingEngine"},
        {"file": "ai_engine_enhanced.py", "name": "AI Engine Melhorado", "class": "EnhancedAIEngine"}
    ]
    
    current_engine = None
    
    # Verificar qual está sendo usado no main.py
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            main_content = f.read()
            
        if "from src.ai_engine import AITradingEngine" in main_content:
            current_engine = "src/ai_engine.py"
            print(f"🎯 ENGINE ATUAL: src/ai_engine.py (AITradingEngine)")
        elif "from ai_engine_enhanced import EnhancedAIEngine" in main_content:
            current_engine = "ai_engine_enhanced.py"
            print(f"🎯 ENGINE ATUAL: ai_engine_enhanced.py (EnhancedAIEngine)")
        else:
            print("❓ ENGINE ATUAL: Não foi possível determinar")
            
    except Exception as e:
        print(f"❌ Erro ao analisar main.py: {e}")
    
    print()
    print("📋 ENGINES DISPONÍVEIS:")
    print("-" * 40)
    
    for engine in ai_engines:
        file_path = engine["file"]
        engine_name = engine["name"]
        class_name = engine["class"]
        
        if os.path.exists(file_path):
            # Verificar tamanho do arquivo
            size_kb = os.path.getsize(file_path) / 1024
            
            # Verificar se é o engine atual
            status = "🟢 ATIVO" if file_path == current_engine else "⚪ DISPONÍVEL"
            
            print(f"{status} {engine_name}")
            print(f"    📁 Arquivo: {file_path}")
            print(f"    🏷️  Classe: {class_name}")
            print(f"    📊 Tamanho: {size_kb:.1f} KB")
            
            # Analisar conteúdo básico
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Contar features/métodos importantes
                features = []
                if "LSTM" in content or "lstm" in content:
                    features.append("LSTM")
                if "XGBoost" in content or "xgb" in content:
                    features.append("XGBoost")
                if "RandomForest" in content:
                    features.append("RandomForest")
                if "enhanced" in content.lower():
                    features.append("Enhanced Features")
                if "regime" in content.lower():
                    features.append("Market Regime")
                if "correlation" in content.lower():
                    features.append("Correlation Analysis")
                if "volume" in content.lower():
                    features.append("Volume Analysis")
                if "candlestick" in content.lower():
                    features.append("Candlestick Patterns")
                if "multi" in content.lower() and "timeframe" in content.lower():
                    features.append("Multi-Timeframe")
                
                if features:
                    print(f"    🔧 Features: {', '.join(features)}")
                else:
                    print(f"    🔧 Features: Básicas")
                    
            except Exception as e:
                print(f"    ❌ Erro ao analisar: {str(e)[:30]}...")
                
            print()
        else:
            print(f"❌ INDISPONÍVEL {engine_name}")
            print(f"    📁 Arquivo não encontrado: {file_path}")
            print()
    
    # Verificar dependências
    print("🔗 DEPENDÊNCIAS DETECTADAS:")
    print("-" * 30)
    
    dependencies = []
    try:
        with open("requirements.txt", "r") as f:
            req_content = f.read()
            
        if "tensorflow" in req_content.lower():
            dependencies.append("TensorFlow")
        if "torch" in req_content.lower():
            dependencies.append("PyTorch")
        if "xgboost" in req_content.lower():
            dependencies.append("XGBoost")
        if "sklearn" in req_content.lower() or "scikit-learn" in req_content.lower():
            dependencies.append("Scikit-learn")
        if "ta-lib" in req_content.lower():
            dependencies.append("TA-Lib")
        if "pandas" in req_content.lower():
            dependencies.append("Pandas")
        if "numpy" in req_content.lower():
            dependencies.append("NumPy")
            
        for dep in dependencies:
            print(f"✅ {dep}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar dependências: {e}")
    
    # Recomendações
    print()
    print("💡 RECOMENDAÇÕES:")
    print("-" * 20)
    
    if current_engine == "src/ai_engine.py":
        print("🎯 Você está usando o ENGINE PRINCIPAL")
        print("✅ Este engine tem todas as melhorias implementadas")
        print("✅ Inclui LSTM, Market Regime, Correlation Analysis")
        print("✅ Otimizado para produção")
        print()
        print("🔄 ALTERNATIVAS:")
        print("   • ai_engine_enhanced.py - Features ainda mais avançadas")
        print("   • src/ai_engine_deploy.py - Versão simplificada para deploy")
        
    elif current_engine == "ai_engine_enhanced.py":
        print("🚀 Você está usando o ENGINE MELHORADO")
        print("✅ Features mais avançadas")
        print("✅ Multi-timeframe analysis")
        print("✅ Candlestick patterns")
        print("✅ Feature interactions")
        
    else:
        print("⚠️  Engine não identificado ou usando versão personalizada")
        print("💡 Considere usar src/ai_engine.py para melhor desempenho")
    
    print()
    print("🔧 PARA ALTERNAR ENGINES:")
    print("1. Edite main.py")
    print("2. Altere a linha de import")
    print("3. Exemplo: from ai_engine_enhanced import EnhancedAIEngine")
    print("4. Altere a inicialização: ai_engine = EnhancedAIEngine(config)")

if __name__ == "__main__":
    analyze_ai_engines()
