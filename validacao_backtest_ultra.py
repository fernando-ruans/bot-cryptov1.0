#!/usr/bin/env python3
"""
🎯 VALIDAÇÃO DE BACKTEST - AI ENGINE ULTRA
Testa a precisão real do sistema com dados históricos
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_signal_accuracy(df: pd.DataFrame, prediction_periods: int = 3) -> Dict:
    """Calcular a acurácia real dos sinais baseado em dados históricos"""
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
        
        config = Config()
        market_data = MarketDataManager(config)
        ultra_ai = UltraEnhancedAIEngine(config)
        
        results = []
        
        # Dividir dados em janelas para simular predições em tempo real
        window_size = 200
        step_size = 10
        
        for i in range(window_size, len(df) - prediction_periods, step_size):
            # Dados até o momento da predição
            train_data = df.iloc[:i].copy()
            
            # Fazer predição
            prediction = ultra_ai.ultra_predict_signal(train_data, 'BACKTEST')
            
            if not prediction.get('ultra_enhanced', False):
                continue  # Só considerar predições ultra
            
            signal_type = prediction.get('signal_type', 'HOLD')
            confidence = prediction.get('confidence', 0)
            
            # Só avaliar sinais com alta confiança
            if confidence < 0.75:
                continue
            
            # Calcular retorno real nos próximos períodos
            current_price = train_data['close'].iloc[-1]
            future_price = df['close'].iloc[i + prediction_periods]
            actual_return = (future_price - current_price) / current_price * 100
            
            # Determinar se a predição estava correta
            threshold = 0.5  # 0.5% de movimento mínimo
            
            if signal_type == 'BUY':
                correct = actual_return > threshold
            elif signal_type == 'SELL':
                correct = actual_return < -threshold
            else:  # HOLD
                correct = abs(actual_return) <= threshold
            
            results.append({
                'timestamp': df.index[i],
                'signal': signal_type,
                'confidence': confidence,
                'predicted_direction': signal_type,
                'actual_return': actual_return,
                'correct': correct,
                'entry_price': current_price,
                'future_price': future_price
            })
        
        # Calcular estatísticas
        if not results:
            return {'accuracy': 0, 'total_signals': 0, 'message': 'No valid signals'}
        
        total_signals = len(results)
        correct_signals = sum(1 for r in results if r['correct'])
        accuracy = (correct_signals / total_signals) * 100
        
        # Estatísticas por tipo de sinal
        buy_signals = [r for r in results if r['signal'] == 'BUY']
        sell_signals = [r for r in results if r['signal'] == 'SELL']
        hold_signals = [r for r in results if r['signal'] == 'HOLD']
        
        stats = {
            'overall_accuracy': round(accuracy, 2),
            'total_signals': total_signals,
            'correct_signals': correct_signals,
            'buy_accuracy': round((sum(1 for r in buy_signals if r['correct']) / len(buy_signals) * 100) if buy_signals else 0, 2),
            'sell_accuracy': round((sum(1 for r in sell_signals if r['correct']) / len(sell_signals) * 100) if sell_signals else 0, 2),
            'hold_accuracy': round((sum(1 for r in hold_signals if r['correct']) / len(hold_signals) * 100) if hold_signals else 0, 2),
            'signal_distribution': {
                'BUY': len(buy_signals),
                'SELL': len(sell_signals),
                'HOLD': len(hold_signals)
            },
            'avg_confidence': round(np.mean([r['confidence'] for r in results]), 3),
            'avg_return_correct': round(np.mean([r['actual_return'] for r in results if r['correct']]), 3),
            'avg_return_incorrect': round(np.mean([r['actual_return'] for r in results if not r['correct']]), 3),
            'details': results[-10:]  # Últimos 10 sinais para análise
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro no cálculo de acurácia: {e}")
        return {'accuracy': 0, 'error': str(e)}

def run_backtest_validation():
    """Executar validação completa de backtest"""
    
    print("🎯 VALIDAÇÃO DE BACKTEST - AI ENGINE ULTRA")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        
        config = Config()
        market_data = MarketDataManager(config)
        
        # Símbolos para teste
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
        timeframes = ['5m', '15m']
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'backtest_validation': True,
            'symbols': {},
            'summary': {}
        }
        
        all_accuracies = []
        total_signals_count = 0
        
        for symbol in test_symbols:
            print(f"\n🔍 Validando {symbol}...")
            validation_results['symbols'][symbol] = {}
            
            for timeframe in timeframes:
                print(f"   ⏱️ Timeframe: {timeframe}")
                
                # Obter dados históricos extensos
                df = market_data.get_historical_data(symbol, timeframe, 2000)
                
                if df is None or len(df) < 500:
                    print(f"   ❌ Dados insuficientes para {symbol} {timeframe}")
                    continue
                
                # Calcular acurácia
                accuracy_stats = calculate_signal_accuracy(df)
                
                if accuracy_stats.get('total_signals', 0) == 0:
                    print(f"   ⚠️ Nenhum sinal válido gerado")
                    continue
                
                validation_results['symbols'][symbol][timeframe] = accuracy_stats
                
                # Estatísticas
                accuracy = accuracy_stats.get('overall_accuracy', 0)
                total_signals = accuracy_stats.get('total_signals', 0)
                
                all_accuracies.append(accuracy)
                total_signals_count += total_signals
                
                print(f"   🎯 Acurácia: {accuracy:.1f}%")
                print(f"   📊 Total de sinais: {total_signals}")
                print(f"   💪 Confiança média: {accuracy_stats.get('avg_confidence', 0):.3f}")
                
                # Análise por tipo de sinal
                buy_acc = accuracy_stats.get('buy_accuracy', 0)
                sell_acc = accuracy_stats.get('sell_accuracy', 0)
                hold_acc = accuracy_stats.get('hold_accuracy', 0)
                
                print(f"   📈 BUY: {buy_acc:.1f}% | 📉 SELL: {sell_acc:.1f}% | ⏸️ HOLD: {hold_acc:.1f}%")
                
                # Qualidade da predição
                if accuracy >= 70:
                    quality = "🟢 EXCELENTE"
                elif accuracy >= 60:
                    quality = "🟡 BOA"
                elif accuracy >= 50:
                    quality = "🟠 REGULAR"
                else:
                    quality = "🔴 RUIM"
                
                print(f"   📊 Qualidade: {quality}")
        
        # Resumo geral
        if all_accuracies:
            avg_accuracy = np.mean(all_accuracies)
            min_accuracy = np.min(all_accuracies)
            max_accuracy = np.max(all_accuracies)
            
            validation_results['summary'] = {
                'average_accuracy': round(avg_accuracy, 2),
                'min_accuracy': round(min_accuracy, 2),
                'max_accuracy': round(max_accuracy, 2),
                'total_backtests': len(all_accuracies),
                'total_signals_evaluated': total_signals_count,
                'target_accuracy': 70.0,
                'target_met': avg_accuracy >= 70.0
            }
            
            print(f"\n📊 RESUMO GERAL:")
            print(f"   🎯 Acurácia média: {avg_accuracy:.1f}%")
            print(f"   📈 Melhor: {max_accuracy:.1f}%")
            print(f"   📉 Pior: {min_accuracy:.1f}%")
            print(f"   📊 Total de sinais avaliados: {total_signals_count}")
            print(f"   🎯 Meta de 70%: {'✅ ATINGIDA' if avg_accuracy >= 70 else '❌ NÃO ATINGIDA'}")
        
        # Salvar resultados
        filename = f"validacao_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        return validation_results
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        logger.error(f"Erro na validação: {e}", exc_info=True)
        return None

def main():
    """Função principal"""
    
    results = run_backtest_validation()
    
    if results:
        summary = results.get('summary', {})
        avg_accuracy = summary.get('average_accuracy', 0)
        
        print(f"\n🏆 RESULTADO FINAL:")
        if avg_accuracy >= 70:
            print(f"✅ SUCESSO! Acurácia média de {avg_accuracy:.1f}% atinge a meta de 70%+")
        elif avg_accuracy >= 60:
            print(f"🟡 QUASE LÁ! Acurácia de {avg_accuracy:.1f}% está próxima da meta")
        else:
            print(f"❌ PRECISA MELHORAR! Acurácia de {avg_accuracy:.1f}% está abaixo da meta")
        
        print(f"\n📋 PRÓXIMOS PASSOS:")
        if avg_accuracy < 70:
            print("   🔧 Ajustar parâmetros do modelo")
            print("   📊 Adicionar mais features")
            print("   🎯 Aumentar threshold de confiança")
            print("   💡 Otimizar ensemble models")
        else:
            print("   🚀 Sistema pronto para produção!")
            print("   📈 Considerar deploy com confiança")
    
    print(f"\n✅ Validação de backtest concluída!")

if __name__ == "__main__":
    main()
