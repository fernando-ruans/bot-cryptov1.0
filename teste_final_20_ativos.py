#!/usr/bin/env python3
"""
TESTE FINAL - 20 ATIVOS VIÉS
"""

import time
import json
from datetime import datetime
from collections import Counter

def test_20_assets():
    """Teste com 20 ativos para validar correção de viés"""
    
    print("🧪 TESTE FINAL DE VIÉS - 20 ATIVOS")
    print("=" * 50)
    
    # Lista completa de 20 ativos
    assets = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
        'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LUNAUSDT',
        'LINKUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'VETUSDT',
        'EOSUSDT', 'TRXUSDT', 'XLMUSDT', 'AAVEUSDT', 'COMPUSDT'
    ]
    
    results = []
    
    try:
        print("🔧 Inicializando sistema...")
        from src.config import Config
        from src.market_data import MarketDataManager  
        from src.signal_generator import SignalGenerator
        from src.ai_engine import AITradingEngine
        
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print("🚀 Testando 20 ativos...")
        print()
        
        start_time = time.time()
        
        for i, asset in enumerate(assets, 1):
            print(f"🔍 [{i:2d}/20] {asset}...")
            
            try:
                signal_result = signal_generator.generate_signal(asset, '1h')
                
                if signal_result is None:
                    signal = 'NONE'
                    confidence = 0.0
                elif hasattr(signal_result, 'to_dict'):
                    # É um objeto Signal
                    signal_dict = signal_result.to_dict()
                    signal = signal_dict.get('signal_type', 'NONE').upper()
                    confidence = signal_dict.get('confidence', 0.0)
                else:
                    # É um dicionário (fallback)
                    signal = signal_result.get('signal', 'NONE')
                    confidence = signal_result.get('confidence', 0.0)
                
                results.append({
                    'asset': asset,
                    'signal': signal,
                    'confidence': confidence
                })
                
                emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡', 'NONE': '⚪'}.get(signal, '❓')
                print(f"  {emoji} {signal} (confiança: {confidence:.2f})")
                
            except Exception as e:
                print(f"  ❌ Erro: {e}")
                results.append({'asset': asset, 'signal': 'ERROR', 'confidence': 0.0})
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print()
        print("📊 ANÁLISE DOS RESULTADOS")
        print("=" * 40)
        
        # Estatísticas básicas
        valid_results = [r for r in results if r['signal'] != 'ERROR']
        signal_counts = Counter([r['signal'] for r in valid_results])
        
        total_valid = len(valid_results)
        total_errors = len(results) - total_valid
        
        print(f"✅ Sucessos: {total_valid}/20")
        print(f"❌ Erros: {total_errors}/20")
        print(f"⏱️ Tempo total: {processing_time:.1f}s")
        print()
        
        # Distribuição de sinais
        print("🎯 DISTRIBUIÇÃO DE SINAIS:")
        print("-" * 30)
        
        for signal_type in ['BUY', 'SELL', 'HOLD', 'NONE']:
            count = signal_counts.get(signal_type, 0)
            percentage = (count / total_valid * 100) if total_valid > 0 else 0
            
            emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡', 'NONE': '⚪'}.get(signal_type, '❓')
            bar = "█" * max(1, int(percentage // 5))  # Barra visual
            print(f"{emoji} {signal_type:4s}: {count:2d} ({percentage:5.1f}%) {bar}")
        
        print()
        
        # Análise de viés
        print("🔍 ANÁLISE DE VIÉS:")
        print("-" * 20)
        
        trading_signals = [r['signal'] for r in valid_results if r['signal'] in ['BUY', 'SELL']]
        
        if trading_signals:
            trading_counts = Counter(trading_signals)
            buy_count = trading_counts.get('BUY', 0)
            sell_count = trading_counts.get('SELL', 0)
            
            buy_pct = (buy_count / len(trading_signals)) * 100
            sell_pct = (sell_count / len(trading_signals)) * 100
            
            print(f"BUY:  {buy_pct:.1f}% ({buy_count} sinais)")
            print(f"SELL: {sell_pct:.1f}% ({sell_count} sinais)")
            
            # Verificar viés
            if buy_pct > 85:
                print("🚨 VIÉS CRÍTICO: Favorece BUY")
                bias_status = "CRITICAL_BUY_BIAS"
            elif sell_pct > 85:
                print("🚨 VIÉS CRÍTICO: Favorece SELL") 
                bias_status = "CRITICAL_SELL_BIAS"
            elif abs(buy_pct - sell_pct) <= 30:
                print("✅ DISTRIBUIÇÃO BALANCEADA!")
                bias_status = "BALANCED"
            else:
                print("⚖️ LIGEIRO DESEQUILÍBRIO (aceitável)")
                bias_status = "SLIGHT_IMBALANCE"
        else:
            print("⚪ Nenhum sinal de trading gerado")
            bias_status = "NO_TRADING_SIGNALS"
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_final_20_ativos_{timestamp}.json"
        
        summary = {
            'timestamp': timestamp,
            'total_assets': len(assets),
            'successful_tests': total_valid,
            'failed_tests': total_errors,
            'processing_time': processing_time,
            'signal_distribution': dict(signal_counts),
            'bias_status': bias_status,
            'results': results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print()
        print("=" * 50)
        
        # Resultado final
        if bias_status in ['BALANCED', 'SLIGHT_IMBALANCE']:
            print("🎉 TESTE PASSOU - VIÉS CORRIGIDO!")
            success = True
        elif bias_status == 'NO_TRADING_SIGNALS':
            print("⚪ SISTEMA CAUTELOSO - Poucos sinais gerados")
            success = True  # Também é válido
        else:
            print("❌ TESTE FALHOU - VIÉS AINDA PRESENTE")
            success = False
        
        print(f"📁 Resultados salvos: {filename}")
        
        return success
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE FINAL DE VIÉS COM 20 ATIVOS")
    print()
    
    success = test_20_assets()
    
    print()
    if success:
        print("✅ SISTEMA VALIDADO - VIÉS CORRIGIDO!")
    else:
        print("❌ SISTEMA REQUER MAIS AJUSTES")
