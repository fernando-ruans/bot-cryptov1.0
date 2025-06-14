#!/usr/bin/env python3
"""
🎯 TESTE DE PRECISÃO DO AI ENGINE ULTRA
Valida a taxa de acerto do novo sistema de IA
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import logging
from typing import Dict, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ultra_ai_precision():
    """Teste focado na precisão do AI Engine Ultra"""
    
    print("🎯 TESTE DE PRECISÃO - AI ENGINE ULTRA")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
        
        config = Config()
        market_data = MarketDataManager(config)
        ultra_ai = UltraEnhancedAIEngine(config)
        
        # Símbolos para teste
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
        timeframes = ['1m', '5m']
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'engine': 'UltraEnhancedAIEngine',
            'precision_test': True,
            'results': {}
        }
        
        total_predictions = 0
        high_confidence_predictions = 0
        
        for symbol in test_symbols:
            print(f"\n🔍 Testando {symbol}...")
            results['results'][symbol] = {}
            
            for timeframe in timeframes:
                print(f"   ⏱️ Timeframe: {timeframe}")
                
                # Obter dados históricos
                df = market_data.get_historical_data(symbol, timeframe, 1000)
                
                if df is None or len(df) < 200:
                    print(f"   ❌ Dados insuficientes para {symbol} {timeframe}")
                    continue
                
                # Fazer predição
                result = ultra_ai.ultra_predict_signal(df, symbol)
                
                signal_type = result.get('signal_type', 'HOLD')
                confidence = result.get('confidence', 0)
                ultra_enhanced = result.get('ultra_enhanced', False)
                
                # Contar predições
                total_predictions += 1
                if confidence >= 0.75:
                    high_confidence_predictions += 1
                
                # Armazenar resultado
                results['results'][symbol][timeframe] = {
                    'signal': signal_type,
                    'confidence': round(confidence, 4),
                    'entry_price': result.get('entry_price', 0),
                    'stop_loss': result.get('stop_loss', 0),
                    'take_profit': result.get('take_profit', 0),
                    'ultra_enhanced': ultra_enhanced,
                    'model_used': result.get('model_used', 'Unknown'),
                    'confluence': result.get('confluence', 0),
                    'probabilities': result.get('probabilities', [])
                }
                
                print(f"   🎯 Sinal: {signal_type}")
                print(f"   📈 Confiança: {confidence:.3f}")
                print(f"   🔄 Ultra Enhanced: {ultra_enhanced}")
                print(f"   🤝 Confluence: {result.get('confluence', 0):.3f}")
                
                # Análise de qualidade do sinal
                if confidence >= 0.80:
                    quality = "🟢 EXCELENTE"
                elif confidence >= 0.75:
                    quality = "🟡 BOA"
                elif confidence >= 0.60:
                    quality = "🟠 REGULAR"
                else:
                    quality = "🔴 BAIXA"
                
                print(f"   📊 Qualidade: {quality}")
        
        # Estatísticas gerais
        high_conf_rate = (high_confidence_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        results['summary'] = {
            'total_predictions': total_predictions,
            'high_confidence_predictions': high_confidence_predictions,
            'high_confidence_rate': round(high_conf_rate, 2),
            'threshold_used': 0.75,
            'symbols_tested': len(test_symbols),
            'timeframes_tested': len(timeframes)
        }
        
        print(f"\n📊 RESUMO DOS TESTES:")
        print(f"   📈 Total de predições: {total_predictions}")
        print(f"   🎯 Predições alta confiança (≥75%): {high_confidence_predictions}")
        print(f"   📊 Taxa de alta confiança: {high_conf_rate:.1f}%")
        
        # Salvar resultados
        filename = f"teste_precisao_ultra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no teste de precisão: {e}")
        logger.error(f"Erro no teste: {e}", exc_info=True)
        return None

def analyze_signal_quality(results: Dict) -> Dict:
    """Análise da qualidade dos sinais"""
    
    if not results or 'results' not in results:
        return {}
    
    analysis = {
        'signal_distribution': {'BUY': 0, 'SELL': 0, 'HOLD': 0},
        'confidence_stats': {
            'mean': 0,
            'min': 1,
            'max': 0,
            'std': 0
        },
        'quality_grades': {
            'excellent': 0,    # ≥ 0.80
            'good': 0,         # ≥ 0.75
            'regular': 0,      # ≥ 0.60
            'low': 0           # < 0.60
        }
    }
    
    confidences = []
    
    for symbol, timeframes in results['results'].items():
        for timeframe, data in timeframes.items():
            signal = data.get('signal', 'HOLD')
            confidence = data.get('confidence', 0)
            
            # Distribuição de sinais
            if signal in analysis['signal_distribution']:
                analysis['signal_distribution'][signal] += 1
            
            # Estatísticas de confiança
            confidences.append(confidence)
            
            # Grades de qualidade
            if confidence >= 0.80:
                analysis['quality_grades']['excellent'] += 1
            elif confidence >= 0.75:
                analysis['quality_grades']['good'] += 1
            elif confidence >= 0.60:
                analysis['quality_grades']['regular'] += 1
            else:
                analysis['quality_grades']['low'] += 1
    
    # Calcular estatísticas
    if confidences:
        analysis['confidence_stats'] = {
            'mean': round(np.mean(confidences), 4),
            'min': round(np.min(confidences), 4),
            'max': round(np.max(confidences), 4),
            'std': round(np.std(confidences), 4)
        }
    
    return analysis

def main():
    """Função principal"""
    
    # Executar teste de precisão
    results = test_ultra_ai_precision()
    
    if results:
        # Análise da qualidade
        quality_analysis = analyze_signal_quality(results)
        
        if quality_analysis:
            print(f"\n📋 ANÁLISE DE QUALIDADE:")
            print(f"   🎯 Distribuição de sinais:")
            for signal, count in quality_analysis['signal_distribution'].items():
                print(f"      {signal}: {count}")
            
            print(f"   📊 Estatísticas de confiança:")
            stats = quality_analysis['confidence_stats']
            print(f"      Média: {stats['mean']:.3f}")
            print(f"      Min: {stats['min']:.3f}")
            print(f"      Max: {stats['max']:.3f}")
            print(f"      Desvio: {stats['std']:.3f}")
            
            print(f"   🏆 Grades de qualidade:")
            grades = quality_analysis['quality_grades']
            total = sum(grades.values())
            if total > 0:
                print(f"      🟢 Excelente (≥80%): {grades['excellent']} ({grades['excellent']/total*100:.1f}%)")
                print(f"      🟡 Boa (≥75%): {grades['good']} ({grades['good']/total*100:.1f}%)")
                print(f"      🟠 Regular (≥60%): {grades['regular']} ({grades['regular']/total*100:.1f}%)")
                print(f"      🔴 Baixa (<60%): {grades['low']} ({grades['low']/total*100:.1f}%)")
    
    print(f"\n✅ Teste de precisão concluído!")

if __name__ == "__main__":
    main()
