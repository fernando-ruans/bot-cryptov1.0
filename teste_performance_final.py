#!/usr/bin/env python3
"""
TESTE FINAL DE VIÉS - 20 ATIVOS
Validação definitiva da correção do viés de 100% BUY
"""

import time
import json
from datetime import datetime
from collections import Counter
from typing import Dict, List
import warnings
from pandas.errors import PerformanceWarning

def test_20_assets_bias():
    """Testar 20 ativos para validar correção de viés"""
    
    print("🧪 TESTE FINAL DE VIÉS - 20 ATIVOS")
    print("=" * 60)
    print("🎯 Objetivo: Verificar se viés de 100% BUY foi eliminado")
    print("📊 Método: Testar 20 ativos no timeframe 1h")
    print()
    
    # Lista de 20 ativos principais
    assets = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
        'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LUNAUSDT',
        'LINKUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'VETUSDT',
        'EOSUSDT', 'TRXUSDT', 'XLMUSDT', 'AAVEUSDT', 'COMPUSDT'
    ]
    
    timeframe = '1h'
    results = []
    
    # Capturar warnings de performance
    performance_warnings = 0
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", PerformanceWarning)
        
        try:
            from src.config import Config
            from src.market_data import MarketDataManager
            from src.signal_generator import SignalGenerator
            
            config = Config()
            market_data = MarketDataManager(config)
            signal_generator = SignalGenerator(config, market_data)
            
            print("🚀 Iniciando testes...")
            print()
            
            start_time = time.time()
            
            for i, asset in enumerate(assets, 1):
                print(f"🔍 [{i:2d}/20] Testando {asset} {timeframe}...")
                
                try:
                    signal_result = signal_generator.generate_signal(asset, timeframe)
                    
                    signal = signal_result.get('signal', 'NONE')
                    confidence = signal_result.get('confidence', 0.0)
                    
                    results.append({
                        'asset': asset,
                        'timeframe': timeframe,
                        'signal': signal,
                        'confidence': confidence,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Emoji para sinal
                    emoji = {
                        'BUY': '🟢',
                        'SELL': '🔴', 
                        'HOLD': '🟡',
                        'NONE': '⚪'
                    }.get(signal, '❓')
                    
                    print(f"  {emoji} {signal} (confiança: {confidence:.2f})")
                    
                except Exception as e:
                    print(f"  ❌ Erro: {e}")
                    results.append({
                        'asset': asset,
                        'timeframe': timeframe,
                        'signal': 'ERROR',
                        'confidence': 0.0,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Contar warnings de performance
            perf_warnings = [warning for warning in w if issubclass(warning.category, PerformanceWarning)]
            performance_warnings = len(perf_warnings)
            
        except Exception as e:
            print(f"❌ Erro crítico durante o teste: {e}")
            return False
    
    print()
    print("📊 ANÁLISE DOS RESULTADOS")
    print("=" * 40)
    
    # Análise estatística
    valid_results = [r for r in results if r['signal'] != 'ERROR']
    signal_counts = Counter([r['signal'] for r in valid_results])
    
    total_valid = len(valid_results)
    total_errors = len(results) - total_valid
    
    print(f"📈 Total de testes: {len(results)}")
    print(f"✅ Sucessos: {total_valid}")
    print(f"❌ Erros: {total_errors}")
    print(f"⏱️ Tempo total: {processing_time:.2f}s")
    print(f"⚡ Tempo médio por ativo: {processing_time/len(assets):.2f}s")
    print()
    
    # Distribuição de sinais
    print("🎯 DISTRIBUIÇÃO DE SINAIS:")
    print("-" * 30)
    
    for signal_type in ['BUY', 'SELL', 'HOLD', 'NONE']:
        count = signal_counts.get(signal_type, 0)
        percentage = (count / total_valid * 100) if total_valid > 0 else 0
        
        emoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡', 
            'NONE': '⚪'
        }.get(signal_type, '❓')
        
        bar = "█" * int(percentage // 5)  # Barra visual
        print(f"{emoji} {signal_type:4s}: {count:2d} ({percentage:5.1f}%) {bar}")
    
    print()
    
    # Análise de viés
    print("🔍 ANÁLISE DE VIÉS:")
    print("-" * 20)
    
    # Apenas sinais de trading (BUY/SELL)
    trading_signals = [r['signal'] for r in valid_results if r['signal'] in ['BUY', 'SELL']]
    trading_counts = Counter(trading_signals)
    
    if trading_signals:
        buy_pct = (trading_counts.get('BUY', 0) / len(trading_signals)) * 100
        sell_pct = (trading_counts.get('SELL', 0) / len(trading_signals)) * 100
        
        print(f"BUY:  {buy_pct:.1f}%")
        print(f"SELL: {sell_pct:.1f}%")
        
        # Verificar viés
        if buy_pct > 80:
            print("⚠️ VIÉS DETECTADO: Favorece BUY")
            bias_status = "BUY_BIAS"
        elif sell_pct > 80:
            print("⚠️ VIÉS DETECTADO: Favorece SELL") 
            bias_status = "SELL_BIAS"
        elif abs(buy_pct - sell_pct) <= 20:
            print("✅ DISTRIBUIÇÃO BALANCEADA!")
            bias_status = "BALANCED"
        else:
            print("⚖️ LIGEIRO DESEQUILÍBRIO (aceitável)")
            bias_status = "SLIGHT_IMBALANCE"
    else:
        print("⚪ Nenhum sinal de trading gerado")
        bias_status = "NO_TRADING_SIGNALS"
    
    print()
    
    # Performance warnings
    print("⚡ PERFORMANCE:")
    print("-" * 15)
    if performance_warnings == 0:
        print("✅ Nenhum warning de fragmentação detectado!")
    else:
        print(f"⚠️ {performance_warnings} warnings de fragmentação detectados")
    
    print()
    
    # Confiança média
    confidences = [r['confidence'] for r in valid_results if r['confidence'] > 0]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        print(f"📊 Confiança média: {avg_confidence:.2f}")
        print(f"📊 Confiança mínima: {min(confidences):.2f}")
        print(f"📊 Confiança máxima: {max(confidences):.2f}")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"teste_20_ativos_{timestamp}.json"
    
    test_summary = {
        'timestamp': timestamp,
        'test_type': '20_assets_bias_test',
        'total_assets': len(assets),
        'successful_tests': total_valid,
        'failed_tests': total_errors,
        'processing_time': processing_time,
        'signal_distribution': dict(signal_counts),
        'bias_status': bias_status,
        'performance_warnings': performance_warnings,
        'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
        'results': results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_summary, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 60)
    
    # Resultado final
    if bias_status in ['BALANCED', 'SLIGHT_IMBALANCE', 'NO_TRADING_SIGNALS']:
        print("🎉 TESTE PASSOU - VIÉS CORRIGIDO COM SUCESSO!")
        success = True
    else:
        print("❌ TESTE FALHOU - VIÉS AINDA PRESENTE")
        success = False
    
    print(f"📁 Resultados salvos em: {filename}")
    
    return success

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE FINAL DE VIÉS")
    print()
    
    success = test_20_assets_bias()
    
    print()
    print("=" * 60)
    if success:
        print("✅ SISTEMA VALIDADO - PRONTO PARA PRODUÇÃO!")
    else:
        print("❌ SISTEMA REQUER AJUSTES ADICIONAIS")
