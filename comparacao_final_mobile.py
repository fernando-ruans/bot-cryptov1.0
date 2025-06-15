#!/usr/bin/env python3
"""
Comparação Final: UltraEnhanced vs V3 Otimizada para Mobile
Teste definitivo para determinar a melhor engine para o app mobile
"""

import os
import sys
import json
import time
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar as engines
try:
    from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
    from ai_engine_v3_otimizado import TradingAI_V3_Otimizado
    from src.config import Config
    from src.market_data import MarketDataManager
    print("✅ Todas as engines importadas com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar engines: {e}")
    sys.exit(1)

class MobileEngineComparator:
    """Comparador de engines com foco em critérios mobile"""
    
    def __init__(self):
        self.config = Config()
        self.market_data = MarketDataManager(self.config)
        self.results = {}
        
    def test_engine_performance(self, engine, engine_name: str, symbols: List[str], 
                              iterations: int = 20) -> Dict[str, Any]:
        """Testa performance de uma engine específica"""
        
        logger.info(f"🧪 Testando {engine_name}...")
        
        results = {
            'engine_name': engine_name,
            'symbols_tested': symbols,
            'iterations_per_symbol': iterations,
            'total_predictions': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'total_time': 0,
            'avg_time_per_prediction': 0,
            'max_time': 0,
            'min_time': float('inf'),
            'confidence_scores': [],
            'signal_distribution': {'buy': 0, 'sell': 0, 'hold': 0},
            'memory_efficiency': 'N/A',
            'mobile_compatibility_score': 0,
            'error_rate': 0,
            'signal_consistency': 0,
            'detailed_times': []
        }
        
        all_times = []
        all_confidences = []
        all_signals = []
        
        for symbol in symbols:
            logger.info(f"  📊 Testando {symbol}...")
            
            # Obter dados do mercado
            try:
                data = self.market_data.get_historical_data(symbol, '1h', limit=100)
                if data is None or len(data) < 50:
                    logger.warning(f"  ⚠️ Dados insuficientes para {symbol}")
                    continue
                    
            except Exception as e:
                logger.error(f"  ❌ Erro ao obter dados para {symbol}: {e}")
                continue
            
            symbol_times = []
            symbol_confidences = []
            symbol_signals = []
            
            for i in range(iterations):
                try:
                    start_time = time.time()
                    
                    # Fazer predição
                    prediction = engine.predict(data)
                    
                    end_time = time.time()
                    prediction_time = end_time - start_time
                    
                    # Registrar resultados
                    symbol_times.append(prediction_time)
                    all_times.append(prediction_time)
                    
                    if prediction and 'signal' in prediction:
                        results['successful_predictions'] += 1
                        
                        # Registrar confiança
                        confidence = prediction.get('confidence', 0.5)
                        symbol_confidences.append(confidence)
                        all_confidences.append(confidence)
                        
                        # Registrar sinal
                        signal = prediction['signal']
                        symbol_signals.append(signal)
                        all_signals.append(signal)
                        
                        if signal in results['signal_distribution']:
                            results['signal_distribution'][signal] += 1
                        else:
                            results['signal_distribution']['hold'] += 1
                            
                    else:
                        results['failed_predictions'] += 1
                        
                    results['total_predictions'] += 1
                    
                except Exception as e:
                    logger.error(f"    ❌ Erro na predição {i+1}: {e}")
                    results['failed_predictions'] += 1
                    results['total_predictions'] += 1
            
            # Calcular estatísticas por símbolo
            if symbol_times:
                logger.info(f"    ⏱️ {symbol}: {len(symbol_times)} predições, "
                          f"tempo médio: {np.mean(symbol_times):.4f}s")
        
        # Calcular estatísticas finais
        if all_times:
            results['total_time'] = sum(all_times)
            results['avg_time_per_prediction'] = np.mean(all_times)
            results['max_time'] = max(all_times)
            results['min_time'] = min(all_times)
            results['detailed_times'] = all_times
            
        if all_confidences:
            results['confidence_scores'] = all_confidences
            results['avg_confidence'] = np.mean(all_confidences)
            results['confidence_std'] = np.std(all_confidences)
            
        # Calcular taxa de erro
        if results['total_predictions'] > 0:
            results['error_rate'] = results['failed_predictions'] / results['total_predictions']
            
        # Calcular consistência de sinais
        if all_signals:
            unique_signals = len(set(all_signals))
            total_signals = len(all_signals)
            results['signal_consistency'] = unique_signals / max(total_signals, 1)
            
        # Calcular score de compatibilidade mobile
        results['mobile_compatibility_score'] = self.calculate_mobile_score(results)
        
        return results
    
    def calculate_mobile_score(self, results: Dict[str, Any]) -> float:
        """Calcula score de compatibilidade mobile (0-100)"""
        
        score = 0
        
        # Velocidade (40% do score)
        if results['avg_time_per_prediction'] > 0:
            # Ideal: < 0.05s = 40 pontos, > 0.2s = 0 pontos
            speed_score = max(0, 40 * (0.2 - results['avg_time_per_prediction']) / 0.15)
            score += min(40, speed_score)
        
        # Confiabilidade (30% do score)
        if results['total_predictions'] > 0:
            success_rate = (results['successful_predictions'] / results['total_predictions'])
            reliability_score = success_rate * 30
            score += reliability_score
        
        # Confiança das predições (20% do score)
        if 'avg_confidence' in results:
            confidence_score = results['avg_confidence'] * 20
            score += confidence_score
        
        # Diversidade de sinais (10% do score)
        total_signals = sum(results['signal_distribution'].values())
        if total_signals > 0:
            non_hold_signals = total_signals - results['signal_distribution'].get('hold', 0)
            diversity_score = min(10, (non_hold_signals / total_signals) * 20)
            score += diversity_score
        
        return min(100, score)
    
    def generate_mobile_recommendation(self, results1: Dict[str, Any], 
                                     results2: Dict[str, Any]) -> Dict[str, Any]:
        """Gera recomendação baseada nos resultados"""
        
        engine1_name = results1['engine_name']
        engine2_name = results2['engine_name']
        
        # Comparar métricas principais
        comparison = {
            'speed_comparison': {
                engine1_name: results1['avg_time_per_prediction'],
                engine2_name: results2['avg_time_per_prediction'],
                'winner': engine1_name if results1['avg_time_per_prediction'] < results2['avg_time_per_prediction'] else engine2_name
            },
            'reliability_comparison': {
                engine1_name: (results1['successful_predictions'] / max(results1['total_predictions'], 1)),
                engine2_name: (results2['successful_predictions'] / max(results2['total_predictions'], 1)),
                'winner': engine1_name if (results1['successful_predictions'] / max(results1['total_predictions'], 1)) > (results2['successful_predictions'] / max(results2['total_predictions'], 1)) else engine2_name
            },
            'confidence_comparison': {
                engine1_name: results1.get('avg_confidence', 0),
                engine2_name: results2.get('avg_confidence', 0),
                'winner': engine1_name if results1.get('avg_confidence', 0) > results2.get('avg_confidence', 0) else engine2_name
            },
            'mobile_score_comparison': {
                engine1_name: results1['mobile_compatibility_score'],
                engine2_name: results2['mobile_compatibility_score'],
                'winner': engine1_name if results1['mobile_compatibility_score'] > results2['mobile_compatibility_score'] else engine2_name
            }
        }
        
        # Determinar vencedor geral
        wins1 = sum(1 for comp in comparison.values() if comp['winner'] == engine1_name)
        wins2 = sum(1 for comp in comparison.values() if comp['winner'] == engine2_name)
        
        overall_winner = engine1_name if wins1 > wins2 else engine2_name
        
        # Gerar recomendações específicas
        recommendations = []
        
        if results1['mobile_compatibility_score'] < 70 and results2['mobile_compatibility_score'] < 70:
            recommendations.append("⚠️ Ambas as engines têm score mobile baixo. Considere otimizações.")
        
        if comparison['speed_comparison'][overall_winner] > 0.1:
            recommendations.append("🚀 Recomenda-se implementar cache agressivo para melhorar velocidade.")
        
        if max(results1.get('avg_confidence', 0), results2.get('avg_confidence', 0)) < 0.8:
            recommendations.append("🎯 Considere ajustar thresholds para melhorar confiança.")
        
        diversity1 = 1 - (results1['signal_distribution'].get('hold', 0) / max(sum(results1['signal_distribution'].values()), 1))
        diversity2 = 1 - (results2['signal_distribution'].get('hold', 0) / max(sum(results2['signal_distribution'].values()), 1))
        
        if max(diversity1, diversity2) < 0.3:
            recommendations.append("📊 Sinais muito conservadores. Considere diminuir thresholds.")
        
        return {
            'overall_winner': overall_winner,
            'comparison_details': comparison,
            'wins_count': {engine1_name: wins1, engine2_name: wins2},
            'recommendations': recommendations,
            'mobile_readiness': 'Alta' if comparison['mobile_score_comparison'][overall_winner] > 80 else 
                              'Média' if comparison['mobile_score_comparison'][overall_winner] > 60 else 'Baixa'
        }
    
    def run_comparison(self) -> Dict[str, Any]:
        """Executa comparação completa"""
        
        print("\n🚀 COMPARAÇÃO FINAL: UltraEnhanced vs V3 Otimizada para Mobile")
        print("=" * 60)
        
        # Símbolos para teste
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT']
        iterations = 15
        
        # Inicializar engines
        try:
            print("\n📱 Inicializando engines...")
            
            ultra_engine = UltraEnhancedAIEngine(self.config)
            print("✅ UltraEnhanced carregada")
            
            v3_engine = TradingAI_V3_Otimizado(self.config)
            print("✅ V3 Otimizada carregada")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar engines: {e}")
            return {}
        
        # Testar UltraEnhanced
        print("\n🧠 Testando UltraEnhanced Engine...")
        ultra_results = self.test_engine_performance(
            ultra_engine, 'UltraEnhanced', test_symbols, iterations
        )
        
        # Testar V3 Otimizada
        print("\n🔧 Testando V3 Otimizada Engine...")
        v3_results = self.test_engine_performance(
            v3_engine, 'V3_Otimizada', test_symbols, iterations
        )
        
        # Gerar recomendação
        print("\n📊 Analisando resultados...")
        recommendation = self.generate_mobile_recommendation(ultra_results, v3_results)
        
        # Compilar resultados finais
        final_results = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'test_config': {
                'symbols': test_symbols,
                'iterations_per_symbol': iterations,
                'total_predictions_per_engine': len(test_symbols) * iterations
            },
            'ultra_enhanced_results': ultra_results,
            'v3_otimizada_results': v3_results,
            'recommendation': recommendation
        }
        
        return final_results
    
    def print_results_summary(self, results: Dict[str, Any]):
        """Imprime resumo dos resultados"""
        
        if not results:
            print("❌ Nenhum resultado para exibir")
            return
        
        print("\n" + "="*80)
        print("📱 RESUMO DA COMPARAÇÃO FINAL PARA MOBILE")
        print("="*80)
        
        ultra = results['ultra_enhanced_results']
        v3 = results['v3_otimizada_results']
        rec = results['recommendation']
        
        print(f"\n⚡ VELOCIDADE:")
        print(f"  UltraEnhanced: {ultra['avg_time_per_prediction']:.4f}s por predição")
        print(f"  V3 Otimizada:  {v3['avg_time_per_prediction']:.4f}s por predição")
        print(f"  🏆 Mais rápida: {rec['comparison_details']['speed_comparison']['winner']}")
        
        print(f"\n🎯 CONFIABILIDADE:")
        ultra_rel = ultra['successful_predictions'] / max(ultra['total_predictions'], 1) * 100
        v3_rel = v3['successful_predictions'] / max(v3['total_predictions'], 1) * 100
        print(f"  UltraEnhanced: {ultra_rel:.1f}% de sucesso")
        print(f"  V3 Otimizada:  {v3_rel:.1f}% de sucesso")
        print(f"  🏆 Mais confiável: {rec['comparison_details']['reliability_comparison']['winner']}")
        
        print(f"\n🔮 CONFIANÇA MÉDIA:")
        print(f"  UltraEnhanced: {ultra.get('avg_confidence', 0):.3f}")
        print(f"  V3 Otimizada:  {v3.get('avg_confidence', 0):.3f}")
        print(f"  🏆 Maior confiança: {rec['comparison_details']['confidence_comparison']['winner']}")
        
        print(f"\n📱 SCORE MOBILE:")
        print(f"  UltraEnhanced: {ultra['mobile_compatibility_score']:.1f}/100")
        print(f"  V3 Otimizada:  {v3['mobile_compatibility_score']:.1f}/100")
        print(f"  🏆 Melhor para mobile: {rec['comparison_details']['mobile_score_comparison']['winner']}")
        
        print(f"\n🏆 RESULTADO FINAL:")
        print(f"  Vencedora: {rec['overall_winner']}")
        print(f"  Vitórias: {rec['wins_count']}")
        print(f"  Prontidão Mobile: {rec['mobile_readiness']}")
        
        if rec['recommendations']:
            print(f"\n💡 RECOMENDAÇÕES:")
            for recommendation in rec['recommendations']:
                print(f"  {recommendation}")
        
        print("\n" + "="*80)

def main():
    """Função principal"""
    
    comparator = MobileEngineComparator()
    
    try:
        # Executar comparação
        results = comparator.run_comparison()
        
        if results:
            # Salvar resultados
            filename = f"comparacao_final_mobile_{results['timestamp']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Resultados salvos em: {filename}")
            
            # Exibir resumo
            comparator.print_results_summary(results)
            
            # Recomendação de implementação
            winner = results['recommendation']['overall_winner']
            readiness = results['recommendation']['mobile_readiness']
            
            print(f"\n🚀 RECOMENDAÇÃO DE IMPLEMENTAÇÃO:")
            print(f"  Engine recomendada: {winner}")
            print(f"  Prontidão para mobile: {readiness}")
            
            if winner == 'V3_Otimizada':
                print(f"  💡 Para implementar: Substituir UltraEnhanced por V3 Otimizada no main.py")
            else:
                print(f"  💡 Para implementar: Manter UltraEnhanced como engine principal")
        
        else:
            print("❌ Falha na comparação")
            
    except Exception as e:
        print(f"❌ Erro durante a comparação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
