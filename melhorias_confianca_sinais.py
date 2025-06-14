#!/usr/bin/env python3
"""
🎯 ESTRATÉGIAS PARA AUMENTAR A CONFIANÇA DOS SINAIS
Análise e implementação de melhorias para maior robustez
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import warnings

# Suprimir warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class SignalConfidenceEnhancer:
    """
    🎯 Classe para melhorar a confiança dos sinais de trading
    Implementa múltiplas estratégias de validação e filtragem
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.min_confidence_threshold = 0.67  # Aumentado para 0.67 - mais agressivo
        self.max_confidence_cap = 0.95  # Cap máximo para evitar overconfidence
        
        # Pesos para diferentes tipos de validação
        self.validation_weights = {
            'technical_consensus': 0.30,    # MAIOR peso para consenso técnico
            'market_regime': 0.20,          # Regime de mercado
            'volatility_filter': 0.15,     # Filtro de volatilidade  
            'volume_confirmation': 0.15,    # Confirmação por volume
            'timeframe_alignment': 0.15,    # Alinhamento multi-timeframe
            'risk_reward': 0.05            # MENOR peso para risco/retorno
        }
        
        # NOVO: Fatores de correção de viés por timeframe - MAIS AGRESSIVO
        self.timeframe_bias_correction = {
            '1m': {'buy_penalty': 0.6, 'sell_boost': 1.3, 'hold_boost': 1.4},    # Penalidade BUY maior
            '5m': {'buy_penalty': 0.5, 'sell_boost': 1.4, 'hold_boost': 1.5},    # Penalidade BUY extrema
            '15m': {'buy_penalty': 0.8, 'sell_boost': 1.1, 'hold_boost': 1.2},   # Leve favor HOLD
            '1h': {'buy_penalty': 1.2, 'sell_boost': 0.6, 'hold_boost': 1.3},    # Penalidade SELL maior
            '4h': {'buy_penalty': 1.0, 'sell_boost': 1.0, 'hold_boost': 1.1},    # Leve favor HOLD
            '1d': {'buy_penalty': 1.4, 'sell_boost': 0.5, 'hold_boost': 1.5}     # Penalidade SELL extrema
        }
    
    def enhance_signal_confidence(self, signal_data: Dict, df: pd.DataFrame, 
                                 symbol: str, timeframe: str) -> Dict:
        """
        🎯 Função principal para melhorar a confiança de um sinal
        
        Args:
            signal_data: Resultado do sinal original
            df: DataFrame com dados históricos
            symbol: Símbolo do ativo
            timeframe: Timeframe usado
            
        Returns:
            Dict com sinal melhorado e métricas de confiança
        """
        
        try:
            logger.info(f"🎯 Melhorando confiança para {symbol} ({timeframe})")
            
            # Extrair dados do sinal original
            original_signal = signal_data.get('signal', 0)
            original_confidence = signal_data.get('confidence', 0.5)
            signal_type = signal_data.get('signal_type', 'hold')
            
            logger.info(f"📊 Sinal original: {signal_type} (confiança: {original_confidence:.3f})")
            
            # === 1. ANÁLISE DE CONSENSO TÉCNICO ===
            technical_score = self._analyze_technical_consensus(df)
            
            # === 2. VALIDAÇÃO DE REGIME DE MERCADO ===
            market_regime_score = self._analyze_market_regime(df, original_signal)
            
            # === 3. FILTRO DE VOLATILIDADE ===
            volatility_score = self._analyze_volatility_context(df)
            
            # === 4. CONFIRMAÇÃO POR VOLUME ===
            volume_score = self._analyze_volume_confirmation(df, original_signal)
            
            # === 5. ALINHAMENTO MULTI-TIMEFRAME ===
            timeframe_score = self._analyze_timeframe_alignment(df, timeframe)
            
            # === 6. ANÁLISE RISCO/RETORNO ===
            risk_reward_score = self._analyze_risk_reward(df, original_signal)
            
            # === CÁLCULO DA CONFIANÇA FINAL ===
            enhanced_confidence = self._calculate_enhanced_confidence(
                original_confidence,
                technical_score,
                market_regime_score,
                volatility_score,
                volume_score,
                timeframe_score,
                risk_reward_score
            )
            
            # === DECISÃO FINAL DO SINAL ===
            final_signal, final_signal_type, final_confidence = self._make_final_decision(
                original_signal, signal_type, enhanced_confidence, 
                technical_score, market_regime_score, timeframe
            )
            
            # === CONSTRUIR RESULTADO MELHORADO ===
            enhanced_result = {
                **signal_data,  # Manter dados originais
                'signal': final_signal,
                'signal_type': final_signal_type,
                'confidence': final_confidence,
                'original_confidence': original_confidence,
                'confidence_enhanced': True,
                'enhancement_scores': {
                    'technical_consensus': technical_score,
                    'market_regime': market_regime_score,
                    'volatility_filter': volatility_score,
                    'volume_confirmation': volume_score,
                    'timeframe_alignment': timeframe_score,
                    'risk_reward': risk_reward_score
                },
                'enhancement_summary': self._create_enhancement_summary(
                    technical_score, market_regime_score, volatility_score,
                    volume_score, timeframe_score, risk_reward_score
                )
            }
            
            logger.info(f"✅ Confiança melhorada: {original_confidence:.3f} → {final_confidence:.3f}")
            logger.info(f"🎯 Sinal final: {final_signal_type}")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ Erro ao melhorar confiança: {e}")
            return signal_data  # Retornar sinal original em caso de erro
    
    def _analyze_technical_consensus(self, df: pd.DataFrame) -> float:
        """📊 Analisar consenso entre indicadores técnicos"""
        
        try:
            signals = []
            
            # RSI
            if 'rsi_14' in df.columns:
                rsi = df['rsi_14'].iloc[-1]
                if rsi < 30:
                    signals.append(1)  # Oversold = Buy
                elif rsi > 70:
                    signals.append(-1)  # Overbought = Sell
                else:
                    signals.append(0)  # Neutral
            
            # MACD
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                macd_diff = df['macd'].iloc[-1] - df['macd_signal'].iloc[-1]
                if macd_diff > 0:
                    signals.append(1)  # Bullish
                else:
                    signals.append(-1)  # Bearish
            
            # Moving Average Crossover
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                sma20 = df['sma_20'].iloc[-1]
                sma50 = df['sma_50'].iloc[-1]
                if sma20 > sma50:
                    signals.append(1)  # Bullish
                else:
                    signals.append(-1)  # Bearish
            
            # Bollinger Bands
            if all(col in df.columns for col in ['bb_upper', 'bb_lower', 'close']):
                close = df['close'].iloc[-1]
                bb_upper = df['bb_upper'].iloc[-1]
                bb_lower = df['bb_lower'].iloc[-1]
                
                if close <= bb_lower:
                    signals.append(1)  # Oversold
                elif close >= bb_upper:
                    signals.append(-1)  # Overbought
                else:
                    signals.append(0)  # Neutral
            
            # Stochastic
            if 'stoch_k' in df.columns:
                stoch = df['stoch_k'].iloc[-1]
                if stoch < 20:
                    signals.append(1)  # Oversold
                elif stoch > 80:
                    signals.append(-1)  # Overbought
                else:
                    signals.append(0)  # Neutral
            
            if not signals:
                return 0.5  # Neutral se não há indicadores
            
            # Calcular consenso
            bullish_signals = sum(1 for s in signals if s == 1)
            bearish_signals = sum(1 for s in signals if s == -1)
            total_signals = len(signals)
            
            consensus_ratio = abs(bullish_signals - bearish_signals) / total_signals
            return min(consensus_ratio + 0.3, 1.0)  # Score entre 0.3-1.0
            
        except Exception as e:
            logger.error(f"Erro no consenso técnico: {e}")
            return 0.5
    
    def _analyze_market_regime(self, df: pd.DataFrame, signal: int) -> float:
        """📈 Analisar regime de mercado e adequação do sinal"""
        
        try:
            # Detectar tendência de longo prazo
            if 'sma_200' in df.columns and len(df) >= 200:
                price = df['close'].iloc[-1]
                sma200 = df['sma_200'].iloc[-1]
                
                # Bull market se acima da MA200
                is_bull_market = price > sma200
                
                # Força da tendência
                trend_strength = abs(price / sma200 - 1)
                
                # Score baseado na adequação do sinal ao regime
                if is_bull_market and signal == 1:  # Buy em bull market
                    return min(0.8 + trend_strength * 2, 1.0)
                elif not is_bull_market and signal == -1:  # Sell em bear market
                    return min(0.8 + trend_strength * 2, 1.0)
                elif signal == 0:  # Hold é sempre adequado
                    return 0.7
                else:  # Sinal contra a tendência
                    return max(0.3 - trend_strength, 0.1)
            
            # Se não há dados suficientes, analisar tendência de curto prazo
            if len(df) >= 20:
                sma20 = df['close'].rolling(20).mean().iloc[-1]
                price = df['close'].iloc[-1]
                
                if price > sma20 and signal == 1:
                    return 0.7
                elif price < sma20 and signal == -1:
                    return 0.7
                else:
                    return 0.5
            
            return 0.5  # Neutral se dados insuficientes
            
        except Exception as e:
            logger.error(f"Erro na análise de regime: {e}")
            return 0.5
    
    def _analyze_volatility_context(self, df: pd.DataFrame) -> float:
        """📊 Analisar contexto de volatilidade"""
        
        try:
            if 'atr' in df.columns and len(df) >= 20:
                current_atr = df['atr'].iloc[-1]
                avg_atr = df['atr'].rolling(20).mean().iloc[-1]
                
                volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1
                
                # Penalizar alta volatilidade (reduz confiança)
                if volatility_ratio > 2.0:
                    return 0.3  # Volatilidade muito alta
                elif volatility_ratio > 1.5:
                    return 0.5  # Volatilidade alta
                elif volatility_ratio < 0.5:
                    return 0.9  # Baixa volatilidade (bom para sinais)
                else:
                    return 0.7  # Volatilidade normal
            
            # Calcular volatilidade manualmente se ATR não disponível
            if len(df) >= 20:
                returns = df['close'].pct_change().dropna()
                current_vol = returns.tail(5).std()
                avg_vol = returns.tail(20).std()
                
                vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
                
                if vol_ratio > 2.0:
                    return 0.3
                elif vol_ratio > 1.5:
                    return 0.5
                else:
                    return 0.7
            
            return 0.6  # Default moderado
            
        except Exception as e:
            logger.error(f"Erro na análise de volatilidade: {e}")
            return 0.6
    
    def _analyze_volume_confirmation(self, df: pd.DataFrame, signal: int) -> float:
        """📊 Analisar confirmação por volume"""
        
        try:
            if 'volume' not in df.columns or len(df) < 20:
                return 0.6  # Score neutro se não há dados de volume
            
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(20).mean().iloc[-1]
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volume alto confirma sinais direcionais
            if signal != 0:  # Buy ou Sell
                if volume_ratio > 1.5:
                    return 0.9  # Volume alto confirma
                elif volume_ratio > 1.2:
                    return 0.8  # Volume moderadamente alto
                elif volume_ratio < 0.8:
                    return 0.4  # Volume baixo enfraquece sinal
                else:
                    return 0.6  # Volume normal
            else:  # Hold
                # Para HOLD, volume baixo é melhor
                if volume_ratio < 0.8:
                    return 0.8
                else:
                    return 0.6
            
        except Exception as e:
            logger.error(f"Erro na análise de volume: {e}")
            return 0.6
    
    def _analyze_timeframe_alignment(self, df: pd.DataFrame, timeframe: str) -> float:
        """⏰ Analisar adequação do timeframe"""
        
        try:
            # Scores baseados na adequação para diferentes tipos de análise
            timeframe_scores = {
                '1m': 0.5,   # Muito ruidoso
                '5m': 0.6,   # Ainda ruidoso
                '15m': 0.7,  # Melhor para scalping
                '1h': 0.9,   # Bom equilíbrio
                '4h': 0.8,   # Bom para swing
                '1d': 0.7    # Bom para posição, mas pode ser lento
            }
            
            base_score = timeframe_scores.get(timeframe, 0.6)
            
            # Ajustar baseado na presença de tendência
            if len(df) >= 50:
                # Calcular força da tendência
                sma20 = df['close'].rolling(20).mean()
                sma50 = df['close'].rolling(50).mean()
                
                trend_strength = 0
                if not sma20.isna().iloc[-1] and not sma50.isna().iloc[-1]:
                    trend_strength = abs(sma20.iloc[-1] / sma50.iloc[-1] - 1)
                
                # Timeframes maiores são melhores em tendências fortes
                if timeframe in ['4h', '1d'] and trend_strength > 0.05:
                    base_score += 0.1
                # Timeframes menores são melhores em mercados laterais
                elif timeframe in ['15m', '1h'] and trend_strength < 0.02:
                    base_score += 0.1
              # === NOVO: APLICAR CORREÇÃO DE VIÉS POR TIMEFRAME - MAIS AGRESSIVO ===
            bias_correction = self.timeframe_bias_correction.get(timeframe, {
                'buy_penalty': 1.0, 
                'sell_boost': 1.0, 
                'hold_boost': 1.0
            })
            
            # Aplicar correções baseadas no timeframe
            if timeframe in ['1m', '5m']:  # Timeframes com viés BUY
                base_score *= bias_correction['buy_penalty']
                # Se score for baixo, favorecer HOLD
                if base_score < 0.4:
                    base_score *= bias_correction.get('hold_boost', 1.2)
            elif timeframe in ['1h', '1d']:  # Timeframes com viés SELL  
                base_score *= bias_correction['sell_boost']
                # Se score for baixo, favorecer HOLD
                if base_score < 0.4:
                    base_score *= bias_correction.get('hold_boost', 1.2)
            else:
                # Timeframes neutros - leve favor para HOLD
                base_score *= bias_correction.get('hold_boost', 1.1)
            
            return min(base_score, 1.0)
            
        except Exception as e:
            logger.error(f"Erro na análise de timeframe: {e}")
            return 0.6
    
    def _analyze_risk_reward(self, df: pd.DataFrame, signal: int) -> float:
        """💰 Analisar relação risco/retorno"""
        
        try:
            if len(df) < 20:
                return 0.6
            
            current_price = df['close'].iloc[-1]
            
            # Calcular suporte e resistência básicos
            recent_highs = df['high'].tail(20)
            recent_lows = df['low'].tail(20)
            
            resistance = recent_highs.max()
            support = recent_lows.min()
            
            # Calcular distância até suporte/resistência
            distance_to_resistance = (resistance - current_price) / current_price
            distance_to_support = (current_price - support) / current_price
            
            if signal == 1:  # Buy signal
                # Melhor se está próximo do suporte
                if distance_to_support < 0.02:  # Muito próximo do suporte
                    return 0.9
                elif distance_to_support < 0.05:
                    return 0.8
                elif distance_to_resistance < 0.02:  # Muito próximo da resistência
                    return 0.3
                else:
                    return 0.6
                    
            elif signal == -1:  # Sell signal
                # Melhor se está próximo da resistência
                if distance_to_resistance < 0.02:  # Muito próximo da resistência
                    return 0.9
                elif distance_to_resistance < 0.05:
                    return 0.8
                elif distance_to_support < 0.02:  # Muito próximo do suporte
                    return 0.3
                else:
                    return 0.6
            
            else:  # Hold
                # Hold é melhor no meio do range
                middle_distance = min(distance_to_support, distance_to_resistance)
                if middle_distance > 0.03:
                    return 0.8
                else:
                    return 0.6
            
        except Exception as e:
            logger.error(f"Erro na análise risco/retorno: {e}")
            return 0.6
    
    def _calculate_enhanced_confidence(self, original_confidence: float,
                                     technical_score: float, market_regime_score: float,
                                     volatility_score: float, volume_score: float,
                                     timeframe_score: float, risk_reward_score: float) -> float:
        """🎯 Calcular confiança melhorada com pesos"""
        
        try:
            # Calcular score ponderado
            weighted_score = (
                self.validation_weights['technical_consensus'] * technical_score +
                self.validation_weights['market_regime'] * market_regime_score +
                self.validation_weights['volatility_filter'] * volatility_score +
                self.validation_weights['volume_confirmation'] * volume_score +
                self.validation_weights['timeframe_alignment'] * timeframe_score +
                self.validation_weights['risk_reward'] * risk_reward_score
            )
            
            # Combinar com confiança original (60% peso para validações, 40% para original)
            enhanced_confidence = 0.6 * weighted_score + 0.4 * original_confidence
            
            # Aplicar limites
            enhanced_confidence = max(enhanced_confidence, 0.1)  # Mínimo 10%
            enhanced_confidence = min(enhanced_confidence, self.max_confidence_cap)  # Máximo 95%
            
            return enhanced_confidence
            
        except Exception as e:
            logger.error(f"Erro no cálculo de confiança: {e}")
            return original_confidence
    
    def _make_final_decision(self, original_signal: int, original_signal_type: str,
                           enhanced_confidence: float, technical_score: float,
                           market_regime_score: float, timeframe: str) -> Tuple[int, str, float]:
        """🎯 Tomar decisão final baseada na confiança melhorada com correção de viés"""
        
        try:
            # === APLICAR CORREÇÃO DE VIÉS POR TIMEFRAME ===
            corrected_confidence = enhanced_confidence
            corrected_signal = original_signal
            
            if timeframe in self.timeframe_bias_correction:
                correction = self.timeframe_bias_correction[timeframe]
                
                # Aplicar penalidades/boosts baseados no viés conhecido
                if original_signal == 1:  # BUY signal
                    corrected_confidence *= correction['buy_penalty']
                elif original_signal == -1:  # SELL signal  
                    corrected_confidence *= correction['sell_boost']
                
                logger.info(f"🔧 Correção de viés {timeframe}: {enhanced_confidence:.3f} → {corrected_confidence:.3f}")
            
            # === FORÇAR HOLD SE CONFIANÇA BAIXA ===
            if corrected_confidence < self.min_confidence_threshold:
                # Análise mais rigorosa para forçar HOLD
                weak_signals = []
                if technical_score < 0.5:
                    weak_signals.append("consenso técnico fraco")
                if market_regime_score < 0.5:
                    weak_signals.append("regime inadequado")
                
                if weak_signals or corrected_confidence < 0.50:
                    logger.info(f"🔄 Convertendo para HOLD: confiança {corrected_confidence:.3f} < {self.min_confidence_threshold}")
                    if weak_signals:
                        logger.info(f"   Razões: {', '.join(weak_signals)}")
                    return 0, 'hold', min(corrected_confidence + 0.1, 0.65)
            
            # === VALIDAÇÃO ADICIONAL PARA SINAIS DIRECIONAIS ===
            if corrected_confidence >= self.min_confidence_threshold:
                # Manter sinal original se passou em todas as validações
                return corrected_signal, original_signal_type, corrected_confidence
            
            # Fallback: sinal original com confiança corrigida
            return corrected_signal, original_signal_type, corrected_confidence
            
        except Exception as e:
            logger.error(f"Erro na decisão final: {e}")
            return original_signal, original_signal_type, enhanced_confidence
    
    def _create_enhancement_summary(self, technical_score: float, market_regime_score: float,
                                  volatility_score: float, volume_score: float,
                                  timeframe_score: float, risk_reward_score: float) -> str:
        """📋 Criar resumo das melhorias aplicadas"""
        
        strengths = []
        weaknesses = []
        
        scores = {
            'Consenso Técnico': technical_score,
            'Regime de Mercado': market_regime_score,
            'Contexto de Volatilidade': volatility_score,
            'Confirmação por Volume': volume_score,
            'Adequação do Timeframe': timeframe_score,
            'Risco/Retorno': risk_reward_score
        }
        
        for metric, score in scores.items():
            if score >= 0.8:
                strengths.append(f"{metric} ({score:.2f})")
            elif score <= 0.4:
                weaknesses.append(f"{metric} ({score:.2f})")
        
        summary_parts = []
        if strengths:
            summary_parts.append(f"✅ Pontos Fortes: {', '.join(strengths)}")
        if weaknesses:
            summary_parts.append(f"⚠️ Pontos Fracos: {', '.join(weaknesses)}")
        
        return " | ".join(summary_parts) if summary_parts else "📊 Análise equilibrada"

# =================================================================
# 🧪 TESTE DAS MELHORIAS DE CONFIANÇA
# =================================================================

def test_confidence_enhancer():
    """Testar as melhorias de confiança"""
    
    print("🎯 TESTANDO MELHORIAS DE CONFIANÇA")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_enhanced import EnhancedAIEngine
        
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = EnhancedAIEngine(config)
        enhancer = SignalConfidenceEnhancer(config)
        
        # Testar com alguns ativos
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        test_timeframes = ['1h', '4h']
        
        results = []
        
        for symbol in test_symbols:
            for timeframe in test_timeframes:
                print(f"\n🔍 Testando {symbol} - {timeframe}")
                
                # Obter dados
                df = market_data.get_historical_data(symbol, timeframe, 200)
                if df is None or len(df) < 100:
                    print(f"❌ Dados insuficientes para {symbol}")
                    continue
                
                # Gerar sinal original
                original_signal = ai_engine.enhanced_predict_signal(df, symbol)
                print(f"📊 Sinal Original: {original_signal.get('signal_type')} (confiança: {original_signal.get('confidence', 0):.3f})")
                
                # Melhorar confiança
                enhanced_signal = enhancer.enhance_signal_confidence(
                    original_signal, df, symbol, timeframe
                )
                
                print(f"🎯 Sinal Melhorado: {enhanced_signal.get('signal_type')} (confiança: {enhanced_signal.get('confidence', 0):.3f})")
                print(f"📈 Melhoria: {enhanced_signal.get('confidence', 0) - original_signal.get('confidence', 0):+.3f}")
                
                # Salvar resultados
                results.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'original_signal': original_signal.get('signal_type'),
                    'original_confidence': original_signal.get('confidence', 0),
                    'enhanced_signal': enhanced_signal.get('signal_type'),
                    'enhanced_confidence': enhanced_signal.get('confidence', 0),
                    'improvement': enhanced_signal.get('confidence', 0) - original_signal.get('confidence', 0),
                    'enhancement_summary': enhanced_signal.get('enhancement_summary', '')
                })
        
        # Resumo dos resultados
        print(f"\n{'='*60}")
        print("📊 RESUMO DOS RESULTADOS:")
        print(f"{'='*60}")
        
        total_tests = len(results)
        improved_count = sum(1 for r in results if r['improvement'] > 0)
        avg_improvement = np.mean([r['improvement'] for r in results])
        high_confidence_count = sum(1 for r in results if r['enhanced_confidence'] >= 0.7)
        
        print(f"🧪 Total de testes: {total_tests}")
        print(f"📈 Melhorias: {improved_count}/{total_tests} ({improved_count/total_tests*100:.1f}%)")
        print(f"📊 Melhoria média: {avg_improvement:+.3f}")
        print(f"🎯 Alta confiança (≥70%): {high_confidence_count}/{total_tests} ({high_confidence_count/total_tests*100:.1f}%)")
        
        # Salvar resultados detalhados
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_melhorias_confianca_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Resultados salvos em: {filename}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_confidence_enhancer()
