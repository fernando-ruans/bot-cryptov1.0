#!/usr/bin/env python3
"""
🚀 TESTE FINAL - UltraEnhancedAIEngine com Ativos Reais do App
=============================================================

Este script testa a UltraEnhancedAIEngine implementada como engine principal
usando os 5 ativos principais configurados no app:
- BTCUSDT, ETHUSDT, ADAUSDT, XRPUSDT, SOLUSDT

Métricas avaliadas:
- Velocidade de resposta
- Qualidade dos sinais
- Confiança das predições
- Diversidade de sinais
- Performance geral

Autor: Sistema de IA
Data: 14/06/2025
"""

import sys
import os
import json
import time
from datetime import datetime
import asyncio

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
    print("✅ UltraEnhancedAIEngine importada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar UltraEnhancedAIEngine: {e}")
    sys.exit(1)

class TesteFinalApp:
    def __init__(self):
        """Inicializar teste com ativos reais do app"""
        # Ativos principais do app (definidos em vercel_app.py)
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT']
        
        # Timeframes testados
        self.timeframes = ['1m', '5m', '15m', '1h']
        
        # Configuração da engine
        self.config = {
            'ai_engine': {
                'confidence_threshold': 0.65,
                'max_signals_per_hour': 12,
                'enable_anti_bias': True,
                'enable_regime_detection': True,
                'enable_correlation_analysis': True,
                'enable_volume_analysis': True
            }
        }
        
        # Resultados
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'engine_name': 'UltraEnhancedAIEngine',
            'test_config': {
                'symbols': self.symbols,
                'timeframes': self.timeframes,
                'total_tests': len(self.symbols) * len(self.timeframes)
            },
            'performance_metrics': {},
            'signal_quality': {},
            'summary': {}
        }
        
        print(f"🎯 Teste Final - UltraEnhancedAIEngine")
        print(f"📊 Ativos: {', '.join(self.symbols)}")
        print(f"⏰ Timeframes: {', '.join(self.timeframes)}")
        print(f"🔢 Total de testes: {self.results['test_config']['total_tests']}")

    def gerar_dados_realistas(self, symbol, timeframe, periods=100):
        """Gerar dados OHLCV realistas para teste"""
        import random
        import numpy as np
        
        # Preços base aproximados (Junho 2025)
        base_prices = {
            'BTCUSDT': 70000,
            'ETHUSDT': 4000,
            'ADAUSDT': 0.45,
            'XRPUSDT': 0.55,
            'SOLUSDT': 145
        }
        
        base_price = base_prices.get(symbol, 50000)
        
        # Gerar dados com tendência realista
        data = []
        current_price = base_price
        
        for i in range(periods):
            # Volatilidade baseada no ativo
            volatility = {
                'BTCUSDT': 0.02,
                'ETHUSDT': 0.025,
                'ADAUSDT': 0.03,
                'XRPUSDT': 0.035,
                'SOLUSDT': 0.04
            }.get(symbol, 0.025)
            
            # Movimento de preço com tendência
            change = np.random.normal(0, volatility)
            current_price *= (1 + change)
            
            # OHLC com spreads realistas
            spread = current_price * 0.001
            high = current_price + random.uniform(0, spread * 2)
            low = current_price - random.uniform(0, spread * 2)
            open_price = current_price + random.uniform(-spread, spread)
            close = current_price
            
            # Volume baseado no ativo
            base_volume = {
                'BTCUSDT': 50000,
                'ETHUSDT': 80000,
                'ADAUSDT': 100000,
                'XRPUSDT': 120000,
                'SOLUSDT': 30000
            }.get(symbol, 50000)
            
            volume = base_volume * random.uniform(0.5, 2.0)
            
            data.append({
                'timestamp': int(time.time() * 1000) - (periods - i) * 60000,
                'open': round(open_price, 8),
                'high': round(high, 8),
                'low': round(low, 8),
                'close': round(close, 8),
                'volume': round(volume, 2)
            })
        
        return data

    def testar_engine_symbol_timeframe(self, symbol, timeframe):
        """Testar engine para um símbolo e timeframe específico"""
        try:
            print(f"\n🔍 Testando {symbol} - {timeframe}")
            
            # Inicializar engine
            engine = UltraEnhancedAIEngine(self.config)
            
            # Gerar dados de teste
            market_data = self.gerar_dados_realistas(symbol, timeframe)
            
            # Medir tempo de resposta
            start_time = time.time()
              # Converter dados para DataFrame
            import pandas as pd
            df = pd.DataFrame(market_data)
            
            # Gerar sinal usando o método correto
            signal = engine.ultra_predict_signal(df, symbol)
            
            response_time = time.time() - start_time
            
            # Analisar resultado
            test_result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'response_time': round(response_time, 4),
                'signal_generated': signal is not None,
                'signal_data': signal if signal else None,
                'success': True,
                'error': None
            }
            
            if signal:
                test_result.update({
                    'signal_type': signal.get('signal', 'unknown'),
                    'confidence': signal.get('confidence', 0),
                    'entry_price': signal.get('entry_price', 0),
                    'take_profit': signal.get('take_profit', 0),
                    'stop_loss': signal.get('stop_loss', 0),
                    'features_count': len(signal.get('analysis', {})),
                    'reasoning_length': len(signal.get('reasoning', '')),
                })
                
                print(f"   ✅ Sinal: {signal.get('signal')} | Confiança: {signal.get('confidence'):.3f} | Tempo: {response_time:.3f}s")
            else:
                print(f"   ⚠️  Nenhum sinal gerado | Tempo: {response_time:.3f}s")
            
            return test_result
            
        except Exception as e:
            error_result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'response_time': 0,
                'signal_generated': False,
                'signal_data': None,
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Erro: {str(e)}")
            return error_result

    def executar_teste_completo(self):
        """Executar teste completo em todos os símbolos e timeframes"""
        print(f"\n🚀 Iniciando Teste Final da UltraEnhancedAIEngine...")
        print(f"{'='*60}")
        
        all_results = []
        total_tests = len(self.symbols) * len(self.timeframes)
        current_test = 0
        
        start_time = time.time()
        
        for symbol in self.symbols:
            print(f"\n📈 Testando {symbol}")
            symbol_results = []
            
            for timeframe in self.timeframes:
                current_test += 1
                progress = (current_test / total_tests) * 100
                
                print(f"   [{current_test}/{total_tests}] ({progress:.1f}%) {timeframe}")
                
                result = self.testar_engine_symbol_timeframe(symbol, timeframe)
                symbol_results.append(result)
                all_results.append(result)
                  # Pequena pausa entre testes
                time.sleep(0.1)
            
            self.results['performance_metrics'][symbol] = symbol_results
        
        total_time = time.time() - start_time
        
        # Análise dos resultados
        self.analisar_resultados(all_results, total_time)
        
        return self.results

    def analisar_resultados(self, all_results, total_time):
        """Analisar e consolidar resultados"""
        print(f"\n📊 Analisando Resultados...")
        print(f"{'='*60}")
        
        # Métricas básicas
        total_tests = len(all_results)
        successful_tests = len([r for r in all_results if r['success']])
        signals_generated = len([r for r in all_results if r['signal_generated']])
        
        # Tempos de resposta
        response_times = [r['response_time'] for r in all_results if r['success']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Análise de sinais
        valid_signals = [r for r in all_results if r['signal_generated']]
        signal_types = {}
        confidence_scores = []
        
        for result in valid_signals:
            signal_type = result.get('signal_type', 'unknown')
            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
            
            confidence = result.get('confidence', 0)
            if confidence > 0:
                confidence_scores.append(confidence)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Análise por símbolo
        symbol_performance = {}
        for symbol in self.symbols:
            symbol_results = [r for r in all_results if r['symbol'] == symbol]
            symbol_signals = [r for r in symbol_results if r['signal_generated']]
            symbol_times = [r['response_time'] for r in symbol_results if r['success']]
            
            symbol_performance[symbol] = {
                'total_tests': len(symbol_results),
                'success_rate': len([r for r in symbol_results if r['success']]) / len(symbol_results),
                'signal_rate': len(symbol_signals) / len(symbol_results),
                'avg_response_time': sum(symbol_times) / len(symbol_times) if symbol_times else 0,
                'avg_confidence': sum([r.get('confidence', 0) for r in symbol_signals]) / len(symbol_signals) if symbol_signals else 0
            }
        
        # Consolidar resultados
        self.results['summary'] = {
            'total_time': round(total_time, 2),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests,
            'signals_generated': signals_generated,
            'signal_rate': signals_generated / total_tests,
            'performance': {
                'avg_response_time': round(avg_response_time, 4),
                'min_response_time': round(min_response_time, 4),
                'max_response_time': round(max_response_time, 4),
                'tests_per_second': round(total_tests / total_time, 2)
            },
            'signal_quality': {
                'avg_confidence': round(avg_confidence, 3),
                'signal_types': signal_types,
                'confidence_distribution': {
                    'high_confidence': len([c for c in confidence_scores if c >= 0.8]),
                    'medium_confidence': len([c for c in confidence_scores if 0.6 <= c < 0.8]),
                    'low_confidence': len([c for c in confidence_scores if c < 0.6])
                }
            },
            'symbol_performance': symbol_performance
        }
        
        self.results['signal_quality'] = valid_signals

    def imprimir_relatorio(self):
        """Imprimir relatório final"""
        summary = self.results['summary']
        
        print(f"\n🎯 RELATÓRIO FINAL - UltraEnhancedAIEngine")
        print(f"{'='*70}")
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   Tempo total: {summary['total_time']}s")
        print(f"   Testes realizados: {summary['total_tests']}")
        print(f"   Taxa de sucesso: {summary['success_rate']:.1%}")
        print(f"   Sinais gerados: {summary['signals_generated']} ({summary['signal_rate']:.1%})")
        
        print(f"\n⚡ PERFORMANCE:")
        perf = summary['performance']
        print(f"   Tempo médio: {perf['avg_response_time']}s")
        print(f"   Tempo mínimo: {perf['min_response_time']}s")
        print(f"   Tempo máximo: {perf['max_response_time']}s")
        print(f"   Testes/segundo: {perf['tests_per_second']}")
        
        print(f"\n🧠 QUALIDADE DOS SINAIS:")
        quality = summary['signal_quality']
        print(f"   Confiança média: {quality['avg_confidence']:.3f}")
        print(f"   Tipos de sinais: {quality['signal_types']}")
        print(f"   Alta confiança (≥0.8): {quality['confidence_distribution']['high_confidence']}")
        print(f"   Média confiança (0.6-0.8): {quality['confidence_distribution']['medium_confidence']}")
        print(f"   Baixa confiança (<0.6): {quality['confidence_distribution']['low_confidence']}")
        
        print(f"\n📈 PERFORMANCE POR SÍMBOLO:")
        for symbol, perf in summary['symbol_performance'].items():
            print(f"   {symbol}:")
            print(f"      Taxa de sucesso: {perf['success_rate']:.1%}")
            print(f"      Taxa de sinais: {perf['signal_rate']:.1%}")
            print(f"      Tempo médio: {perf['avg_response_time']:.3f}s")
            print(f"      Confiança média: {perf['avg_confidence']:.3f}")
        
        # Avaliar resultado geral
        print(f"\n🏆 AVALIAÇÃO FINAL:")
        
        score_components = {
            'success_rate': summary['success_rate'] * 30,
            'signal_rate': summary['signal_rate'] * 20,
            'speed_score': max(0, (1 - perf['avg_response_time']) * 25),
            'confidence_score': quality['avg_confidence'] * 25
        }
        
        total_score = sum(score_components.values())
        
        print(f"   Taxa de Sucesso: {score_components['success_rate']:.1f}/30")
        print(f"   Taxa de Sinais: {score_components['signal_rate']:.1f}/20")
        print(f"   Velocidade: {score_components['speed_score']:.1f}/25")
        print(f"   Confiança: {score_components['confidence_score']:.1f}/25")
        print(f"   SCORE TOTAL: {total_score:.1f}/100")
        
        if total_score >= 80:
            print(f"   🏆 EXCELENTE - Engine pronta para produção!")
        elif total_score >= 60:
            print(f"   ✅ BOM - Engine adequada com pequenos ajustes")
        elif total_score >= 40:
            print(f"   ⚠️  REGULAR - Engine precisa de otimizações")
        else:
            print(f"   ❌ INSUFICIENTE - Engine precisa de revisão")

    def salvar_resultados(self):
        """Salvar resultados em arquivo JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_final_app_ultra_enhanced_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        return filename

def main():
    """Função principal"""
    print("🚀 TESTE FINAL - UltraEnhancedAIEngine com Ativos do App")
    print("=" * 60)
    
    teste = TesteFinalApp()
    
    try:
        # Executar teste completo
        results = teste.executar_teste_completo()
        
        # Imprimir relatório
        teste.imprimir_relatorio()
        
        # Salvar resultados
        filename = teste.salvar_resultados()
        
        print(f"\n✅ Teste finalizado com sucesso!")
        print(f"📁 Arquivo de resultados: {filename}")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
