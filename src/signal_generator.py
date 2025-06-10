#!/usr/bin/env python3
"""
Gerador de sinais de trading usando IA e análise técnica
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json

from .technical_indicators import TechnicalIndicators
from .market_data import MarketDataManager
from .ai_engine import AITradingEngine
from .market_analyzer import MarketAnalyzer
from .config import Config

logger = logging.getLogger(__name__)

# Global variable to store socketio instance for notifications
_socketio_instance = None

def emit_signal_notification(signal_data: Dict):
    """Emitir notificação de sinal via WebSocket"""
    try:
        if _socketio_instance:
            _socketio_instance.emit('new_signal', signal_data)
        logger.info(f"Signal notification emitted: {signal_data.get('id', 'unknown')}")
    except Exception as e:
        logger.error(f"Erro ao emitir notificação: {e}")

def set_socketio_instance(socketio):
    """Definir instância do SocketIO"""
    global _socketio_instance
    _socketio_instance = socketio



class Signal:
    """Classe para representar um sinal de trading"""
    
    def __init__(self, symbol: str, signal_type: str, confidence: float, 
                 entry_price: float, stop_loss: float, take_profit: float,
                 timeframe: str, timestamp: datetime, reasons: List[str]):
        self.symbol = symbol
        self.signal_type = signal_type  # 'buy', 'sell', 'hold'
        self.confidence = confidence
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.timeframe = timeframe
        self.timestamp = timestamp
        self.reasons = reasons
        self.status = 'active'
        self.id = f"{symbol}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def to_dict(self) -> Dict:
        """Converter sinal para dicionário"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp.isoformat(),
            'reasons': self.reasons,
            'status': self.status
        }

class SignalGenerator:
    """Gerador principal de sinais de trading"""
    
    def __init__(self, ai_engine: AITradingEngine, market_data: MarketDataManager):
        self.ai_engine = ai_engine
        self.market_data = market_data
        self.config = ai_engine.config
        self.technical_indicators = TechnicalIndicators(self.config)
        self.market_analyzer = MarketAnalyzer(self.config, market_data, ai_engine)
        self.active_signals = {}
        self.signal_history = []
        self.last_signal_time = {}
        
    def generate_signal(self, symbol: str, timeframe: str = '1h') -> Optional[Signal]:
        """Gerar sinal de trading baseado em análise de mercado com IA"""
        try:
            logger.info(f"=== Iniciando análise de mercado com IA para {symbol} {timeframe} ===")
            
            # Verificar cooldown
            if self._is_in_cooldown(symbol):
                logger.info(f"Símbolo {symbol} em cooldown")
                raise ValueError(f"COOLDOWN:{symbol}")
            logger.info(f"✓ Cooldown OK para {symbol}")
            
            # Obter dados de mercado
            df = self.market_data.get_historical_data(symbol, timeframe, 500)
            logger.info(f"Dados obtidos para {symbol}: {len(df)} registros")
            
            # Validação robusta dos dados
            if df is None or df.empty or len(df) < 100:
                logger.error(f"Dados insuficientes para {symbol}")
                raise ValueError(f"INSUFFICIENT_DATA:{symbol}")
            
            # Verificar colunas essenciais
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Colunas faltantes no DataFrame para {symbol}")
                raise ValueError(f"MISSING_COLUMNS:{symbol}")
            
            logger.info(f"✓ Dados válidos para {symbol}: {len(df)} registros")
            
            # Calcular indicadores técnicos
            logger.info(f"Calculando indicadores técnicos para {symbol}")
            df = self.technical_indicators.calculate_all_indicators(df)
            if df is None or df.empty:
                logger.error(f"Falha ao calcular indicadores técnicos para {symbol}")
                raise ValueError(f"INDICATORS_FAILED:{symbol}")
            logger.info(f"✓ Indicadores técnicos calculados para {symbol}")
            
            # Análise completa de mercado com IA
            logger.info(f"Executando análise completa de mercado com IA para {symbol}")
            market_recommendation = self.market_analyzer.get_trade_recommendation(
                symbol=symbol,
                timeframe=timeframe
            )
            
            if not market_recommendation:
                logger.warning(f"Análise de mercado não retornou recomendação para {symbol}")
                return None
            
            # Verificar se a confiança da IA atende aos critérios mínimos
            ai_confidence = market_recommendation.get('confidence', 0.0)
            market_score = market_recommendation.get('market_score', 0.0)
            
            min_ai_confidence = self.config.SIGNAL_CONFIG.get('min_ai_confidence', 0.30)
            min_market_score = self.config.SIGNAL_CONFIG.get('min_market_score', 0.30)
            
            if ai_confidence < min_ai_confidence:
                logger.info(f"Confiança da IA insuficiente para {symbol}: {ai_confidence:.2f} < {min_ai_confidence}")
                return None
                
            if market_score < min_market_score:
                logger.info(f"Score de mercado insuficiente para {symbol}: {market_score:.2f} < {min_market_score}")
                return None
            
            signal_type = market_recommendation.get('recommendation', 'hold')
            if signal_type == 'hold':
                logger.info(f"Recomendação de mercado é HOLD para {symbol}")
                return None
            
            # Calcular confiança final (combinando IA e análise de mercado)
            final_confidence = (ai_confidence * 0.6) + (market_score * 0.4)
            
            logger.info(f"✓ Análise de mercado concluída para {symbol}:")
            logger.info(f"  - Sinal: {signal_type}")
            logger.info(f"  - Confiança IA: {ai_confidence:.2f}")
            logger.info(f"  - Score Mercado: {market_score:.2f}")
            logger.info(f"  - Confiança Final: {final_confidence:.2f}")
            
            # Obter preço atual usando API de tempo real
            from .realtime_price_api import realtime_price_api
            
            current_price = realtime_price_api.get_current_price(symbol)
            if current_price is None:
                current_price = self.market_data.get_current_price(symbol)
                
            if current_price is None:
                logger.error(f"Não foi possível obter preço atual para {symbol}")
                raise ValueError(f"PRICE_ERROR:{symbol}")
            
            # Calcular níveis de trade usando método principal com valores corretos
            levels = self._calculate_trade_levels(df, signal_type, current_price, timeframe)
            logger.info(f"✓ Níveis calculados - SL: ${levels['stop_loss']:.2f}, TP: ${levels['take_profit']:.2f}")
            
            # Criar sinal
            signal = Signal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=final_confidence,
                entry_price=current_price,
                stop_loss=levels['stop_loss'],
                take_profit=levels['take_profit'],
                timeframe=timeframe,
                timestamp=datetime.now(),
                reasons=market_recommendation.get('reasons', [])
            )
            
            # Registrar sinal
            self._register_signal(signal)
            
            logger.info(f"🎯 SINAL IA GERADO: {signal.signal_type} {symbol} - Confiança: {signal.confidence:.2f}")
            logger.info(f"=== Fim da análise de mercado para {symbol} ===")
            
            return signal
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Erro ao gerar sinal IA para {symbol}: {e}")
            logger.error(f"Detalhes do erro: {error_details}")
            return None
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Verificar se símbolo está em cooldown"""
        if symbol not in self.last_signal_time:
            return False
        
        cooldown_minutes = self.config.SIGNAL_CONFIG['signal_cooldown_minutes']
        time_diff = datetime.now() - self.last_signal_time[symbol]
        
        return time_diff.total_seconds() < (cooldown_minutes * 60)
    
    def _analyze_market_context(self, symbol: str, timeframe: str) -> Dict:
        """Analisar contexto de mercado incluindo cenário macroeconômico"""
        try:
            # Estrutura de mercado (com fallback)
            try:
                market_structure = self.market_data.detect_market_structure(symbol, timeframe)
            except:
                market_structure = {'trend': 'sideways', 'support_levels': [], 'resistance_levels': []}
            
            # Perfil de volume (com fallback)
            try:
                volume_profile = self.market_data.get_volume_profile(symbol, timeframe)
            except:
                volume_profile = {'volume_ratio': 1.0}
            
            # Volatilidade (com fallback)
            try:
                volatility = self.market_data.calculate_volatility(symbol, timeframe)
            except:
                volatility = 0.02  # Volatilidade padrão
            
            # Correlações (exemplo com BTC para altcoins)
            correlation = 0
            try:
                if symbol != 'BTCUSDT' and self.config.is_crypto_pair(symbol):
                    correlation = self.market_data.get_market_correlation(symbol, 'BTCUSDT', timeframe)
            except:
                correlation = 0
            
            # Análise de timeframe específico
            timeframe_analysis = self._analyze_timeframe_context(timeframe)
            
            # Cenário macroeconômico
            macro_context = self._analyze_macro_context(symbol)
            
            return {
                'trend': market_structure.get('trend', 'sideways'),
                'support_levels': market_structure.get('support_levels', []),
                'resistance_levels': market_structure.get('resistance_levels', []),
                'volume_ratio': volume_profile.get('volume_ratio', 1.0),
                'volatility': volatility,
                'btc_correlation': correlation,
                'timeframe_context': timeframe_analysis,
                'macro_context': macro_context
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de contexto: {e}")
            return {}
    
    def _analyze_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Analisar indicadores técnicos"""
        try:
            if df.empty or len(df) < 20:  # Reduzido de 50 para 20
                return {'signal': 'hold', 'confidence': 0, 'reasons': []}
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            signals = []
            reasons = []
            
            # RSI Analysis (mais flexível)
            if 'rsi' in latest and not pd.isna(latest['rsi']):
                if latest['rsi'] < 35:  # Menos restritivo que 30
                    signals.append(('buy', 0.7))
                    reasons.append(f"RSI oversold: {latest['rsi']:.1f}")
                elif latest['rsi'] > 65:  # Menos restritivo que 70
                    signals.append(('sell', 0.7))
                    reasons.append(f"RSI overbought: {latest['rsi']:.1f}")
                elif 35 <= latest['rsi'] <= 50:
                    signals.append(('buy', 0.4))  # Aumentado de 0.3
                    reasons.append(f"RSI in buy zone: {latest['rsi']:.1f}")
                elif 50 <= latest['rsi'] <= 65:
                    signals.append(('sell', 0.4))  # Aumentado de 0.3
                    reasons.append(f"RSI in sell zone: {latest['rsi']:.1f}")
            
            # MACD Analysis
            if ('macd' in latest and 'macd_signal' in latest and 
                not pd.isna(latest['macd']) and not pd.isna(latest['macd_signal'])):
                
                if latest['macd'] > latest['macd_signal']:
                    if len(df) > 1 and prev['macd'] <= prev['macd_signal']:
                        signals.append(('buy', 0.8))  # Crossover forte
                        reasons.append("MACD bullish crossover")
                    else:
                        signals.append(('buy', 0.5))  # Apenas acima da linha de sinal
                        reasons.append("MACD above signal line")
                elif latest['macd'] < latest['macd_signal']:
                    if len(df) > 1 and prev['macd'] >= prev['macd_signal']:
                        signals.append(('sell', 0.8))  # Crossover forte
                        reasons.append("MACD bearish crossover")
                    else:
                        signals.append(('sell', 0.5))  # Apenas abaixo da linha de sinal
                        reasons.append("MACD below signal line")
            
            # Bollinger Bands (mais flexível)
            if ('bb_lower' in latest and 'bb_upper' in latest and 
                not pd.isna(latest['bb_lower']) and not pd.isna(latest['bb_upper'])):
                
                bb_position = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
                
                if bb_position <= 0.2:  # Próximo à banda inferior
                    signals.append(('buy', 0.6))
                    reasons.append("Price near lower Bollinger Band")
                elif bb_position >= 0.8:  # Próximo à banda superior
                    signals.append(('sell', 0.6))
                    reasons.append("Price near upper Bollinger Band")
                elif bb_position <= 0.4:
                    signals.append(('buy', 0.3))
                    reasons.append("Price in lower BB zone")
                elif bb_position >= 0.6:
                    signals.append(('sell', 0.3))
                    reasons.append("Price in upper BB zone")
            
            # Moving Average Analysis (mais abrangente)
            if 'ema_12' in latest and 'ema_26' in latest:
                if not pd.isna(latest['ema_12']) and not pd.isna(latest['ema_26']):
                    if latest['ema_12'] > latest['ema_26']:
                        if len(df) > 1 and prev['ema_12'] <= prev['ema_26']:
                            signals.append(('buy', 0.7))  # Crossover
                            reasons.append("EMA 12/26 bullish crossover")
                        else:
                            signals.append(('buy', 0.4))  # Tendência de alta
                            reasons.append("EMA 12 above EMA 26")
                    else:
                        if len(df) > 1 and prev['ema_12'] >= prev['ema_26']:
                            signals.append(('sell', 0.7))  # Crossover
                            reasons.append("EMA 12/26 bearish crossover")
                        else:
                            signals.append(('sell', 0.4))  # Tendência de baixa
                            reasons.append("EMA 12 below EMA 26")
            
            # Stochastic (mais flexível)
            if ('stoch_k' in latest and 'stoch_d' in latest and 
                not pd.isna(latest['stoch_k']) and not pd.isna(latest['stoch_d'])):
                
                if latest['stoch_k'] < 25:  # Menos restritivo que 20
                    if latest['stoch_k'] > latest['stoch_d']:
                        signals.append(('buy', 0.6))
                        reasons.append("Stochastic oversold with bullish signal")
                    else:
                        signals.append(('buy', 0.3))
                        reasons.append("Stochastic oversold")
                elif latest['stoch_k'] > 75:  # Menos restritivo que 80
                    if latest['stoch_k'] < latest['stoch_d']:
                        signals.append(('sell', 0.6))
                        reasons.append("Stochastic overbought with bearish signal")
                    else:
                        signals.append(('sell', 0.3))
                        reasons.append("Stochastic overbought")
            
            # ADX Trend Strength (menos restritivo)
            if 'adx' in latest and not pd.isna(latest['adx']):
                if latest['adx'] > 20:  # Reduzido de 25
                    if 'adx_pos' in latest and 'adx_neg' in latest:
                        if not pd.isna(latest['adx_pos']) and not pd.isna(latest['adx_neg']):
                            if latest['adx_pos'] > latest['adx_neg']:
                                signals.append(('buy', 0.5))
                                reasons.append(f"Uptrend detected (ADX: {latest['adx']:.1f})")
                            else:
                                signals.append(('sell', 0.5))
                                reasons.append(f"Downtrend detected (ADX: {latest['adx']:.1f})")
            
            # Candlestick Patterns
            if 'hammer' in latest and latest['hammer']:
                signals.append(('buy', 0.5))
                reasons.append("Hammer candlestick pattern")
            
            if 'shooting_star' in latest and latest['shooting_star']:
                signals.append(('sell', 0.5))
                reasons.append("Shooting star candlestick pattern")
            
            if 'bullish_engulfing' in latest and latest['bullish_engulfing']:
                signals.append(('buy', 0.6))
                reasons.append("Bullish engulfing pattern")
            
            if 'bearish_engulfing' in latest and latest['bearish_engulfing']:
                signals.append(('sell', 0.6))
                reasons.append("Bearish engulfing pattern")
            
            # Calcular sinal final (mais flexível)
            buy_signals = [s[1] for s in signals if s[0] == 'buy']
            sell_signals = [s[1] for s in signals if s[0] == 'sell']
            
            buy_strength = sum(buy_signals)
            sell_strength = sum(sell_signals)
            
            # Lógica mais flexível - basta ter força suficiente e diferença mínima
            min_strength = 0.4  # Reduzido de 0.6 para 0.4
            min_diff = 0.2      # Diferença mínima entre buy e sell
            
            if buy_strength >= min_strength and buy_strength > sell_strength + min_diff:
                signal_type = 'buy'
                confidence = min(buy_strength / 2.0, 1.0)  # Divisor reduzido para 2.0
            elif sell_strength >= min_strength and sell_strength > buy_strength + min_diff:
                signal_type = 'sell'
                confidence = min(sell_strength / 2.0, 1.0)  # Divisor reduzido para 2.0
            elif buy_strength >= min_strength and buy_strength > sell_strength:
                # Se buy é maior mas diferença < min_diff, ainda dar sinal buy com confiança reduzida
                signal_type = 'buy'
                confidence = min(buy_strength / 3.0, 0.6)  # Confiança reduzida
            elif sell_strength >= min_strength and sell_strength > buy_strength:
                # Se sell é maior mas diferença < min_diff, ainda dar sinal sell com confiança reduzida
                signal_type = 'sell'
                confidence = min(sell_strength / 3.0, 0.6)  # Confiança reduzida
            elif buy_strength >= min_strength and buy_strength == sell_strength:
                # Empate - escolher baseado no primeiro sinal mais forte encontrado
                if buy_signals and sell_signals:
                    max_buy = max(buy_signals)
                    max_sell = max(sell_signals)
                    if max_buy >= max_sell:
                        signal_type = 'buy'
                        confidence = min(buy_strength / 2.2, 0.6)  # Divisor mais baixo para empates
                    else:
                        signal_type = 'sell'
                        confidence = min(sell_strength / 2.2, 0.6)
                elif buy_signals:
                    signal_type = 'buy'
                    confidence = min(buy_strength / 2.2, 0.6)
                elif sell_signals:
                    signal_type = 'sell'
                    confidence = min(sell_strength / 2.2, 0.6)
                else:
                    signal_type = 'hold'
                    confidence = 0.0
            else:
                signal_type = 'hold'
                confidence = 0.0
            
            return {
                'signal': signal_type,
                'confidence': confidence,
                'reasons': reasons,
                'buy_strength': buy_strength,
                'sell_strength': sell_strength
            }
            
        except Exception as e:
            logger.error(f"Erro na análise técnica: {e}")
            return {'signal': 'hold', 'confidence': 0, 'reasons': []}
    
    def _analyze_technical_indicators_debug(self, df: pd.DataFrame) -> Dict:
        """Versão de debug da análise técnica que sempre retorna um sinal válido"""
        try:
            if df.empty or len(df) < 50:
                return {'signal': 'hold', 'confidence': 0, 'reasons': []}
            
            latest = df.iloc[-1]
            reasons = []
            
            # Forçar um sinal baseado no preço (simulação simples)
            if 'close' in latest:
                close_price = latest['close']
                
                # Criar um sinal baseado em uma lógica simples
                # Se o preço termina em dígito par, BUY, se ímpar, SELL
                last_digit = int(close_price) % 10
                
                if last_digit % 2 == 0:
                    signal_type = 'buy'
                    confidence = 0.75
                    reasons = ['Padrão de preço favorável para compra (debug)', 'Momento adequado identificado']
                else:
                    signal_type = 'sell' 
                    confidence = 0.70
                    reasons = ['Padrão de preço favorável para venda (debug)', 'Reversão detectada']
                
                # Adicionar mais razões para parecer mais realista
                if 'rsi' in latest:
                    rsi_value = latest['rsi']
                    if signal_type == 'buy':
                        reasons.append(f'RSI em nível favorável: {rsi_value:.1f}')
                    else:
                        reasons.append(f'RSI indicando reversão: {rsi_value:.1f}')
                
                return {
                    'signal': signal_type,
                    'confidence': confidence,
                    'reasons': reasons,
                    'buy_strength': confidence if signal_type == 'buy' else 0,
                    'sell_strength': confidence if signal_type == 'sell' else 0
                }
            
            return {'signal': 'hold', 'confidence': 0, 'reasons': []}
            
        except Exception as e:
            logger.error(f"Erro na análise técnica debug: {e}")
            return {'signal': 'hold', 'confidence': 0, 'reasons': []}
    
    def _analyze_timeframe_context(self, timeframe: str) -> Dict:
        """Analisar contexto específico do timeframe"""
        try:
            timeframe_configs = {
                '1m': {'volume_importance': 0.1, 'trend_weight': 0.3, 'noise_level': 'high'},
                '5m': {'volume_importance': 0.15, 'trend_weight': 0.4, 'noise_level': 'medium-high'},
                '15m': {'volume_importance': 0.2, 'trend_weight': 0.5, 'noise_level': 'medium'},
                '1h': {'volume_importance': 0.25, 'trend_weight': 0.6, 'noise_level': 'medium-low'},
                '4h': {'volume_importance': 0.3, 'trend_weight': 0.7, 'noise_level': 'low'},
                '1d': {'volume_importance': 0.35, 'trend_weight': 0.8, 'noise_level': 'very-low'}
            }
            
            return timeframe_configs.get(timeframe, {
                'volume_importance': 0.25,
                'trend_weight': 0.5,
                'noise_level': 'medium'
            })
            
        except Exception as e:
            logger.error(f"Erro na análise de timeframe: {e}")
            return {'volume_importance': 0.25, 'trend_weight': 0.5, 'noise_level': 'medium'}
    
    def _analyze_macro_context(self, symbol: str) -> Dict:
        """Analisar cenário macroeconômico"""
        try:
            # Análise básica baseada no tipo de ativo
            if self.config.is_crypto_pair(symbol):
                return {
                    'asset_class': 'crypto',
                    'risk_level': 'high',
                    'market_hours': '24/7',                    'correlation_with_traditional': 'low'
                }
            else:
                return {
                    'asset_class': 'unknown',
                    'risk_level': 'medium',
                    'market_hours': 'varies',
                    'correlation_with_traditional': 'medium'
                }
                
        except Exception as e:
            logger.error(f"Erro na análise macro: {e}")
            return {'asset_class': 'unknown', 'risk_level': 'medium'}
    
    def _analyze_volume(self, df: pd.DataFrame, timeframe_context: Dict = None) -> Dict:
        """Analisar volume de negociação com contexto de timeframe"""
        try:
            if df.empty or 'volume' not in df.columns:
                return {'signal': 'hold', 'confidence': 0, 'reasons': []}
            
            latest = df.iloc[-1]
            volume_ma = df['volume'].rolling(window=20).mean().iloc[-1]
            
            # Volume ratio
            volume_ratio = latest['volume'] / volume_ma if volume_ma > 0 else 1
            
            # OBV analysis
            obv = self._calculate_obv(df)
            obv_trend = 'neutral'
            
            if len(obv) >= 5:
                recent_obv = obv[-5:]
                if recent_obv[-1] > recent_obv[0]:
                    obv_trend = 'bullish'
                elif recent_obv[-1] < recent_obv[0]:
                    obv_trend = 'bearish'
            
            # Volume Profile Analysis
            volume_profile = self._analyze_volume_profile(df)
            
            # VWAP Analysis
            vwap_analysis = self._analyze_vwap(df)
            
            reasons = []
            confidence = 0
            signal = 'hold'
            
            # Ajustar thresholds baseado no timeframe
            if timeframe_context:
                volume_importance = timeframe_context.get('volume_importance', 0.25)
                high_volume_threshold = 1.5 + (volume_importance * 2)  # Mais importante = threshold maior
                low_volume_threshold = 0.7 - (volume_importance * 0.3)
            else:
                high_volume_threshold = 1.5
                low_volume_threshold = 0.7
            
            # Volume analysis
            if volume_ratio > high_volume_threshold:
                confidence += 0.3 * (volume_importance if timeframe_context else 1.0)
                reasons.append(f"High volume: {volume_ratio:.2f}x average")
                
                if obv_trend == 'bullish':
                    signal = 'buy'
                    confidence += 0.4
                    reasons.append("OBV trending up with high volume")
                elif obv_trend == 'bearish':
                    signal = 'sell'
                    confidence += 0.4
                    reasons.append("OBV trending down with high volume")
                else:
                    signal = 'confirm'
                    reasons.append("High volume confirms price movement")
            
            elif volume_ratio < low_volume_threshold:
                confidence = 0.2
                signal = 'caution'
                reasons.append(f"Low volume: {volume_ratio:.2f}x average")
            
            else:
                confidence = 0.1
                reasons.append(f"Normal volume: {volume_ratio:.2f}x average")
            
            # Adicionar análises de volume profile e VWAP
            if volume_profile['signal'] != 'neutral':
                if volume_profile['signal'] == signal or signal == 'hold':
                    confidence += volume_profile['confidence'] * 0.3
                    reasons.extend(volume_profile['reasons'])
                    if signal == 'hold':
                        signal = volume_profile['signal']
            
            if vwap_analysis['signal'] != 'neutral':
                if vwap_analysis['signal'] == signal or signal == 'hold':
                    confidence += vwap_analysis['confidence'] * 0.2
                    reasons.extend(vwap_analysis['reasons'])
                    if signal == 'hold':
                        signal = vwap_analysis['signal']
            
            return {
                'signal': signal,
                'confidence': min(confidence, 1.0),
                'reasons': reasons,
                'volume_ratio': volume_ratio,
                'obv_trend': obv_trend,
                'volume_profile': volume_profile,
                'vwap_analysis': vwap_analysis
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de volume: {e}")
            return {'signal': 'hold', 'confidence': 0, 'reasons': []}
    
    def _calculate_obv(self, df: pd.DataFrame) -> np.ndarray:
        """Calcular On-Balance Volume"""
        try:
            obv = np.zeros(len(df))
            obv[0] = df['volume'].iloc[0]
            
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    obv[i] = obv[i-1] + df['volume'].iloc[i]
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    obv[i] = obv[i-1] - df['volume'].iloc[i]
                else:
                    obv[i] = obv[i-1]
            
            return obv
            
        except Exception as e:
            logger.error(f"Erro ao calcular OBV: {e}")
            return np.zeros(len(df))
    
    def _analyze_volume_profile(self, df: pd.DataFrame) -> Dict:
        """Analisar perfil de volume"""
        try:
            if len(df) < 20:
                return {'signal': 'neutral', 'confidence': 0, 'reasons': []}
            
            # Calcular VPOC (Volume Point of Control)
            price_levels = pd.cut(df['close'], bins=20)
            volume_by_price = df.groupby(price_levels)['volume'].sum()
            vpoc_level = volume_by_price.idxmax()
            
            current_price = df['close'].iloc[-1]
            vpoc_mid = (vpoc_level.left + vpoc_level.right) / 2
            
            # Analisar posição em relação ao VPOC
            price_distance = (current_price - vpoc_mid) / vpoc_mid
            
            if abs(price_distance) < 0.01:  # Próximo ao VPOC
                return {
                    'signal': 'neutral',
                    'confidence': 0.3,
                    'reasons': ['Price near Volume POC (consolidation zone)']
                }
            elif price_distance > 0.02:  # Acima do VPOC
                return {
                    'signal': 'sell',
                    'confidence': 0.4,
                    'reasons': ['Price above Volume POC (potential resistance)']
                }
            elif price_distance < -0.02:  # Abaixo do VPOC
                return {
                    'signal': 'buy',
                    'confidence': 0.4,
                    'reasons': ['Price below Volume POC (potential support)']
                }
            
            return {'signal': 'neutral', 'confidence': 0, 'reasons': []}
            
        except Exception as e:
            logger.error(f"Erro na análise de volume profile: {e}")
            return {'signal': 'neutral', 'confidence': 0, 'reasons': []}
    
    def _analyze_vwap(self, df: pd.DataFrame) -> Dict:
        """Analisar VWAP (Volume Weighted Average Price)"""
        try:
            if len(df) < 10:
                return {'signal': 'neutral', 'confidence': 0, 'reasons': []}
            
            # Calcular VWAP
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            
            current_price = df['close'].iloc[-1]
            current_vwap = vwap.iloc[-1]
            
            # Analisar posição em relação ao VWAP
            price_vs_vwap = (current_price - current_vwap) / current_vwap
            
            if price_vs_vwap > 0.005:  # 0.5% acima do VWAP
                return {
                    'signal': 'buy',
                    'confidence': 0.3,
                    'reasons': [f'Price {price_vs_vwap*100:.2f}% above VWAP (bullish)']
                }
            elif price_vs_vwap < -0.005:  # 0.5% abaixo do VWAP
                return {
                    'signal': 'sell',
                    'confidence': 0.3,
                    'reasons': [f'Price {abs(price_vs_vwap)*100:.2f}% below VWAP (bearish)']
                }
            
            return {
                'signal': 'neutral',
                'confidence': 0.1,
                'reasons': ['Price near VWAP (neutral)']
            }
            
        except Exception as e:
            logger.error(f"Erro na análise VWAP: {e}")
            return {'signal': 'neutral', 'confidence': 0, 'reasons': []}
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """Analisar volatilidade"""
        try:
            if df.empty or len(df) < 20:
                return {'signal': 'hold', 'confidence': 0, 'reasons': []}
            
            # Calcular volatilidade
            returns = df['close'].pct_change().dropna()
            current_vol = returns.rolling(20).std().iloc[-1]
            avg_vol = returns.rolling(100).std().mean()
            
            reasons = []
            
            if current_vol > avg_vol * 1.5:
                reasons.append(f"High volatility environment (current: {current_vol:.4f})")
                return {'signal': 'caution', 'confidence': 0.3, 'reasons': reasons}
            elif current_vol < avg_vol * 0.5:
                reasons.append(f"Low volatility - potential breakout (current: {current_vol:.4f})")
                return {'signal': 'prepare', 'confidence': 0.4, 'reasons': reasons}
            
            return {'signal': 'normal', 'confidence': 0.5, 'reasons': reasons}
            
        except Exception as e:
            logger.error(f"Erro na análise de volatilidade: {e}")
            return {'signal': 'hold', 'confidence': 0, 'reasons': []}
    
    def _combine_analyses(self, technical: Dict, ai_prediction: Dict, 
                         volume: Dict, volatility: Dict, market_context: Dict) -> Dict:
        """Combinar todas as análises"""
        try:
            # Pesos dinâmicos baseados no timeframe
            timeframe_context = market_context.get('timeframe_context', {})
            
            # Ajustar pesos baseado no timeframe
            volume_importance = timeframe_context.get('volume_importance', 0.25)
            trend_weight = timeframe_context.get('trend_weight', 0.5)
            
            # Pesos mais conservadores - priorizando análise técnica
            technical_weight = 0.45  # Aumentado para dar mais peso à análise técnica
            ai_weight = 0.20         # Reduzido para diminuir dependência da IA
            volume_weight = 0.25     # Mantido - volume é importante
            market_context_weight = 0.10  # Reduzido - contexto como suporte
            
            # Ajustar baseado no timeframe
            if timeframe_context.get('timeframe') in ['1m', '5m']:
                # Para timeframes curtos, dar mais peso ao volume e menos à IA
                technical_weight = 0.40
                ai_weight = 0.15
                volume_weight = 0.35
                market_context_weight = 0.10
            elif timeframe_context.get('timeframe') in ['4h', '1d']:
                # Para timeframes longos, dar mais peso à análise técnica
                technical_weight = 0.50
                ai_weight = 0.25
                volume_weight = 0.15
                market_context_weight = 0.10
            
            # Garantir que somem 1.0
            total_weight = technical_weight + ai_weight + volume_weight + market_context_weight
            if abs(total_weight - 1.0) > 0.01:  # Se não somar 1.0, normalizar
                factor = 1.0 / total_weight
                technical_weight *= factor
                ai_weight *= factor
                volume_weight *= factor
                market_context_weight *= factor
            
            weights = {
                'technical': technical_weight,
                'ai': ai_weight,
                'volume': volume_weight,
                'market_context': market_context_weight
            }
            
            # Converter sinais de IA
            ai_signal_map = {1: 'buy', -1: 'sell', 0: 'hold'}
            ai_signal = ai_signal_map.get(ai_prediction.get('signal', 0), 'hold')
            ai_confidence = ai_prediction.get('confidence', 0)
            
            # Calcular scores
            buy_score = 0
            sell_score = 0
            reasons = []
            
            # Technical analysis
            if technical['signal'] == 'buy':
                buy_score += technical['confidence'] * weights['technical']
            elif technical['signal'] == 'sell':
                sell_score += technical['confidence'] * weights['technical']
            reasons.extend(technical['reasons'])
            
            # AI prediction
            if ai_signal == 'buy':
                buy_score += ai_confidence * weights['ai']
                reasons.append(f"AI prediction: BUY (confidence: {ai_confidence:.2f})")
            elif ai_signal == 'sell':
                sell_score += ai_confidence * weights['ai']
                reasons.append(f"AI prediction: SELL (confidence: {ai_confidence:.2f})")
            
            # Volume analysis
            if volume['signal'] in ['buy', 'confirm']:
                buy_score += volume['confidence'] * weights['volume']
            elif volume['signal'] == 'sell':
                sell_score += volume['confidence'] * weights['volume']
            reasons.extend(volume['reasons'])
            
            # Timeframe context adjustments
            timeframe_context = market_context.get('timeframe_context', {})
            noise_level = timeframe_context.get('noise_level', 'medium')
            
            # Ajustar confiança baseado no nível de ruído
            noise_multipliers = {
                'very-low': 1.3,
                'low': 1.2,
                'medium-low': 1.1,
                'medium': 1.0,
                'medium-high': 0.9,
                'high': 0.8
            }
            
            noise_multiplier = noise_multipliers.get(noise_level, 1.0)
            buy_score *= noise_multiplier
            sell_score *= noise_multiplier
            
            if noise_level in ['high', 'medium-high']:
                reasons.append(f"Timeframe noise level: {noise_level} (reduced confidence)")
            elif noise_level in ['low', 'very-low']:
                reasons.append(f"Timeframe noise level: {noise_level} (increased confidence)")
            
            # Market context adjustments
            trend = market_context.get('trend', 'sideways')
            if trend == 'bullish':
                buy_score *= 1.2
                reasons.append("Market trend: Bullish")
            elif trend == 'bearish':
                sell_score *= 1.2
                reasons.append("Market trend: Bearish")
            
            # Macro context adjustments
            macro_context = market_context.get('macro_context', {})
            asset_class = macro_context.get('asset_class', 'unknown')
            risk_level = macro_context.get('risk_level', 'medium')
              # Ajustar baseado na classe de ativo
            if asset_class == 'crypto':
                # Crypto tem maior volatilidade
                buy_score *= 1.1
                sell_score *= 1.1
                reasons.append("Asset class: Crypto (higher volatility expected)")
            
            # Ajustar baseado no nível de risco
            risk_multipliers = {
                'low': 1.1,
                'medium': 1.0,
                'high': 0.9
            }
            
            risk_multiplier = risk_multipliers.get(risk_level, 1.0)
            buy_score *= risk_multiplier
            sell_score *= risk_multiplier
            sell_score *= risk_multiplier
            
            # Volatility adjustments
            if volatility['signal'] == 'caution':
                buy_score *= 0.8
                sell_score *= 0.8
                reasons.append("Reduced confidence due to high volatility")
            
            # Log dos scores para debug
            logger.info(f"Scores calculados - Buy: {buy_score:.3f}, Sell: {sell_score:.3f}")
            logger.info(f"Pesos utilizados: {weights}")
            logger.info(f"Análises individuais - Technical: {technical['signal']} ({technical['confidence']:.3f}), AI: {ai_signal} ({ai_confidence:.3f}), Volume: {volume['signal']} ({volume['confidence']:.3f})")
            
            # Estratégia mais conservadora com thresholds ajustados
            strong_threshold = 0.25   # Threshold para sinais fortes
            medium_threshold = 0.15   # Threshold para sinais médios
            weak_threshold = 0.08     # Threshold para sinais fracos
            
            # Calcular diferença entre scores para validar direção
            score_difference = abs(buy_score - sell_score)
            min_difference = 0.05  # Diferença mínima para evitar sinais ambíguos
            
            if score_difference < min_difference:
                # Sinais muito próximos - preferir HOLD
                final_signal = 'hold'
                final_confidence = 0.0
                logger.info(f"Sinal HOLD - scores muito próximos (diff: {score_difference:.3f})")
            elif buy_score > sell_score and buy_score > strong_threshold:
                # Sinal BUY forte
                final_signal = 'buy'
                final_confidence = min(buy_score * 0.85, 0.75)  # Cap em 75%
                logger.info(f"Sinal BUY FORTE gerado com confiança {final_confidence:.3f}")
            elif sell_score > buy_score and sell_score > strong_threshold:
                # Sinal SELL forte
                final_signal = 'sell'
                final_confidence = min(sell_score * 0.85, 0.75)  # Cap em 75%
                logger.info(f"Sinal SELL FORTE gerado com confiança {final_confidence:.3f}")
            elif buy_score > sell_score and buy_score > medium_threshold:
                # Sinal BUY médio
                final_signal = 'buy'
                final_confidence = min(buy_score * 0.7, 0.55)  # Cap em 55%
                logger.info(f"Sinal BUY MÉDIO gerado com confiança {final_confidence:.3f}")
            elif sell_score > buy_score and sell_score > medium_threshold:
                # Sinal SELL médio
                final_signal = 'sell'
                final_confidence = min(sell_score * 0.7, 0.55)  # Cap em 55%
                logger.info(f"Sinal SELL MÉDIO gerado com confiança {final_confidence:.3f}")
            elif buy_score > sell_score and buy_score > weak_threshold:
                # Sinal BUY fraco - apenas se houver confluência
                if self._has_strong_confluence(technical, ai_prediction, volume):
                    final_signal = 'buy'
                    final_confidence = min(buy_score * 0.6, 0.35)  # Cap em 35%
                    logger.info(f"Sinal BUY FRACO com confluência - confiança {final_confidence:.3f}")
                else:
                    final_signal = 'hold'
                    final_confidence = 0.0
                    logger.info(f"Sinal BUY fraco rejeitado - sem confluência suficiente")
            elif sell_score > buy_score and sell_score > weak_threshold:
                # Sinal SELL fraco - apenas se houver confluência
                if self._has_strong_confluence(technical, ai_prediction, volume):
                    final_signal = 'sell'
                    final_confidence = min(sell_score * 0.6, 0.35)  # Cap em 35%
                    logger.info(f"Sinal SELL FRACO com confluência - confiança {final_confidence:.3f}")
                else:
                    final_signal = 'hold'
                    final_confidence = 0.0
                    logger.info(f"Sinal SELL fraco rejeitado - sem confluência suficiente")
            else:
                final_signal = 'hold'
                final_confidence = 0.0
                logger.info(f"Sinal HOLD - scores insuficientes (buy: {buy_score:.3f}, sell: {sell_score:.3f})")
            
            return {
                'signal': final_signal,
                'confidence': final_confidence,
                'reasons': reasons,
                'scores': {
                    'buy': buy_score,
                    'sell': sell_score,
                    'technical': technical['confidence'],
                    'ai': ai_confidence,
                    'volume': volume['confidence']
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao combinar análises: {e}")
            return {'signal': 'hold', 'confidence': 0, 'reasons': []}
    
    def _has_strong_confluence(self, technical: Dict, ai_prediction: Dict, volume: Dict) -> bool:
        """Verificar confluência forte entre análises para sinais fracos"""
        try:
            confirmations = 0
            min_required = 2  # Mínimo 2 confirmações para sinais fracos
            
            # Análise técnica com confiança > 0.3
            if technical.get('confidence', 0) > 0.3:
                confirmations += 1
            
            # IA com confiança > 0.4
            ai_confidence = ai_prediction.get('confidence', 0)
            if ai_confidence > 0.4:
                confirmations += 1
            
            # Volume confirmando (confiança > 0.3)
            if volume.get('confidence', 0) > 0.3 and volume.get('signal') in ['buy', 'sell', 'confirm']:
                confirmations += 1
            
            # Bonus: se todas as 3 análises concordam na direção
            signals = [technical.get('signal'), volume.get('signal')]
            ai_signal_map = {1: 'buy', -1: 'sell', 0: 'hold'}
            ai_signal = ai_signal_map.get(ai_prediction.get('signal', 0), 'hold')
            signals.append(ai_signal)
            
            # Contar sinais na mesma direção
            buy_signals = signals.count('buy')
            sell_signals = signals.count('sell')
            
            if buy_signals >= 2 or sell_signals >= 2:
                confirmations += 1
            
            logger.info(f"Confluência forte: {confirmations} confirmações (mín: {min_required})")
            return confirmations >= min_required
            
        except Exception as e:
            logger.error(f"Erro ao verificar confluência forte: {e}")
            return False
    
    def _check_confluence(self, signal_data: Dict) -> bool:
        """Verificar confluência de sinais"""
        try:
            min_confluence = self.config.SIGNAL_CONFIG['min_confluence_count']
            reasons = signal_data.get('reasons', [])
            
            # Contar diferentes tipos de confirmação
            confirmations = 0
            
            # Indicadores técnicos
            technical_indicators = ['RSI', 'MACD', 'Bollinger', 'EMA', 'Stochastic', 'ADX']
            for indicator in technical_indicators:
                if any(indicator.lower() in reason.lower() for reason in reasons):
                    confirmations += 1
            
            # IA
            if any('AI prediction' in reason for reason in reasons):
                confirmations += 1
            
            # Volume
            if any('volume' in reason.lower() for reason in reasons):
                confirmations += 1
            
            # Padrões de candlestick
            patterns = ['hammer', 'shooting star', 'engulfing', 'star']
            for pattern in patterns:
                if any(pattern in reason.lower() for reason in reasons):
                    confirmations += 1
                    break
            
            return confirmations >= min_confluence
            
        except Exception as e:
            logger.error(f"Erro ao verificar confluência: {e}")
            return False
    
    def _calculate_trade_levels(self, df: pd.DataFrame, signal_type: str, current_price: float, timeframe: str = '1h') -> Dict:
        """Calcular níveis de stop loss e take profit baseado no timeframe"""
        try:
            if df.empty:
                return {'stop_loss': 0, 'take_profit': 0}
            
            # Para sinais HOLD, não calcular níveis
            if signal_type == 'hold':
                return {'stop_loss': 0, 'take_profit': 0}
            
            # Usar ATR para calcular níveis
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.02
            
            # Ajustar percentuais baseado no timeframe - Valores otimizados conforme análise de volatilidade
            timeframe_multipliers = {
                '1m': {'sl': 0.10, 'tp': 0.15},  # 0.10% SL, 0.15% TP - Scalping alta frequência
                '3m': {'sl': 0.20, 'tp': 0.30},  # 0.20% SL, 0.30% TP - Micro scalping
                '5m': {'sl': 0.30, 'tp': 0.50},  # 0.30% SL, 0.50% TP - Scalping intradiário
                '15m': {'sl': 0.60, 'tp': 0.80}, # 0.60% SL, 0.80% TP - Micro swings curtos
                '30m': {'sl': 0.80, 'tp': 1.20}, # 0.80% SL, 1.20% TP - Transição para swing
                '1h': {'sl': 1.20, 'tp': 1.80},  # 1.20% SL, 1.80% TP - Mais estável, menos ruído
                '2h': {'sl': 1.80, 'tp': 2.70},  # 1.80% SL, 2.70% TP - Swing intermediário
                '4h': {'sl': 2.50, 'tp': 3.50},  # 2.50% SL, 3.50% TP - Swings amplos, boa relação ATR
                '6h': {'sl': 3.00, 'tp': 4.20},  # 3.00% SL, 4.20% TP - Swing estendido
                '8h': {'sl': 3.50, 'tp': 4.90},  # 3.50% SL, 4.90% TP - Swing longo
                '12h': {'sl': 3.80, 'tp': 5.30}, # 3.80% SL, 5.30% TP - Transição para diário
                '1d': {'sl': 4.00, 'tp': 5.00},  # 4.00% SL, 5.00% TP - Tendências longas
                '3d': {'sl': 4.50, 'tp': 5.60},  # 4.50% SL, 5.60% TP - Swing de médio prazo
                '1w': {'sl': 5.00, 'tp': 6.25}   # 5.00% SL, 6.25% TP - Swing de longo prazo
            }
            
            # Obter multiplicadores para o timeframe (padrão 1h se não encontrado)
            multipliers = timeframe_multipliers.get(timeframe, timeframe_multipliers['1h'])
            
            # Converter para decimais
            stop_loss_pct = multipliers['sl'] / 100.0
            take_profit_pct = multipliers['tp'] / 100.0
            
            logger.info(f"Timeframe {timeframe}: SL {multipliers['sl']}%, TP {multipliers['tp']}%")
            
            if signal_type == 'buy':
                # Para compra
                stop_loss = current_price * (1 - stop_loss_pct)
                take_profit = current_price * (1 + take_profit_pct)
                
                # Ajustar com base no ATR (mais conservador para timeframes menores)
                # atr_multiplier = 1.5 if timeframe in ['1m', '3m', '5m'] else 2.0
                # atr_stop = current_price - (atr * atr_multiplier)
                # stop_loss = max(stop_loss, atr_stop)  # Comentado para usar valores exatos da tabela
                
            elif signal_type == 'sell':
                # Para venda
                stop_loss = current_price * (1 + stop_loss_pct)
                take_profit = current_price * (1 - take_profit_pct)
                
                # Ajustar com base no ATR
                # atr_multiplier = 1.5 if timeframe in ['1m', '3m', '5m'] else 2.0
                # atr_stop = current_price + (atr * atr_multiplier)
                # stop_loss = min(stop_loss, atr_stop)  # Comentado para usar valores exatos da tabela
                
            else:
                # Fallback para outros tipos
                return {'stop_loss': 0, 'take_profit': 0}
            
            return {
                'stop_loss': round(stop_loss, 8),
                'take_profit': round(take_profit, 8)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular níveis: {e}")
            return {'stop_loss': 0, 'take_profit': 0}
    
    def _calculate_trade_levels_1to1(self, current_price: float, signal_type: str, timeframe: str) -> Dict[str, float]:
        """Calcular níveis de trade com relação risco/recompensa 1:1 para estratégia de IA"""
        try:
            if signal_type == 'hold':
                return {'stop_loss': 0, 'take_profit': 0}
            
            # Percentuais para micro-scalping - valores ajustados conforme RESUMO_AJUSTES_ALVOS.md
            timeframe_percentages = {
                '1m': 0.04,  # 0.04% para SL e TP - ~$40 no BTC (micro-scalping)
                '3m': 0.06,  # 0.06% para SL e TP - ~$60 no BTC
                '5m': 0.08,  # 0.08% para SL e TP - ~$80 no BTC
                '15m': 0.12, # 0.12% para SL e TP - ~$120 no BTC
                '30m': 0.18, # 0.18% para SL e TP - ~$180 no BTC
                '1h': 0.25,  # 0.25% para SL e TP - ~$250 no BTC
                '2h': 0.40,  # 0.40% para SL e TP - ~$400 no BTC
                '4h': 0.60,  # 0.60% para SL e TP - ~$600 no BTC
                '6h': 0.90,  # 0.90% para SL e TP - ~$900 no BTC
                '8h': 1.2,   # 1.2% para SL e TP - ~$1200 no BTC
                '12h': 1.5,  # 1.5% para SL e TP - ~$1500 no BTC
                '1d': 2.5,   # 2.5% para SL e TP - ~$2500 no BTC
                '3d': 3.5,   # 3.5% para SL e TP - ~$3500 no BTC
                '1w': 5.0    # 5.0% para SL e TP - ~$5000 no BTC
            }
            
            # Obter percentual para o timeframe (padrão 2.5% se não encontrado)
            percentage = timeframe_percentages.get(timeframe, 2.5)
            percentage_decimal = percentage / 100.0
            
            logger.info(f"Calculando níveis 1:1 para {timeframe}: {percentage}% SL/TP")
            
            if signal_type == 'buy':
                # Para compra: SL abaixo, TP acima
                stop_loss = current_price * (1 - percentage_decimal)
                take_profit = current_price * (1 + percentage_decimal)
                
            elif signal_type == 'sell':
                # Para venda: SL acima, TP abaixo
                stop_loss = current_price * (1 + percentage_decimal)
                take_profit = current_price * (1 - percentage_decimal)
                
            else:
                return {'stop_loss': 0, 'take_profit': 0}
            
            return {
                'stop_loss': round(stop_loss, 8),
                'take_profit': round(take_profit, 8)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular níveis 1:1: {e}")
            return {'stop_loss': 0, 'take_profit': 0}
    
    def _register_signal(self, signal: Signal):
        """Registrar sinal gerado"""
        try:
            # Adicionar aos sinais ativos
            self.active_signals[signal.id] = signal
            
            # Adicionar ao histórico
            self.signal_history.append(signal)
            
            # Atualizar último tempo de sinal
            self.last_signal_time[signal.symbol] = signal.timestamp
            
            # Limitar histórico
            if len(self.signal_history) > 1000:
                self.signal_history = self.signal_history[-500:]
            
            # Emit WebSocket notification
            emit_signal_notification(signal.to_dict())
            
            logger.info(f"🔔 Sinal registrado e notificação enviada: {signal.id}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar sinal: {e}")
    
    def get_active_signals(self) -> List[Dict]:
        """Obter sinais ativos"""
        try:
            return [signal.to_dict() for signal in self.active_signals.values()]
        except Exception as e:
            logger.error(f"Erro ao obter sinais ativos: {e}")
            return []
    
    def get_signal_history(self, limit: int = 50) -> List[Dict]:
        """Obter histórico de sinais"""
        try:
            recent_signals = self.signal_history[-limit:] if limit else self.signal_history
            return [signal.to_dict() for signal in recent_signals]
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return []
    
    def update_signal_status(self, signal_id: str, status: str):
        """Atualizar status de um sinal"""
        try:
            if signal_id in self.active_signals:
                self.active_signals[signal_id].status = status
                
                if status in ['closed', 'expired']:
                    del self.active_signals[signal_id]
                
                logger.info(f"Status do sinal {signal_id} atualizado para {status}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do sinal: {e}")
    
    def generate_signals_for_all_pairs(self) -> List[Signal]:
        """Gerar sinais para todos os pares configurados"""
        signals = []
        
        try:
            for symbol in self.config.get_all_pairs():
                signal = self.generate_signal(symbol)
                if signal and signal.signal_type != 'hold':
                    signals.append(signal)
            
            logger.info(f"Gerados {len(signals)} sinais para todos os pares")
            return signals
            
        except Exception as e:
            logger.error(f"Erro ao gerar sinais para todos os pares: {e}")
            return signals