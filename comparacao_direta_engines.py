#!/usr/bin/env python3
"""
🔥 COMPARAÇÃO DIRETA: Engine Atual vs V3 Otimizada
Teste específico para determinar a melhor engine para o app mobile
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
    ULTRA_AVAILABLE = True
    logger.info("✅ UltraEnhancedAIEngine importada")
except ImportError as e:
    logger.error(f"❌ Erro ao importar UltraEnhanced: {e}")
    ULTRA_AVAILABLE = False

try:
    from ai_engine_v3_otimizado import OptimizedAIEngineV3
    V3_AVAILABLE = True
    logger.info("✅ OptimizedAIEngineV3 importada")
except ImportError as e:
    logger.error(f"❌ Erro ao importar V3: {e}")
    V3_AVAILABLE = False

class DirectEngineComparison:
    """Comparação direta entre engine atual e V3 otimizada"""
    
    def __init__(self):
        self.config = self._create_config()
        self.results = {}
        
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
    
    def generate_test_data(self, symbol: str, periods: int = 200) -> pd.DataFrame:
        """Gerar dados de teste realistas"""
        
        logger.info(f"📊 Gerando dados de teste para {symbol}...")
        
        # Preço base
        base_price = 50000 if 'BTC' in symbol else 3000
        
        # Criar cenário misto (mais realista)
        prices = []
        current_price = base_price
        
        for i in range(periods):
            # Movimento mais realista com tendências e reversões
            if i < periods // 3:
                trend = 0.001  # Tendência de alta inicial
            elif i < 2 * periods // 3:
                trend = -0.0005  # Correção
            else:
                trend = 0.0008  # Recuperação
            
            # Adicionar volatilidade
            noise = np.random.normal(0, 0.02)
            price_change = (trend + noise) * current_price
            current_price = max(current_price + price_change, base_price * 0.7)
            
            # OHLC realista
            high = current_price * np.random.uniform(1.001, 1.015)
            low = current_price * np.random.uniform(0.985, 0.999)
            open_price = current_price * np.random.uniform(0.995, 1.005)
            
            # Volume correlacionado
            base_volume = 1000000
            volume = base_volume * np.random.uniform(0.5, 3.0)
            
            prices.append({
                'timestamp': pd.Timestamp.now() - pd.Timedelta(minutes=(periods-i)),
                'open': open_price,
                'high': high,
                'low': low,
                'close': current_price,
                'volume': volume
            })
        
        df = pd.DataFrame(prices)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"✅ {len(df)} períodos gerados para {symbol}")
        return df
    
    def test_engine_performance(self, engine_name: str, engine, df: pd.DataFrame, symbol: str) -> Dict:
        """Testar performance da engine com métricas específicas para mobile"""
        
        logger.info(f"🔍 Testando {engine_name} com {symbol}...")
        
        try:
            # Métricas de performance
            start_time = time.time()
            
            # Teste de velocidade - múltiplas predições
            prediction_times = []
            predictions = []
            confidences = []
            signal_counts = {'buy': 0, 'sell': 0, 'hold': 0}
            
            # Simular uso real - predições a cada 10 períodos
            test_points = range(50, len(df), 10)
            
            for i in test_points:
                window_df = df.iloc[max(0, i-50):i+1].copy()
                
                pred_start = time.time()
                
                # Escolher método correto baseado na engine
                if engine_name == "UltraEnhanced":
                    if hasattr(engine, 'ultra_predict_signal'):
                        result = engine.ultra_predict_signal(window_df, f"{symbol}_test")
                    else:
                        result = engine.predict_signal(window_df, f"{symbol}_test")
                elif engine_name == "V3Optimized":
                    if hasattr(engine, 'optimized_predict_signal'):
                        result = engine.optimized_predict_signal(window_df, f"{symbol}_test")
                    else:
                        result = engine.predict_signal(window_df, f"{symbol}_test")
                else:
                    result = engine.predict_signal(window_df, f"{symbol}_test")
                
                pred_time = time.time() - pred_start
                prediction_times.append(pred_time)
                
                if result and isinstance(result, dict):
                    signal = result.get('signal', 2)
                    confidence = result.get('confidence', 0.5)
                    signal_type = result.get('signal_type', 'hold')
                    
                    predictions.append(signal)
                    confidences.append(confidence)
                    
                    if signal_type.lower() == 'buy':
                        signal_counts['buy'] += 1
                    elif signal_type.lower() == 'sell':
                        signal_counts['sell'] += 1
                    else:
                        signal_counts['hold'] += 1
                else:
                    predictions.append(2)
                    confidences.append(0.5)
                    signal_counts['hold'] += 1
            
            total_time = time.time() - start_time
            
            # Calcular métricas
            if prediction_times:
                avg_pred_time = np.mean(prediction_times)
                max_pred_time = np.max(prediction_times)
                min_pred_time = np.min(prediction_times)
                
                # Métricas de qualidade
                avg_confidence = np.mean(confidences)
                confidence_std = np.std(confidences)
                
                # Diversidade de sinais (importante para não ficar "travado" em HOLD)
                total_signals = len(predictions)
                active_signals = signal_counts['buy'] + signal_counts['sell']
                signal_diversity = active_signals / total_signals if total_signals > 0 else 0
                
                # Score específico para mobile
                mobile_score = self._calculate_mobile_score(
                    avg_pred_time, avg_confidence, signal_diversity, 
                    signal_counts, total_signals
                )
                
                result = {
                    'engine': engine_name,
                    'symbol': symbol,
                    'total_predictions': total_signals,
                    'total_time': total_time,
                    'avg_prediction_time': avg_pred_time,
                    'max_prediction_time': max_pred_time,
                    'min_prediction_time': min_pred_time,
                    'avg_confidence': avg_confidence,
                    'confidence_std': confidence_std,
                    'signal_counts': signal_counts,
                    'signal_diversity': signal_diversity,
                    'mobile_score': mobile_score,
                    'predictions_per_second': 1 / avg_pred_time if avg_pred_time > 0 else 0,
                    'success': True
                }
                
                logger.info(f"   ✅ {total_signals} predições em {total_time:.2f}s")
                logger.info(f"   ⚡ Tempo médio: {avg_pred_time*1000:.1f}ms")
                logger.info(f"   🎯 Confiança: {avg_confidence:.3f}")
                logger.info(f"   📊 Diversidade: {signal_diversity:.3f}")
                logger.info(f"   📱 Score Mobile: {mobile_score:.1f}")
                
                return result
            
            else:
                return {'engine': engine_name, 'symbol': symbol, 'success': False, 'error': 'No predictions made'}
                
        except Exception as e:
            logger.error(f"   ❌ Erro testando {engine_name}: {e}")
            return {'engine': engine_name, 'symbol': symbol, 'success': False, 'error': str(e)}
    
    def _calculate_mobile_score(self, avg_time: float, confidence: float, 
                               diversity: float, signal_counts: dict, total: int) -> float:
        """Calcular score específico para mobile"""
        
        # Peso dos critérios para mobile
        time_score = max(0, 100 - (avg_time * 1000))  # Penalizar se > 1s
        confidence_score = confidence * 100
        diversity_score = diversity * 100
        
        # Bonus por gerar sinais ativos (não só HOLD)
        activity_bonus = 0
        if total > 0:
            active_ratio = (signal_counts['buy'] + signal_counts['sell']) / total
            activity_bonus = active_ratio * 20  # Máximo 20 pontos
        
        # Score final ponderado para mobile
        mobile_score = (
            time_score * 0.4 +      # 40% - Velocidade é crítica
            confidence_score * 0.3 + # 30% - Confiança
            diversity_score * 0.2 +  # 20% - Diversidade
            activity_bonus * 0.1     # 10% - Atividade
        )
        
        return min(mobile_score, 100)  # Cap em 100
    
    def run_comparison(self):
        """Executar comparação direta"""
        
        logger.info("🔥 COMPARAÇÃO DIRETA: Engine Atual vs V3 Otimizada")
        logger.info("=" * 60)
        
        if not ULTRA_AVAILABLE or not V3_AVAILABLE:
            logger.error("❌ Engines não disponíveis para comparação")
            return
        
        # Inicializar engines
        try:
            ultra_engine = UltraEnhancedAIEngine(self.config)
            logger.info("✅ UltraEnhanced inicializada")
        except Exception as e:
            logger.error(f"❌ Erro inicializando UltraEnhanced: {e}")
            return
            
        try:
            v3_engine = OptimizedAIEngineV3(self.config)
            logger.info("✅ V3Optimized inicializada")
        except Exception as e:
            logger.error(f"❌ Erro inicializando V3Optimized: {e}")
            return
        
        # Símbolos para teste
        test_symbols = ['BTCUSDT', 'ETHUSDT']
        engines = {
            'UltraEnhanced': ultra_engine,
            'V3Optimized': v3_engine
        }
        
        all_results = []
        
        # Testar cada combinação
        for symbol in test_symbols:
            logger.info(f"\n📊 Testando com {symbol}...")
            
            # Gerar dados únicos para cada símbolo
            df = self.generate_test_data(symbol, 200)
            
            symbol_results = {}
            
            for engine_name, engine in engines.items():
                result = self.test_engine_performance(engine_name, engine, df, symbol)
                if result.get('success', False):
                    symbol_results[engine_name] = result
                    all_results.append(result)
            
            # Comparação direta para este símbolo
            if len(symbol_results) == 2:
                self._compare_symbol_results(symbol, symbol_results)
        
        # Análise final
        self._final_analysis(all_results)
        
        # Salvar resultados
        self._save_results(all_results)
        
        return all_results
    
    def _compare_symbol_results(self, symbol: str, results: Dict):
        """Comparar resultados para um símbolo específico"""
        
        logger.info(f"\n🔍 COMPARAÇÃO DIRETA - {symbol}:")
        logger.info("-" * 40)
        
        ultra = results.get('UltraEnhanced', {})
        v3 = results.get('V3Optimized', {})
        
        # Velocidade
        ultra_time = ultra.get('avg_prediction_time', float('inf')) * 1000
        v3_time = v3.get('avg_prediction_time', float('inf')) * 1000
        
        logger.info(f"⚡ Velocidade:")
        logger.info(f"   UltraEnhanced: {ultra_time:.1f}ms")
        logger.info(f"   V3Optimized:   {v3_time:.1f}ms")
        if ultra_time < v3_time:
            speed_diff = ((v3_time - ultra_time) / ultra_time) * 100
            logger.info(f"   🏆 UltraEnhanced é {speed_diff:.1f}% mais rápida")
        else:
            speed_diff = ((ultra_time - v3_time) / v3_time) * 100
            logger.info(f"   🏆 V3Optimized é {speed_diff:.1f}% mais rápida")
        
        # Confiança
        ultra_conf = ultra.get('avg_confidence', 0)
        v3_conf = v3.get('avg_confidence', 0)
        
        logger.info(f"🎯 Confiança:")
        logger.info(f"   UltraEnhanced: {ultra_conf:.3f}")
        logger.info(f"   V3Optimized:   {v3_conf:.3f}")
        
        # Score Mobile
        ultra_mobile = ultra.get('mobile_score', 0)
        v3_mobile = v3.get('mobile_score', 0)
        
        logger.info(f"📱 Score Mobile:")
        logger.info(f"   UltraEnhanced: {ultra_mobile:.1f}/100")
        logger.info(f"   V3Optimized:   {v3_mobile:.1f}/100")
        
        # Diversidade
        ultra_div = ultra.get('signal_diversity', 0)
        v3_div = v3.get('signal_diversity', 0)
        
        logger.info(f"🎲 Diversidade:")
        logger.info(f"   UltraEnhanced: {ultra_div:.3f}")
        logger.info(f"   V3Optimized:   {v3_div:.3f}")
    
    def _final_analysis(self, results: List[Dict]):
        """Análise final e recomendação"""
        
        logger.info("\n" + "=" * 60)
        logger.info("🏆 ANÁLISE FINAL - MELHOR ENGINE PARA APP")
        logger.info("=" * 60)
        
        # Agrupar por engine
        ultra_results = [r for r in results if r.get('engine') == 'UltraEnhanced']
        v3_results = [r for r in results if r.get('engine') == 'V3Optimized']
        
        if not ultra_results or not v3_results:
            logger.error("❌ Dados insuficientes para comparação")
            return
        
        # Médias gerais
        ultra_stats = self._calculate_stats(ultra_results)
        v3_stats = self._calculate_stats(v3_results)
        
        logger.info("📊 ESTATÍSTICAS GERAIS:")
        logger.info("\n🚀 UltraEnhanced:")
        logger.info(f"   ⚡ Velocidade média: {ultra_stats['avg_time']*1000:.1f}ms")
        logger.info(f"   🎯 Confiança média: {ultra_stats['avg_confidence']:.3f}")
        logger.info(f"   📱 Score Mobile: {ultra_stats['mobile_score']:.1f}/100")
        logger.info(f"   🎲 Diversidade: {ultra_stats['diversity']:.3f}")
        logger.info(f"   📈 Predições/seg: {ultra_stats['pred_per_sec']:.1f}")
        
        logger.info("\n🔬 V3Optimized:")
        logger.info(f"   ⚡ Velocidade média: {v3_stats['avg_time']*1000:.1f}ms")
        logger.info(f"   🎯 Confiança média: {v3_stats['avg_confidence']:.3f}")
        logger.info(f"   📱 Score Mobile: {v3_stats['mobile_score']:.1f}/100")
        logger.info(f"   🎲 Diversidade: {v3_stats['diversity']:.3f}")
        logger.info(f"   📈 Predições/seg: {v3_stats['pred_per_sec']:.1f}")
        
        # Determinar vencedora
        winner = self._determine_winner(ultra_stats, v3_stats)
        
        logger.info("\n" + "🏆" * 20)
        logger.info(f"🥇 RECOMENDAÇÃO FINAL PARA APP: {winner['name']}")
        logger.info("🏆" * 20)
        
        logger.info(f"\n✅ RAZÕES DA ESCOLHA:")
        for reason in winner['reasons']:
            logger.info(f"   • {reason}")
        
        logger.info(f"\n📱 ADEQUAÇÃO MOBILE: {winner['mobile_rating']}")
        
        # Recomendações específicas
        logger.info(f"\n🛠️ RECOMENDAÇÕES:")
        for rec in winner['recommendations']:
            logger.info(f"   📋 {rec}")
    
    def _calculate_stats(self, results: List[Dict]) -> Dict:
        """Calcular estatísticas agregadas"""
        
        if not results:
            return {}
        
        return {
            'avg_time': np.mean([r.get('avg_prediction_time', 0) for r in results]),
            'avg_confidence': np.mean([r.get('avg_confidence', 0) for r in results]),
            'mobile_score': np.mean([r.get('mobile_score', 0) for r in results]),
            'diversity': np.mean([r.get('signal_diversity', 0) for r in results]),
            'pred_per_sec': np.mean([r.get('predictions_per_second', 0) for r in results])
        }
    
    def _determine_winner(self, ultra_stats: Dict, v3_stats: Dict) -> Dict:
        """Determinar engine vencedora baseada em critérios mobile"""
        
        ultra_score = 0
        v3_score = 0
        
        reasons = []
        
        # Critério 1: Velocidade (peso 40%)
        if ultra_stats['avg_time'] < v3_stats['avg_time']:
            ultra_score += 40
            speed_diff = ((v3_stats['avg_time'] - ultra_stats['avg_time']) / ultra_stats['avg_time']) * 100
            reasons.append(f"⚡ UltraEnhanced é {speed_diff:.1f}% mais rápida")
        else:
            v3_score += 40
            speed_diff = ((ultra_stats['avg_time'] - v3_stats['avg_time']) / v3_stats['avg_time']) * 100
            reasons.append(f"⚡ V3Optimized é {speed_diff:.1f}% mais rápida")
        
        # Critério 2: Score Mobile (peso 30%)
        if ultra_stats['mobile_score'] > v3_stats['mobile_score']:
            ultra_score += 30
            reasons.append(f"📱 Melhor score mobile ({ultra_stats['mobile_score']:.1f} vs {v3_stats['mobile_score']:.1f})")
        else:
            v3_score += 30
            reasons.append(f"📱 Melhor score mobile ({v3_stats['mobile_score']:.1f} vs {ultra_stats['mobile_score']:.1f})")
        
        # Critério 3: Confiança (peso 20%)
        if ultra_stats['avg_confidence'] > v3_stats['avg_confidence']:
            ultra_score += 20
            reasons.append(f"🎯 Maior confiança ({ultra_stats['avg_confidence']:.3f})")
        else:
            v3_score += 20
            reasons.append(f"🎯 Maior confiança ({v3_stats['avg_confidence']:.3f})")
        
        # Critério 4: Diversidade (peso 10%)
        if ultra_stats['diversity'] > v3_stats['diversity']:
            ultra_score += 10
            reasons.append(f"🎲 Melhor diversidade de sinais")
        else:
            v3_score += 10
            reasons.append(f"🎲 Melhor diversidade de sinais")
        
        # Determinar vencedora
        if ultra_score > v3_score:
            winner_name = "UltraEnhanced"
            mobile_rating = "EXCELENTE" if ultra_stats['mobile_score'] > 80 else "BOA" if ultra_stats['mobile_score'] > 60 else "REGULAR"
            recommendations = [
                "Usar como engine principal no app",
                "Implementar cache para otimizar ainda mais",
                "Configurar thresholds específicos por ativo"
            ]
        else:
            winner_name = "V3Optimized"
            mobile_rating = "EXCELENTE" if v3_stats['mobile_score'] > 80 else "BOA" if v3_stats['mobile_score'] > 60 else "REGULAR"
            recommendations = [
                "Usar como engine principal, mas otimizar velocidade",
                "Implementar modo 'lite' para mobile",
                "Considerar cache agressivo para compensar lentidão"
            ]
        
        return {
            'name': winner_name,
            'score': max(ultra_score, v3_score),
            'reasons': reasons,
            'mobile_rating': mobile_rating,
            'recommendations': recommendations
        }
    
    def _save_results(self, results: List[Dict]):
        """Salvar resultados da comparação"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparacao_direta_engines_{timestamp}.json"
        
        output = {
            'timestamp': timestamp,
            'comparison_type': 'direct_ultra_vs_v3',
            'results': results,
            'summary': 'Comparação direta entre UltraEnhanced e V3Optimized para app mobile'
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            logger.info(f"\n💾 Resultados salvos em: {filename}")
        except Exception as e:
            logger.error(f"❌ Erro salvando resultados: {e}")

def main():
    """Função principal"""
    
    comparator = DirectEngineComparison()
    results = comparator.run_comparison()
    
    if results:
        logger.info("\n✅ Comparação concluída com sucesso!")
    else:
        logger.error("\n❌ Falha na comparação!")

if __name__ == "__main__":
    main()
