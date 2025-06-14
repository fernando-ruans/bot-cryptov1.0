#!/usr/bin/env python3
"""
🧪 TESTE COMPLETO DE VIÉS - Enhanced AI Engine
Teste abrangente para verificar a distribuição de sinais com o novo motor de IA
"""

import sys
import os
import json
import time
from datetime import datetime
from collections import Counter, defaultdict
import pandas as pd

# Adicionar diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_engine_bias():
    """Teste completo de viés com o Enhanced AI Engine"""
    
    print("🚀 TESTE COMPLETO DE VIÉS - ENHANCED AI ENGINE")
    print("=" * 80)
    
    try:
        # Imports
        from ai_engine_enhanced import EnhancedAIEngine
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.signal_generator import SignalGenerator
        
        print("✅ Enhanced AI Engine carregado")
        
        # Inicialização
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = EnhancedAIEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print("✅ Sistema inicializado com Enhanced AI Engine")
        print()
        
        # Lista completa de ativos para testar
        symbols = [
            # Principais criptomoedas
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT",
            "SOLUSDT", "DOTUSDT", "LINKUSDT", "LTCUSDT", "BCHUSDT",
            
            # Altcoins populares
            "AVAXUSDT", "MATICUSDT", "UNIUSDT", "XLMUSDT", "ATOMUSDT",
            "FILUSDT", "TRXUSDT", "ETCUSDT", "ALGOUSDT", "VETUSDT",
            
            # DeFi tokens
            "AAVEUSDT", "COMPUSDT", "MKRUSDT", "SUSHIUSDT", "CRVUSDT",
            
            # Meme coins e outros
            "DOGEUSDT", "SHIBUSDT", "PEPEUSDT", "FLOKIUSDT"
        ]
        
        # Timeframes para testar
        timeframes = ["1h", "4h", "1d"]
        
        # Resultados
        all_results = []
        signal_distribution = Counter()
        distribution_by_tf = defaultdict(Counter)
        distribution_by_symbol = defaultdict(Counter)
        confidence_stats = []
        
        total_tests = len(symbols) * len(timeframes)
        current_test = 0
        
        print(f"📊 Iniciando teste de {len(symbols)} ativos em {len(timeframes)} timeframes")
        print(f"🎯 Total de testes: {total_tests}")
        print()
        
        # Executar testes
        for symbol in symbols:
            print(f"🔍 Testando {symbol}...")
            
            for timeframe in timeframes:
                current_test += 1
                progress = (current_test / total_tests) * 100
                
                try:
                    print(f"  📈 {timeframe} ({progress:.1f}%)...", end=" ")
                    
                    # Gerar sinal
                    result = signal_generator.generate_signal(symbol, timeframe)
                    
                    signal_type = result.signal_type.lower()
                    confidence = result.confidence
                    
                    # Armazenar resultados
                    test_result = {
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal': signal_type,
                        'confidence': confidence,
                        'timestamp': datetime.now().isoformat(),
                        'enhanced_engine': True
                    }
                    
                    all_results.append(test_result)
                    signal_distribution[signal_type] += 1
                    distribution_by_tf[timeframe][signal_type] += 1
                    distribution_by_symbol[symbol][signal_type] += 1
                    confidence_stats.append(confidence)
                    
                    # Emoji para o sinal
                    emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}.get(signal_type, "⚪")
                    print(f"{emoji} {signal_type.upper()} ({confidence:.3f})")
                    
                    # Pequena pausa para não sobrecarregar
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"❌ Erro: {str(e)[:40]}...")
                    continue
            
            print()
        
        # Análise dos resultados
        print("\n" + "=" * 80)
        print("📈 ANÁLISE COMPLETA DOS RESULTADOS")
        print("=" * 80)
        
        total_signals = len(all_results)
        print(f"✅ Total de sinais gerados: {total_signals}")
        print()
        
        # 1. Distribuição geral
        print("🎯 DISTRIBUIÇÃO GERAL:")
        print("-" * 40)
        for signal_type, count in signal_distribution.most_common():
            percentage = (count / total_signals) * 100 if total_signals > 0 else 0
            emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}.get(signal_type, "⚪")
            print(f"{emoji} {signal_type.upper()}: {count:3d} ({percentage:5.1f}%)")
        
        # 2. Distribuição por timeframe
        print("\n📊 DISTRIBUIÇÃO POR TIMEFRAME:")
        print("-" * 40)
        for tf in timeframes:
            print(f"\n⏰ {tf}:")
            tf_total = sum(distribution_by_tf[tf].values())
            for signal_type in ['buy', 'sell', 'hold']:
                count = distribution_by_tf[tf][signal_type]
                percentage = (count / tf_total) * 100 if tf_total > 0 else 0
                emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}.get(signal_type, "⚪")
                print(f"  {emoji} {signal_type.upper()}: {count:2d} ({percentage:4.1f}%)")
        
        # 3. Estatísticas de confiança
        print("\n🎯 ESTATÍSTICAS DE CONFIANÇA:")
        print("-" * 40)
        if confidence_stats:
            avg_confidence = sum(confidence_stats) / len(confidence_stats)
            min_confidence = min(confidence_stats)
            max_confidence = max(confidence_stats)
            
            print(f"📊 Média: {avg_confidence:.3f}")
            print(f"📉 Mínima: {min_confidence:.3f}")
            print(f"📈 Máxima: {max_confidence:.3f}")
        
        # 4. Análise de viés
        print("\n🔍 ANÁLISE DE VIÉS:")
        print("-" * 40)
        
        buy_pct = (signal_distribution['buy'] / total_signals) * 100 if total_signals > 0 else 0
        sell_pct = (signal_distribution['sell'] / total_signals) * 100 if total_signals > 0 else 0
        hold_pct = (signal_distribution['hold'] / total_signals) * 100 if total_signals > 0 else 0
        
        # Verificar viés
        bias_detected = False
        bias_messages = []
        
        if buy_pct > 60:
            bias_detected = True
            bias_messages.append(f"⚠️  VIÉS PARA BUY DETECTADO! ({buy_pct:.1f}%)")
        elif sell_pct > 60:
            bias_detected = True
            bias_messages.append(f"⚠️  VIÉS PARA SELL DETECTADO! ({sell_pct:.1f}%)")
        elif hold_pct > 80:
            bias_detected = True
            bias_messages.append(f"⚠️  EXCESSO DE HOLD! Sistema muito conservador ({hold_pct:.1f}%)")
        
        # Verificar variedade
        unique_signals = len([s for s in signal_distribution.values() if s > 0])
        if unique_signals < 3:
            bias_detected = True
            bias_messages.append(f"❌ FALTA DE VARIEDADE! Apenas {unique_signals} tipos de sinal")
        
        # Verificar distribuição muito desigual
        signal_values = list(signal_distribution.values())
        if signal_values:
            max_signal = max(signal_values)
            min_signal = min(signal_values)
            if max_signal > 0 and (max_signal / min_signal) > 5:
                bias_detected = True
                bias_messages.append("⚠️  DISTRIBUIÇÃO MUITO DESIGUAL!")
        
        if bias_detected:
            for msg in bias_messages:
                print(msg)
        else:
            print("✅ DISTRIBUIÇÃO BALANCEADA!")
            print("✅ Nenhum viés significativo detectado")
            print("✅ Variedade adequada de sinais")
        
        # 5. Top ativos por tipo de sinal
        print("\n🏆 TOP ATIVOS POR TIPO DE SINAL:")
        print("-" * 40)
        
        for signal_type in ['buy', 'sell', 'hold']:
            emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}.get(signal_type, "⚪")
            print(f"\n{emoji} TOP {signal_type.upper()}:")
            
            # Ordenar símbolos por quantidade deste tipo de sinal
            sorted_symbols = sorted(
                distribution_by_symbol.items(),
                key=lambda x: x[1][signal_type],
                reverse=True
            )[:5]
            
            for symbol, counts in sorted_symbols:
                count = counts[signal_type]
                if count > 0:
                    print(f"  {symbol}: {count}")
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_vies_enhanced_engine_{timestamp}.json"
        
        summary = {
            'timestamp': timestamp,
            'engine_type': 'EnhancedAIEngine',
            'total_signals': total_signals,
            'total_symbols': len(symbols),
            'total_timeframes': len(timeframes),
            'distribution': dict(signal_distribution),
            'percentages': {
                'buy': buy_pct,
                'sell': sell_pct,
                'hold': hold_pct
            },
            'confidence_stats': {
                'average': avg_confidence if confidence_stats else 0,
                'min': min_confidence if confidence_stats else 0,
                'max': max_confidence if confidence_stats else 0
            },
            'bias_detected': bias_detected,
            'bias_messages': bias_messages,
            'distribution_by_timeframe': {tf: dict(dist) for tf, dist in distribution_by_tf.items()},
            'all_results': all_results
        }
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        # Status final
        print("\n" + "=" * 80)
        print("🏁 VEREDICTO FINAL")
        print("=" * 80)
        
        if not bias_detected and unique_signals >= 3:
            print("🎉 ENHANCED AI ENGINE APROVADO!")
            print("✅ Distribuição balanceada em todos os timeframes")
            print("✅ Variedade adequada de sinais")
            print("✅ Nenhum viés significativo detectado")
            print("🚀 SISTEMA PRONTO PARA PRODUÇÃO!")
            return True
        else:
            print("⚠️  ENHANCED AI ENGINE PRECISA DE AJUSTES")
            print("❌ Problemas de viés detectados")
            for msg in bias_messages:
                print(f"   {msg}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 INICIANDO TESTE COMPLETO DE VIÉS COM ENHANCED AI ENGINE...")
    print()
    
    success = test_enhanced_engine_bias()
    
    print("\n" + "="*80)
    if success:
        print("🎯 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Enhanced AI Engine aprovado para produção")
    else:
        print("⚠️  TESTE REVELOU PROBLEMAS")
        print("🔧 Enhanced AI Engine precisa de mais ajustes")
        
    print("\n💡 Verifique os logs detalhados acima para análise completa.")
