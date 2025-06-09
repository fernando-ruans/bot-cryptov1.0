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

logger = logging.getLogger(__name__)

# Global variable to store socketio instance for notifications
_socketio_instance = None

def set_socketio_instance(socketio):
    """Set the global socketio instance for notifications"""
    global _socketio_instance
    _socketio_instance = socketio

def emit_signal_notification(signal_data):
    """Emit signal notification via WebSocket"""
    global _socketio_instance
    if _socketio_instance:
        try:
            _socketio_instance.emit('new_signal', signal_data)
            logger.info(f"📡 Notificação de sinal enviada via WebSocket: {signal_data.get('symbol')} {signal_data.get('signal_type')}")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de sinal: {e}")

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
        self.active_signals = {}
        self.signal_history = []
        self.last_signal_time = {}
        
    def generate_signal(self, symbol: str, timeframe: str = '1h') -> Optional[Signal]:
        """Gerar sinal de trading para um símbolo"""
        try:
            logger.info(f"=== Iniciando geração de sinal para {symbol} {timeframe} ===")
            
            # Verificar cooldown
            if self._is_in_cooldown(symbol):
                logger.info(f"Símbolo {symbol} em cooldown")
                raise ValueError(f"COOLDOWN:{symbol}")
            logger.info(f"✓ Cooldown OK para {symbol}")
            
            # Obter dados de mercado
            df = self.market_data.get_historical_data(symbol, timeframe, 500)
            logger.info(f"Dados obtidos para {symbol}: {len(df)} registros")
            
            # Validação robusta dos dados
            if df is None:
                logger.error(f"DataFrame é None para {symbol}")
                raise ValueError(f"NO_DATA:{symbol}")
            
            if df.empty:
                logger.warning(f"DataFrame vazio para {symbol}")
                raise ValueError(f"EMPTY_DATA:{symbol}")
                
            if len(df) < 100:
                logger.warning(f"Dados insuficientes para {symbol}: {len(df)} registros")
                raise ValueError(f"INSUFFICIENT_DATA:{symbol}:{len(df)}")
            
            # Verificar se as colunas essenciais existem
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Colunas faltantes no DataFrame para {symbol}: {missing_columns}")
                raise ValueError(f"MISSING_COLUMNS:{symbol}:{','.join(missing_columns)}")
            
            # Verificar se há dados válidos (não NaN)
            if df[required_columns].isnull().all().any():
                logger.error(f"Dados contêm apenas valores NaN para {symbol}")
                raise ValueError(f"INVALID_DATA:{symbol}")
                
            logger.info(f"✓ Dados válidos para {symbol}: {len(df)} registros")
            
            # Calcular indicadores técnicos
            logger.info(f"Calculando indicadores técnicos para {symbol}")
            try:
                df = self.technical_indicators.calculate_all_indicators(df)
                if df is None or df.empty:
                    logger.error(f"Falha ao calcular indicadores técnicos para {symbol}")
                    raise ValueError(f"INDICATORS_FAILED:{symbol}")
                logger.info(f"✓ Indicadores técnicos calculados para {symbol}")
            except Exception as e:
                logger.error(f"Erro ao calcular indicadores técnicos para {symbol}: {e}")
                return None
            
            # Análise de contexto de mercado
            logger.info(f"Analisando contexto de mercado para {symbol}")
            try:
                market_context = self._analyze_market_context(symbol, timeframe)
                logger.info(f"✓ Contexto de mercado analisado para {symbol}")
            except Exception as e:
                logger.error(f"Erro na análise de contexto para {symbol}: {e}")
                market_context = {}
            
            # Análise técnica
            logger.info(f"Executando análise técnica para {symbol}")
            try:
                technical_analysis = self._analyze_technical_indicators(df)
                if not technical_analysis or 'signal' not in technical_analysis:
                    logger.error(f"Análise técnica retornou resultado inválido para {symbol}")
                    return None
                logger.info(f"✓ Análise técnica: {technical_analysis['signal']} (confiança: {technical_analysis['confidence']:.2f})")
            except Exception as e:
                logger.error(f"Erro na análise técnica para {symbol}: {e}")
                return None
            
            # Predição de IA
            logger.info(f"Executando predição de IA para {symbol}")
            try:
                ai_prediction = self.ai_engine.predict_signal(df, symbol)
                logger.info(f"✓ Predição de IA concluída para {symbol}")
            except Exception as e:
                logger.error(f"Erro na predição de IA para {symbol}: {e}")
                ai_prediction = {'signal': 'hold', 'confidence': 0.0, 'reasons': []}
            
            # Análise de volume
            logger.info(f"Analisando volume para {symbol}")
            volume_analysis = self._analyze_volume(df)
            logger.info(f"✓ Análise de volume: {volume_analysis['signal']} (confiança: {volume_analysis['confidence']:.2f})")
            
            # Análise de volatilidade
            logger.info(f"Analisando volatilidade para {symbol}")
            volatility_analysis = self._analyze_volatility(df)
            logger.info(f"✓ Análise de volatilidade: {volatility_analysis['signal']} (confiança: {volatility_analysis['confidence']:.2f})")
            
            # Combinar análises
            logger.info(f"Combinando todas as análises para {symbol}")
            combined_signal = self._combine_analyses(
                technical_analysis,
                ai_prediction,
                volume_analysis,
                volatility_analysis,
                market_context
            )
            logger.info(f"✓ Sinal combinado: {combined_signal['signal']} (confiança: {combined_signal['confidence']:.2f})")
            
            # Verificar confluência
            if self.config.SIGNAL_CONFIG['enable_confluence']:
                logger.info(f"Verificando confluência para {symbol}")
                if not self._check_confluence(combined_signal):
                    logger.info(f"Confluência insuficiente para {symbol}")
                    raise ValueError(f"LOW_CONFLUENCE:{symbol}")
                logger.info(f"✓ Confluência verificada para {symbol}")
            else:
                logger.info(f"✓ Confluência desabilitada")
            
            # REMOVIDA: Verificação de confiança mínima
            # Agora sempre gera o sinal com a confiança calculada
            # O usuário decide se aceita ou não o sinal na interface
            logger.info(f"✓ Sinal será gerado com confiança: {combined_signal['confidence']:.2f}")
            
            # Calcular níveis de entrada, stop loss e take profit
            logger.info(f"Obtendo preço atual para {symbol}")
            current_price = self.market_data.get_current_price(symbol)
            if current_price is None:
                logger.error(f"Não foi possível obter preço atual para {symbol}")
                raise ValueError(f"PRICE_ERROR:{symbol}")
            logger.info(f"✓ Preço atual obtido para {symbol}: ${current_price:.2f}")
            
            logger.info(f"Calculando níveis de trade para {symbol}")
            levels = self._calculate_trade_levels(df, combined_signal['signal'], current_price)
            logger.info(f"✓ Níveis calculados - SL: ${levels['stop_loss']:.2f}, TP: ${levels['take_profit']:.2f}")
            
            # Criar sinal
            logger.info(f"Criando objeto de sinal para {symbol}")
            signal = Signal(
                symbol=symbol,
                signal_type=combined_signal['signal'],
                confidence=combined_signal['confidence'],
                entry_price=current_price,
                stop_loss=levels['stop_loss'],
                take_profit=levels['take_profit'],
                timeframe=timeframe,
                timestamp=datetime.now(),
                reasons=combined_signal['reasons']
            )
            logger.info(f"✓ Objeto de sinal criado para {symbol}")
            
            # Registrar sinal
            logger.info(f"Registrando sinal para {symbol}")
            self._register_signal(signal)
            logger.info(f"✓ Sinal registrado para {symbol}")
            
            logger.info(f"🎯 SINAL GERADO COM SUCESSO: {signal.signal_type} {symbol} - Confiança: {signal.confidence:.2f}")
            logger.info(f"=== Fim da geração de sinal para {symbol} ===")
            
            return signal
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Erro ao gerar sinal para {symbol}: {e}")
            logger.error(f"Detalhes do erro: {error_details}")
            
            # Tentar identificar o tipo específico do erro
            if "KeyError" in str(e):
                logger.error(f"Erro de chave faltante: {e}")
            elif "AttributeError" in str(e):
                logger.error(f"Erro de atributo: {e}")
            elif "NoneType" in str(e):
                logger.error(f"Erro de valor None: {e}")
            elif "DataFrame" in str(e):
                logger.error(f"Erro relacionado ao DataFrame: {e}")
            
            return None
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Verificar se símbolo está em cooldown"""
        if symbol not in self.last_signal_time:
            return False
        
        cooldown_minutes = self.config.SIGNAL_CONFIG['signal_cooldown_minutes']
        time_diff = datetime.now() - self.last_signal_time[symbol]
        
        return time_diff.total_seconds() < (cooldown_minutes * 60)
    
    def _analyze_market_context(self, symbol: str, timeframe: str) -> Dict:
        """Analisar contexto de mercado"""
        try:
            # Estrutura de mercado
            market_structure = self.market_data.detect_market_structure(symbol, timeframe)
            
            # Perfil de volume
            volume_profile = self.market_data.get_volume_profile(symbol, timeframe)
            
            # Volatilidade
            volatility = self.market_data.calculate_volatility(symbol, timeframe)
            
            # Correlações (exemplo com BTC para altcoins)
            correlation = 0
            if symbol != 'BTCUSDT' and self.config.is_crypto_pair(symbol):
                correlation = self.market_data.get_market_correlation(symbol, 'BTCUSDT', timeframe)
            
            return {
                'trend': market_structure.get('trend', 'sideways'),
                'support_levels': market_structure.get('support_levels', []),
                'resistance_levels': market_structure.get('resistance_levels', []),
                'volume_ratio': volume_profile.get('volume_ratio', 1.0),
                'volatility': volatility,
                'btc_correlation': correlation
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
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analisar volume"""
        try:
            if df.empty or 'volume' not in df.columns:
                return {'signal': 'hold', 'confidence': 0, 'reasons': []}
            
            latest = df.iloc[-1]
            reasons = []
            
            # Volume ratio
            if 'volume_ratio' in latest:
                volume_ratio = latest['volume_ratio']
                if volume_ratio > self.config.VOLUME_INDICATORS['volume_threshold_multiplier']:
                    confidence = min(volume_ratio / 3.0, 0.8)
                    reasons.append(f"High volume confirmation (ratio: {volume_ratio:.1f})")
                    return {'signal': 'confirm', 'confidence': confidence, 'reasons': reasons}
            
            # OBV trend
            if 'obv' in df.columns and len(df) >= 10:
                obv_trend = df['obv'].iloc[-5:].diff().mean()
                if obv_trend > 0:
                    reasons.append("OBV showing accumulation")
                    return {'signal': 'buy', 'confidence': 0.4, 'reasons': reasons}
                elif obv_trend < 0:
                    reasons.append("OBV showing distribution")
                    return {'signal': 'sell', 'confidence': 0.4, 'reasons': reasons}
            
            return {'signal': 'hold', 'confidence': 0, 'reasons': reasons}
            
        except Exception as e:
            logger.error(f"Erro na análise de volume: {e}")
            return {'signal': 'hold', 'confidence': 0, 'reasons': []}
    
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
            # Pesos das análises
            weights = {
                'technical': 0.4,
                'ai': 0.3,
                'volume': 0.2,
                'market_context': 0.1
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
            
            # Market context adjustments
            trend = market_context.get('trend', 'sideways')
            if trend == 'bullish':
                buy_score *= 1.2
                reasons.append("Market trend: Bullish")
            elif trend == 'bearish':
                sell_score *= 1.2
                reasons.append("Market trend: Bearish")
            
            # Volatility adjustments
            if volatility['signal'] == 'caution':
                buy_score *= 0.8
                sell_score *= 0.8
                reasons.append("Reduced confidence due to high volatility")
            
            # Determinar sinal final
            if buy_score > sell_score and buy_score > 0.3:
                final_signal = 'buy'
                final_confidence = min(buy_score, 1.0)
            elif sell_score > buy_score and sell_score > 0.3:
                final_signal = 'sell'
                final_confidence = min(sell_score, 1.0)
            else:
                final_signal = 'hold'
                final_confidence = 0.0
            
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
    
    def _calculate_trade_levels(self, df: pd.DataFrame, signal_type: str, current_price: float) -> Dict:
        """Calcular níveis de stop loss e take profit"""
        try:
            if df.empty:
                return {'stop_loss': current_price, 'take_profit': current_price}
            
            # Usar ATR para calcular níveis
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.02
            
            # Configurações de risco
            stop_loss_pct = self.config.RISK_MANAGEMENT['stop_loss_pct']
            take_profit_pct = self.config.RISK_MANAGEMENT['take_profit_pct']
            
            if signal_type == 'buy':
                # Para compra
                stop_loss = current_price * (1 - stop_loss_pct)
                take_profit = current_price * (1 + take_profit_pct)
                
                # Ajustar com base no ATR
                atr_stop = current_price - (atr * 2)
                stop_loss = max(stop_loss, atr_stop)
                
            elif signal_type == 'sell':
                # Para venda
                stop_loss = current_price * (1 + stop_loss_pct)
                take_profit = current_price * (1 - take_profit_pct)
                
                # Ajustar com base no ATR
                atr_stop = current_price + (atr * 2)
                stop_loss = min(stop_loss, atr_stop)
                
            else:
                stop_loss = current_price
                take_profit = current_price
            
            return {
                'stop_loss': round(stop_loss, 8),
                'take_profit': round(take_profit, 8)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular níveis: {e}")
            return {'stop_loss': current_price, 'take_profit': current_price}
    
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