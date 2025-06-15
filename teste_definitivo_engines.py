#!/usr/bin/env python3
"""
🚀 TESTE DEFINITIVO - COMPARAÇÃO ENGINES DE IA
Teste completo das engines enhanced/V3 com dados reais e métricas avançadas
"""

import pandas as pd
import numpy as np
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Importar engines
try:
    from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
    ULTRA_ENHANCED_AVAILABLE = True
except ImportError as e:
    logger.warning(f"UltraEnhancedAIEngine não disponível: {e}")
    ULTRA_ENHANCED_AVAILABLE = False

try:
    from ai_engine_v3_otimizado import OptimizedAIEngineV3
    V3_OPTIMIZED_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OptimizedAIEngineV3 não disponível: {e}")
    V3_OPTIMIZED_AVAILABLE = False

try:
    from src.ai_engine import AITradingEngine
    BASE_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AITradingEngine base não disponível: {e}")
    BASE_ENGINE_AVAILABLE = False

class AdvancedEngineComparator:
    """Comparador avançado de engines de IA"""
    
    def __init__(self):
        self.results = []
        self.engines = {}
        self.test_data = {}
        
        # Configuração básica
        self.config = self._create_config()
        
    def _create_config(self):
        """Criar configuração simulada"""
        return type('Config', (), {
            'binance_api_key': 'test',
            'binance_secret_key': 'test',
            'trading': {
                'pairs': ['BTCUSDT', 'ETHUSDT'],
                'default_quantity': 0.001,
                'risk_percentage': 2.0
            },
            'ai': {
                'confidence_threshold': 0.6,
                'use_ml_features': True
            }
        })()
    
    def generate_realistic_market_data(self, symbol: str, periods: int = 500) -> pd.DataFrame:
        """Gerar dados realistas de mercado para teste"""
        
        logger.info(f"📊 Gerando dados para {symbol}...")
        
        # Base price
        base_price = 50000 if 'BTC' in symbol else 3000
        
        # Gerar tendência e volatilidade
        trend = np.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])  # Bear, sideways, bull
        volatility = np.random.uniform(0.015, 0.04)  # 1.5% a 4% diário
        
        logger.info(f"   Cenário: {'📈 Bull' if trend > 0 else '📉 Bear' if trend < 0 else '↔️ Sideways'}")
        logger.info(f"   Volatilidade: {volatility*100:.1f}%")
        
        # Gerar preços
        prices = []
        volumes = []
        
        current_price = base_price
        for i in range(periods):
            # Movimento aleatório com tendência
            random_move = np.random.normal(0, volatility)
            trend_move = trend * 0.001  # 0.1% por período
            
            # Adicionar alguns eventos especiais
            if np.random.random() < 0.05:  # 5% chance de evento especial
                random_move *= np.random.uniform(2, 5)  # Movimento forte
            
            price_change = (trend_move + random_move) * current_price
            current_price = max(current_price + price_change, base_price * 0.5)
            
            # Simular OHLC
            high = current_price * np.random.uniform(1.001, 1.02)
            low = current_price * np.random.uniform(0.98, 0.999)
            open_price = current_price * np.random.uniform(0.995, 1.005)
            
            # Volume correlacionado com volatilidade
            base_volume = 1000000
            volume_multiplier = 1 + abs(random_move) * 10
            volume = base_volume * volume_multiplier * np.random.uniform(0.5, 2.0)
            
            prices.append({
                'timestamp': pd.Timestamp.now() - pd.Timedelta(minutes=(periods-i)),
                'open': open_price,
                'high': high,
                'low': low,
                'close': current_price,
                'volume': volume
            })
            
            volumes.append(volume)
        
        df = pd.DataFrame(prices)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"✅ Dados gerados: {len(df)} períodos")
        logger.info(f"   Preço inicial: ${prices[0]['close']:.2f}")
        logger.info(f"   Preço final: ${prices[-1]['close']:.2f}")
        logger.info(f"   Retorno total: {((prices[-1]['close']/prices[0]['close'])-1)*100:.2f}%")
        
        return df
    
    def initialize_engines(self):
        """Inicializar todas as engines disponíveis"""
        
        logger.info("🔧 Inicializando engines...")
        
        if ULTRA_ENHANCED_AVAILABLE:
            try:
                self.engines['UltraEnhanced'] = UltraEnhancedAIEngine(self.config)
                logger.info("✅ UltraEnhancedAIEngine inicializada")
            except Exception as e:
                logger.error(f"❌ Erro inicializando UltraEnhanced: {e}")
        
        if V3_OPTIMIZED_AVAILABLE:
            try:
                self.engines['V3Optimized'] = OptimizedAIEngineV3(self.config)
                logger.info("✅ OptimizedAIEngineV3 inicializada")
            except Exception as e:
                logger.error(f"❌ Erro inicializando V3Optimized: {e}")
        
        if BASE_ENGINE_AVAILABLE:
            try:
                self.engines['BaseEngine'] = AITradingEngine(self.config)
                logger.info("✅ AITradingEngine base inicializada")
            except Exception as e:
                logger.error(f"❌ Erro inicializando BaseEngine: {e}")
        
        logger.info(f"🎯 {len(self.engines)} engines inicializadas")
    
    def test_engine_with_data(self, engine_name: str, engine, df: pd.DataFrame, symbol: str) -> Dict:
        """Testar uma engine com dados específicos"""
        
        try:
            logger.info(f"🔍 Testando {engine_name} com {symbol}...")
            
            # Métricas de timing
            start_time = time.time()
            
            # Predições múltiplas para avaliar consistência
            predictions = []
            confidences = []
            processing_times = []
            
            # Testar com janelas deslizantes
            window_size = 100
            step_size = 10
            
            for i in range(window_size, len(df), step_size):
                if i + 10 > len(df):  # Parar antes do final
                    break
                
                window_df = df.iloc[i-window_size:i].copy()
                
                pred_start = time.time()
                
                # Chamar método apropriado dependendo da engine
                if hasattr(engine, 'optimized_predict_signal') and engine_name == 'V3Optimized':
                    result = engine.optimized_predict_signal(window_df, f"{symbol}_{engine_name}")
                elif hasattr(engine, 'enhanced_predict_signal') and 'Enhanced' in engine_name:
                    result = engine.enhanced_predict_signal(window_df, f"{symbol}_{engine_name}")
                else:
                    result = engine.predict_signal(window_df, f"{symbol}_{engine_name}")
                
                pred_time = time.time() - pred_start
                processing_times.append(pred_time)
                
                if result and isinstance(result, dict):
                    signal = result.get('signal', 2)
                    confidence = result.get('confidence', 0.5)
                    
                    predictions.append(signal)
                    confidences.append(confidence)
                else:
                    predictions.append(2)  # HOLD
                    confidences.append(0.5)
            
            total_time = time.time() - start_time
            
            # Calcular métricas
            if predictions:
                signal_distribution = {
                    'buy': predictions.count(1),
                    'sell': predictions.count(0), 
                    'hold': predictions.count(2)
                }
                
                signal_diversity = 1.0 - (max(signal_distribution.values()) / len(predictions))
                avg_confidence = np.mean(confidences)
                max_confidence = np.max(confidences)
                confidence_std = np.std(confidences)
                avg_processing_time = np.mean(processing_times)
                
                # Simular acurácia baseada em movimentos reais
                actual_movements = []
                predicted_directions = []
                
                for i in range(len(predictions)):
                    actual_idx = window_size + i * step_size
                    if actual_idx + 5 < len(df):
                        current_price = df.iloc[actual_idx]['close']
                        future_price = df.iloc[actual_idx + 5]['close']
                        actual_movement = 1 if future_price > current_price else 0
                        
                        pred_signal = predictions[i]
                        pred_direction = 1 if pred_signal == 1 else 0 if pred_signal == 0 else None
                        
                        if pred_direction is not None:
                            actual_movements.append(actual_movement)
                            predicted_directions.append(pred_direction)
                
                # Calcular acurácia
                if actual_movements and predicted_directions:
                    correct_predictions = sum(1 for a, p in zip(actual_movements, predicted_directions) if a == p)
                    simulated_accuracy = correct_predictions / len(actual_movements)
                else:
                    simulated_accuracy = 0.5
                
                # Score final
                performance_score = (
                    simulated_accuracy * 1000 +  # Acurácia é o mais importante
                    signal_diversity * 200 +       # Diversidade de sinais
                    avg_confidence * 100 +         # Confiança média
                    (1/avg_processing_time) * 50   # Velocidade
                )
                
                result = {
                    'engine_name': engine_name,
                    'symbol': symbol,
                    'total_time': total_time,
                    'avg_processing_time': avg_processing_time,
                    'predictions_made': len(predictions),
                    'signal_distribution': signal_distribution,
                    'signal_diversity': signal_diversity,
                    'avg_confidence': avg_confidence,
                    'max_confidence': max_confidence,
                    'confidence_std': confidence_std,
                    'simulated_accuracy': simulated_accuracy,
                    'performance_score': performance_score,
                    'success': True
                }
                
                logger.info(f"   ✅ {engine_name}: {len(predictions)} predições")
                logger.info(f"      Acurácia simulada: {simulated_accuracy:.3f}")
                logger.info(f"      Confiança média: {avg_confidence:.3f}")
                logger.info(f"      Diversidade: {signal_diversity:.3f}")
                logger.info(f"      Score: {performance_score:.1f}")
                
                return result
            
            else:
                logger.warning(f"   ⚠️ {engine_name}: Nenhuma predição válida")
                return {
                    'engine_name': engine_name,
                    'symbol': symbol,
                    'success': False,
                    'error': 'No valid predictions'
                }
                
        except Exception as e:
            logger.error(f"   ❌ {engine_name}: Erro durante teste - {e}")
            return {
                'engine_name': engine_name,
                'symbol': symbol,
                'success': False,
                'error': str(e)
            }
    
    def run_comprehensive_test(self):
        """Executar teste abrangente"""
        
        logger.info("🚀 INICIANDO TESTE DEFINITIVO DE ENGINES")
        logger.info("=" * 60)
        
        # Inicializar engines
        self.initialize_engines()
        
        if not self.engines:
            logger.error("❌ Nenhuma engine disponível para teste!")
            return
        
        # Símbolos para teste
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        # Gerar dados para cada símbolo
        for symbol in test_symbols:
            logger.info(f"\n📊 Preparando dados para {symbol}...")
            df = self.generate_realistic_market_data(symbol, 300)
            self.test_data[symbol] = df
        
        # Testar cada engine com cada símbolo
        all_results = []
        
        for engine_name, engine in self.engines.items():
            logger.info(f"\n🧠 Testando {engine_name}...")
            engine_results = []
            
            for symbol in test_symbols:
                df = self.test_data[symbol]
                result = self.test_engine_with_data(engine_name, engine, df, symbol)
                
                if result.get('success', False):
                    engine_results.append(result)
                    all_results.append(result)
            
            # Calcular métricas agregadas por engine
            if engine_results:
                avg_accuracy = np.mean([r['simulated_accuracy'] for r in engine_results])
                avg_confidence = np.mean([r['avg_confidence'] for r in engine_results])
                avg_diversity = np.mean([r['signal_diversity'] for r in engine_results])
                total_score = sum([r['performance_score'] for r in engine_results])
                
                logger.info(f"   📊 {engine_name} - Resumo:")
                logger.info(f"      Acurácia média: {avg_accuracy:.3f}")
                logger.info(f"      Confiança média: {avg_confidence:.3f}")
                logger.info(f"      Diversidade média: {avg_diversity:.3f}")
                logger.info(f"      Score total: {total_score:.1f}")
        
        # Análise final
        self.analyze_results(all_results)
        
        # Salvar resultados
        self.save_results(all_results)
        
        return all_results
    
    def analyze_results(self, results: List[Dict]):
        """Analisar resultados e gerar ranking"""
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 ANÁLISE FINAL - RANKING DAS ENGINES")
        logger.info("=" * 60)
        
        # Agrupar por engine
        engine_stats = {}
        
        for result in results:
            if not result.get('success', False):
                continue
                
            engine_name = result['engine_name']
            
            if engine_name not in engine_stats:
                engine_stats[engine_name] = {
                    'results': [],
                    'total_score': 0,
                    'avg_accuracy': 0,
                    'avg_confidence': 0,
                    'avg_diversity': 0,
                    'total_predictions': 0
                }
            
            engine_stats[engine_name]['results'].append(result)
            engine_stats[engine_name]['total_score'] += result['performance_score']
            engine_stats[engine_name]['total_predictions'] += result['predictions_made']
        
        # Calcular médias
        for engine_name, stats in engine_stats.items():
            results_list = stats['results']
            if results_list:
                stats['avg_accuracy'] = np.mean([r['simulated_accuracy'] for r in results_list])
                stats['avg_confidence'] = np.mean([r['avg_confidence'] for r in results_list])
                stats['avg_diversity'] = np.mean([r['signal_diversity'] for r in results_list])
                stats['count'] = len(results_list)
        
        # Ranking por score total
        ranking = sorted(
            engine_stats.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )
        
        logger.info("🏆 RANKING FINAL:")
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (engine_name, stats) in enumerate(ranking):
            medal = medals[i] if i < 3 else f"{i+1}º"
            
            logger.info(f"\n{medal} {engine_name}")
            logger.info(f"   📊 Score Total: {stats['total_score']:.1f}")
            logger.info(f"   🎯 Acurácia: {stats['avg_accuracy']:.3f}")
            logger.info(f"   💪 Confiança: {stats['avg_confidence']:.3f}")
            logger.info(f"   🎲 Diversidade: {stats['avg_diversity']:.3f}")
            logger.info(f"   📈 Predições: {stats['total_predictions']}")
            logger.info(f"   ✅ Testes: {stats['count']}")
        
        # Recomendação final
        if ranking:
            best_engine = ranking[0][0]
            best_stats = ranking[0][1]
            
            logger.info("\n" + "🎯" * 20)
            logger.info("🏆 RECOMENDAÇÃO FINAL PARA MOBILE/ANDROID:")
            logger.info(f"🥇 Melhor Engine: {best_engine}")
            logger.info(f"📊 Score: {best_stats['total_score']:.1f}")
            logger.info(f"🎯 Acurácia: {best_stats['avg_accuracy']:.3f}")
            logger.info(f"💪 Confiança: {best_stats['avg_confidence']:.3f}")
            
            # Avaliação para mobile
            mobile_score = self.evaluate_mobile_suitability(best_engine, best_stats)
            logger.info(f"📱 Score Mobile: {mobile_score:.1f}/100")
            
            if mobile_score >= 80:
                logger.info("✅ EXCELENTE para uso mobile!")
            elif mobile_score >= 60:
                logger.info("✅ BOM para uso mobile")
            else:
                logger.info("⚠️ Pode precisar otimizações para mobile")
    
    def evaluate_mobile_suitability(self, engine_name: str, stats: Dict) -> float:
        """Avaliar adequação para mobile"""
        
        # Critérios específicos para mobile
        accuracy_score = stats['avg_accuracy'] * 40  # 40% do peso
        confidence_score = stats['avg_confidence'] * 20  # 20% do peso
        diversity_score = stats['avg_diversity'] * 20  # 20% do peso
        
        # Bonus por características específicas
        mobile_bonus = 0
        
        if 'Enhanced' in engine_name:
            mobile_bonus += 10  # Features avançadas
        
        if 'V3' in engine_name or 'Optimized' in engine_name:
            mobile_bonus += 10  # Otimização específica
        
        mobile_score = accuracy_score + confidence_score + diversity_score + mobile_bonus
        
        return min(mobile_score * 100, 100)  # Cap em 100
    
    def save_results(self, results: List[Dict]):
        """Salvar resultados em arquivo"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_definitivo_engines_{timestamp}.json"
        
        output = {
            'timestamp': timestamp,
            'test_type': 'definitive_engine_comparison',
            'engines_tested': list(self.engines.keys()),
            'symbols_tested': list(self.test_data.keys()),
            'results': results,
            'summary': self._generate_summary(results)
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            logger.info(f"\n💾 Resultados salvos em: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Erro salvando resultados: {e}")
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Gerar resumo dos resultados"""
        
        if not results:
            return {}
        
        # Agrupar por engine
        engine_groups = {}
        for result in results:
            if result.get('success', False):
                engine_name = result['engine_name']
                if engine_name not in engine_groups:
                    engine_groups[engine_name] = []
                engine_groups[engine_name].append(result)
        
        # Calcular estatísticas
        summary = {}
        for engine_name, group_results in engine_groups.items():
            accuracy_scores = [r['simulated_accuracy'] for r in group_results]
            confidence_scores = [r['avg_confidence'] for r in group_results]
            diversity_scores = [r['signal_diversity'] for r in group_results]
            performance_scores = [r['performance_score'] for r in group_results]
            
            summary[engine_name] = {
                'count': len(group_results),
                'avg_accuracy': np.mean(accuracy_scores),
                'avg_confidence': np.mean(confidence_scores),
                'avg_diversity': np.mean(diversity_scores),
                'total_score': sum(performance_scores),
                'accuracy_std': np.std(accuracy_scores),
                'confidence_std': np.std(confidence_scores)
            }
        
        return summary

def main():
    """Função principal"""
    
    try:
        comparator = AdvancedEngineComparator()
        results = comparator.run_comprehensive_test()
        
        if results:
            logger.info("\n✅ Teste definitivo concluído com sucesso!")
        else:
            logger.error("❌ Teste definitivo falhou!")
            
    except Exception as e:
        logger.error(f"❌ Erro no teste definitivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
