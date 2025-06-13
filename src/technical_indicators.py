#!/usr/bin/env python3
"""
Indicadores técnicos para análise de mercado
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Classe para calcular indicadores técnicos"""
    
    def __init__(self, config):
        self.config = config
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular todos os indicadores técnicos"""
        try:
            df = df.copy()
            
            # Médias móveis
            df = self._add_moving_averages(df)
            
            # Indicadores de momentum
            df = self._add_momentum_indicators(df)
            
            # Indicadores de volatilidade
            df = self._add_volatility_indicators(df)
              # Indicadores de volume
            df = self._add_volume_indicators(df)
            
            # MELHORIA 2: Indicadores avançados de volume
            df = self._add_advanced_volume_indicators(df)
            
            # Indicadores de tendência
            df = self._add_trend_indicators(df)
              # Padrões de candlestick
            df = self._add_candlestick_patterns(df)
            
            # MELHORIA 3: Padrões avançados de candlestick
            df = self._add_advanced_candlestick_patterns(df)
            
            # MELHORIA 3: Padrões de Candlestick Automáticos Avançados
            df = self._add_advanced_candlestick_patterns(df)
            
            # MELHORIA 5: ANÁLISE DE SENTIMENTO DE MERCADO
            df = self._add_market_sentiment_indicators(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao calcular indicadores: {e}")
            return df
    
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar médias móveis"""
        # SMA (Simple Moving Average)
        for period in self.config.TECHNICAL_INDICATORS['sma_periods']:
            df[f'sma_{period}'] = ta.trend.sma_indicator(df['close'], window=period)
        
        # EMA (Exponential Moving Average)
        for period in self.config.TECHNICAL_INDICATORS['ema_periods']:
            df[f'ema_{period}'] = ta.trend.ema_indicator(df['close'], window=period)
        
        # WMA (Weighted Moving Average)
        df['wma_20'] = ta.trend.wma_indicator(df['close'], window=20)
        
        return df
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar indicadores de momentum"""
        # RSI (Relative Strength Index)
        rsi_period = self.config.TECHNICAL_INDICATORS['rsi_period']
        df['rsi'] = ta.momentum.rsi(df['close'], window=rsi_period)
        
        # MACD (Moving Average Convergence Divergence)
        macd_fast = self.config.TECHNICAL_INDICATORS['macd_fast']
        macd_slow = self.config.TECHNICAL_INDICATORS['macd_slow']
        macd_signal = self.config.TECHNICAL_INDICATORS['macd_signal']
        
        macd_line = ta.trend.macd_diff(df['close'], window_fast=macd_fast, window_slow=macd_slow)
        macd_signal_line = ta.trend.macd_signal(df['close'], window_fast=macd_fast, 
                                               window_slow=macd_slow, window_sign=macd_signal)
        
        df['macd'] = macd_line
        df['macd_signal'] = macd_signal_line
        df['macd_histogram'] = macd_line - macd_signal_line
        
        # Stochastic Oscillator
        stoch_k = self.config.TECHNICAL_INDICATORS['stoch_k']
        stoch_d = self.config.TECHNICAL_INDICATORS['stoch_d']
        
        df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'], 
                                         window=stoch_k, smooth_window=stoch_d)
        df['stoch_d'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'], 
                                                window=stoch_k, smooth_window=stoch_d)
        
        # Williams %R
        df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'], lbp=14)
        
        # CCI (Commodity Channel Index)
        df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'], window=20)
        
        # ROC (Rate of Change)
        df['roc'] = ta.momentum.roc(df['close'], window=12)
        
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar indicadores de volatilidade"""
        # Bollinger Bands
        bb_period = self.config.TECHNICAL_INDICATORS['bb_period']
        bb_std = self.config.TECHNICAL_INDICATORS['bb_std']
        
        df['bb_upper'] = ta.volatility.bollinger_hband(df['close'], window=bb_period, window_dev=bb_std)
        df['bb_middle'] = ta.volatility.bollinger_mavg(df['close'], window=bb_period)
        df['bb_lower'] = ta.volatility.bollinger_lband(df['close'], window=bb_period, window_dev=bb_std)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR (Average True Range)
        atr_period = self.config.TECHNICAL_INDICATORS['atr_period']
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=atr_period)
        
        # Keltner Channels
        df['kc_upper'] = ta.volatility.keltner_channel_hband(df['high'], df['low'], df['close'], window=20)
        df['kc_middle'] = ta.volatility.keltner_channel_mband(df['high'], df['low'], df['close'], window=20)
        df['kc_lower'] = ta.volatility.keltner_channel_lband(df['high'], df['low'], df['close'], window=20)
        
        # Donchian Channels
        df['dc_upper'] = ta.volatility.donchian_channel_hband(df['high'], df['low'], df['close'], window=20)
        df['dc_lower'] = ta.volatility.donchian_channel_lband(df['high'], df['low'], df['close'], window=20)
        
        return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar indicadores de volume"""
        # Volume SMA
        volume_period = self.config.VOLUME_INDICATORS['volume_sma_period']
        df['volume_sma'] = df['volume'].rolling(window=volume_period).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # OBV (On-Balance Volume)
        if self.config.VOLUME_INDICATORS['obv_enabled']:
            df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
        
        # VWAP (Volume Weighted Average Price)
        if self.config.VOLUME_INDICATORS['vwap_enabled']:
            df['vwap'] = ta.volume.volume_weighted_average_price(df['high'], df['low'], 
                                                               df['close'], df['volume'])
        
        # Money Flow Index
        df['mfi'] = ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume'], window=14)
        
        # Accumulation/Distribution Line
        df['ad_line'] = ta.volume.acc_dist_index(df['high'], df['low'], df['close'], df['volume'])
        
        # Chaikin Money Flow
        df['cmf'] = ta.volume.chaikin_money_flow(df['high'], df['low'], df['close'], df['volume'], window=20)
        
        # Volume Price Trend
        df['vpt'] = ta.volume.volume_price_trend(df['close'], df['volume'])
        
        # Indicadores avançados de volume
        df = self._add_advanced_volume_indicators(df)
        
        return df
    
    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar indicadores de tendência"""
        # ADX (Average Directional Index)
        adx_period = self.config.TECHNICAL_INDICATORS['adx_period']
        df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)
        df['adx_pos'] = ta.trend.adx_pos(df['high'], df['low'], df['close'], window=adx_period)
        df['adx_neg'] = ta.trend.adx_neg(df['high'], df['low'], df['close'], window=adx_period)
        
        # Parabolic SAR
        df['psar'] = ta.trend.psar_down(df['high'], df['low'], df['close'])        
        # Aroon - comentado temporariamente devido a problemas de versão
        # aroon = ta.trend.AroonIndicator(high=df['high'], low=df['low'], window=25)
        # df['aroon_up'] = aroon.aroon_up()
        # df['aroon_down'] = aroon.aroon_down()
        # df['aroon_indicator'] = df['aroon_up'] - df['aroon_down']
        
        # TRIX
        df['trix'] = ta.trend.trix(df['close'], window=14)
        
        # Mass Index
        df['mass_index'] = ta.trend.mass_index(df['high'], df['low'], window_fast=9, window_slow=25)
        
        # Vortex Indicator
        df['vortex_pos'] = ta.trend.vortex_indicator_pos(df['high'], df['low'], df['close'], window=14)
        df['vortex_neg'] = ta.trend.vortex_indicator_neg(df['high'], df['low'], df['close'], window=14)
        
        return df
    
    def _add_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar padrões de candlestick"""
        try:
            # Doji
            df['doji'] = self._detect_doji(df)
            
            # Hammer
            df['hammer'] = self._detect_hammer(df)
            
            # Shooting Star
            df['shooting_star'] = self._detect_shooting_star(df)
            
            # Engulfing patterns
            df['bullish_engulfing'] = self._detect_bullish_engulfing(df)
            df['bearish_engulfing'] = self._detect_bearish_engulfing(df)
            
            # Morning/Evening Star
            df['morning_star'] = self._detect_morning_star(df)
            df['evening_star'] = self._detect_evening_star(df)
            
        except Exception as e:
            logger.error(f"Erro ao detectar padrões de candlestick: {e}")
        
        return df
    
    def _detect_doji(self, df: pd.DataFrame) -> pd.Series:
        """Detectar padrão Doji"""
        body_size = abs(df['close'] - df['open'])
        range_size = df['high'] - df['low']
        return (body_size / range_size) < 0.1
    
    def _detect_hammer(self, df: pd.DataFrame) -> pd.Series:
        """Detectar padrão Hammer"""
        body_size = abs(df['close'] - df['open'])
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        
        return (lower_shadow > 2 * body_size) & (upper_shadow < body_size)
    
    def _detect_shooting_star(self, df: pd.DataFrame) -> pd.Series:
        """Detectar padrão Shooting Star"""
        body_size = abs(df['close'] - df['open'])
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        
        return (upper_shadow > 2 * body_size) & (lower_shadow < body_size)
    
    def _detect_bullish_engulfing(self, df: pd.DataFrame) -> pd.Series:
        """Detectar padrão Bullish Engulfing"""
        prev_bearish = df['close'].shift(1) < df['open'].shift(1)
        curr_bullish = df['close'] > df['open']
        engulfing = (df['open'] < df['close'].shift(1)) & (df['close'] > df['open'].shift(1))
        
        return prev_bearish & curr_bullish & engulfing
    
    def _detect_bearish_engulfing(self, df: pd.DataFrame) -> pd.Series:
        """Detectar padrão Bearish Engulfing"""
        prev_bullish = df['close'].shift(1) > df['open'].shift(1)
        curr_bearish = df['close'] < df['open']
        engulfing = (df['open'] > df['close'].shift(1)) & (df['close'] < df['open'].shift(1))
        
        return prev_bullish & curr_bearish & engulfing
    
    def _detect_morning_star(self, df: pd.DataFrame) -> pd.Series:
        """Detectar padrão Morning Star"""
        # Primeiro candle: bearish
        first_bearish = df['close'].shift(2) < df['open'].shift(2)
        
        # Segundo candle: pequeno corpo (doji ou spinning top)
        second_small = abs(df['close'].shift(1) - df['open'].shift(1)) < \
                      abs(df['close'].shift(2) - df['open'].shift(2)) * 0.3
        
        # Terceiro candle: bullish
        third_bullish = df['close'] > df['open']
        
        # Gap down e gap up
        gap_down = df['high'].shift(1) < df['low'].shift(2)
        gap_up = df['low'] > df['high'].shift(1)
        
        return first_bearish & second_small & third_bullish & gap_down & gap_up
    
    def _detect_evening_star(self, df: pd.DataFrame) -> pd.Series:
        """Detectar padrão Evening Star"""
        # Primeiro candle: bullish
        first_bullish = df['close'].shift(2) > df['open'].shift(2)
        
        # Segundo candle: pequeno corpo
        second_small = abs(df['close'].shift(1) - df['open'].shift(1)) < \
                      abs(df['close'].shift(2) - df['open'].shift(2)) * 0.3
        
        # Terceiro candle: bearish
        third_bearish = df['close'] < df['open']
        
        # Gap up e gap down
        gap_up = df['low'].shift(1) > df['high'].shift(2)
        gap_down = df['high'] < df['low'].shift(1)
        
        return first_bullish & second_small & third_bearish & gap_up & gap_down
    
    def get_signal_strength(self, df: pd.DataFrame) -> Dict:
        """Calcular força dos sinais baseado nos indicadores"""
        try:
            if df.empty or len(df) < 50:
                return {'strength': 0, 'direction': 'neutral', 'confidence': 0}
            
            latest = df.iloc[-1]
            signals = []
            
            # Sinais de RSI
            if latest['rsi'] < 30:
                signals.append(('buy', 0.8))
            elif latest['rsi'] > 70:
                signals.append(('sell', 0.8))
            
            # Sinais de MACD
            if latest['macd'] > latest['macd_signal'] and df.iloc[-2]['macd'] <= df.iloc[-2]['macd_signal']:
                signals.append(('buy', 0.7))
            elif latest['macd'] < latest['macd_signal'] and df.iloc[-2]['macd'] >= df.iloc[-2]['macd_signal']:
                signals.append(('sell', 0.7))
            
            # Sinais de Bollinger Bands
            if latest['close'] < latest['bb_lower']:
                signals.append(('buy', 0.6))
            elif latest['close'] > latest['bb_upper']:
                signals.append(('sell', 0.6))
            
            # Sinais de médias móveis
            if latest['ema_12'] > latest['ema_26'] and df.iloc[-2]['ema_12'] <= df.iloc[-2]['ema_26']:
                signals.append(('buy', 0.6))
            elif latest['ema_12'] < latest['ema_26'] and df.iloc[-2]['ema_12'] >= df.iloc[-2]['ema_26']:
                signals.append(('sell', 0.6))
            
            # Calcular força e direção
            buy_signals = [s[1] for s in signals if s[0] == 'buy']
            sell_signals = [s[1] for s in signals if s[0] == 'sell']
            
            buy_strength = sum(buy_signals)
            sell_strength = sum(sell_signals)
            
            if buy_strength > sell_strength:
                direction = 'buy'
                strength = buy_strength
            elif sell_strength > buy_strength:
                direction = 'sell'
                strength = sell_strength
            else:
                direction = 'neutral'
                strength = 0
            
            confidence = min(strength / 3.0, 1.0)  # Normalizar para 0-1
            
            return {
                'strength': strength,
                'direction': direction,
                'confidence': confidence,
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular força do sinal: {e}")
            return {'strength': 0, 'direction': 'neutral', 'confidence': 0}
    
    def analyze_multi_timeframe(self, symbol: str, base_timeframe: str = '1h') -> Dict:
        """
        Análise multi-timeframe para confirmar sinais
        Verifica alinhamento de tendência em múltiplos timeframes
        """
        try:
            from .market_data import MarketDataManager
            
            # Definir timeframes baseado no timeframe principal
            if base_timeframe == '5m':
                timeframes = ['5m', '15m', '1h']
            elif base_timeframe == '15m':
                timeframes = ['15m', '1h', '4h']
            elif base_timeframe == '1h':
                timeframes = ['1h', '4h', '1d']
            elif base_timeframe == '4h':
                timeframes = ['4h', '1d', '1w']
            else:
                timeframes = ['1h', '4h', '1d']  # Default
            
            market_data = MarketDataManager(self.config)
            signals = {}
            scores = {}
            
            for tf in timeframes:
                try:
                    # Obter dados para o timeframe
                    df = market_data.get_historical_data(symbol, tf, 200)
                    if df is None or df.empty:
                        continue
                    
                    # Calcular indicadores
                    df = self.calculate_all_indicators(df)
                    
                    # Analisar tendência
                    trend_score = self._analyze_trend_strength(df)
                    signals[tf] = trend_score
                    
                    # Peso baseado no timeframe (maior timeframe = maior peso)
                    weight = {'5m': 1, '15m': 2, '1h': 3, '4h': 4, '1d': 5, '1w': 6}.get(tf, 3)
                    scores[tf] = trend_score * weight
                    
                    logger.info(f"Multi-TF {symbol} {tf}: score={trend_score:.3f}, weight={weight}")
                    
                except Exception as e:
                    logger.warning(f"Erro no timeframe {tf}: {e}")
                    continue
            
            if not signals:
                return {'alignment': 'neutral', 'strength': 0.5, 'signals': {}}
            
            # Calcular alinhamento
            total_score = sum(scores.values())
            total_weight = sum([{'5m': 1, '15m': 2, '1h': 3, '4h': 4, '1d': 5, '1w': 6}.get(tf, 3) 
                               for tf in signals.keys()])
            
            average_score = total_score / total_weight if total_weight > 0 else 0.5
            
            # Determinar alinhamento
            if average_score > 0.65:
                alignment = 'bullish'
            elif average_score < 0.35:
                alignment = 'bearish'
            else:
                alignment = 'neutral'
            
            # Calcular força do alinhamento
            alignment_strength = abs(average_score - 0.5) * 2  # 0-1
            
            result = {
                'alignment': alignment,
                'strength': alignment_strength,
                'average_score': average_score,
                'signals': signals,
                'weighted_scores': scores,
                'timeframes_analyzed': list(signals.keys())
            }
            
            logger.info(f"Multi-TF {symbol}: {alignment} (força: {alignment_strength:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise multi-timeframe: {e}")
            return {'alignment': 'neutral', 'strength': 0.5, 'signals': {}}
    
    def _analyze_trend_strength(self, df: pd.DataFrame) -> float:
        """
        Analisa a força da tendência em um DataFrame
        Retorna: 0.0 (bearish forte) a 1.0 (bullish forte)
        """
        try:
            if df.empty or len(df) < 20:
                return 0.5
            
            latest = df.iloc[-1]
            prev_20 = df.iloc[-20]
            
            signals = []
            
            # 1. Preço vs EMAs
            if 'ema_20' in df.columns and 'ema_50' in df.columns:
                if latest['close'] > latest['ema_20'] > latest['ema_50']:
                    signals.append(1.0)  # Bullish
                elif latest['close'] < latest['ema_20'] < latest['ema_50']:
                    signals.append(0.0)  # Bearish
                else:
                    signals.append(0.5)  # Neutral
            
            # 2. Momentum (RSI)
            if 'rsi' in df.columns:
                rsi = latest['rsi']
                if rsi > 60:
                    signals.append(0.8)
                elif rsi > 50:
                    signals.append(0.6)
                elif rsi < 40:
                    signals.append(0.2)
                elif rsi < 50:
                    signals.append(0.4)
                else:
                    signals.append(0.5)
            
            # 3. MACD
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                if latest['macd'] > latest['macd_signal']:
                    signals.append(0.7)
                else:
                    signals.append(0.3)
            
            # 4. Direção do preço (20 períodos)
            price_change = (latest['close'] - prev_20['close']) / prev_20['close']
            if price_change > 0.05:  # +5%
                signals.append(0.9)
            elif price_change > 0:
                signals.append(0.6)
            elif price_change < -0.05:  # -5%
                signals.append(0.1)
            else:
                signals.append(0.4)
            
            # Média ponderada
            return sum(signals) / len(signals) if signals else 0.5
            
        except Exception as e:
            logger.error(f"Erro ao analisar força da tendência: {e}")
            return 0.5
    
    def _add_advanced_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        MELHORIA 2: Adicionar indicadores avançados de volume para melhor análise
        """
        try:
            # 1. Volume Profile básico (simulado através de clustering)
            df['volume_profile_score'] = self._calculate_volume_profile_score(df)
            
            # 2. On-Balance Volume (OBV) melhorado com sinais
            if 'obv' in df.columns:
                df['obv_signal'] = self._analyze_obv_signals(df)
            
            # 3. Volume Rate of Change
            df['volume_roc'] = df['volume'].pct_change(periods=10) * 100
            
            # 4. Price Volume Trend melhorado
            if 'vpt' in df.columns:
                df['vpt_signal'] = self._analyze_vpt_signals(df)
            
            # 5. Volume Weighted Moving Average
            df['vwma_10'] = self._calculate_vwma(df, 10)
            df['vwma_20'] = self._calculate_vwma(df, 20)
            
            # 6. Volume Breakout Detection
            df['volume_breakout'] = self._detect_volume_breakouts(df)
            
            # 7. Money Flow Quality
            df['money_flow_quality'] = self._calculate_money_flow_quality(df)
            
            # 8. Volume Divergence com preço
            df['volume_price_divergence'] = self._detect_volume_price_divergence(df)
            
            logger.info("✅ Indicadores avançados de volume calculados")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao calcular indicadores avançados de volume: {e}")
            return df
    
    def _calculate_volume_profile_score(self, df: pd.DataFrame) -> pd.Series:
        """Calcular score do volume profile (versão simplificada)"""
        try:
            # Usar rolling window para calcular concentração de volume
            window = 20
            volume_avg = df['volume'].rolling(window=window).mean()
            volume_std = df['volume'].rolling(window=window).std()
            
            # Score baseado em desvios padrão
            volume_score = (df['volume'] - volume_avg) / (volume_std + 1e-8)
            
            # Normalizar entre 0 e 1
            return (volume_score + 3) / 6  # Assumindo que raramente passa de 3 std
            
        except Exception:
            return pd.Series(0.5, index=df.index)
    
    def _analyze_obv_signals(self, df: pd.DataFrame) -> pd.Series:
        """Analisar sinais do On-Balance Volume"""
        try:
            obv = df['obv']
            obv_ma = obv.rolling(window=14).mean()
            
            # Sinal baseado na direção do OBV vs sua média
            signals = pd.Series(0.5, index=df.index)  # Neutro por padrão
            
            # OBV acima da média e subindo = bullish
            bullish = (obv > obv_ma) & (obv > obv.shift(1))
            signals.loc[bullish] = 0.8
            
            # OBV abaixo da média e descendo = bearish
            bearish = (obv < obv_ma) & (obv < obv.shift(1))
            signals.loc[bearish] = 0.2
            
            return signals
            
        except Exception:
            return pd.Series(0.5, index=df.index)
    
    def _analyze_vpt_signals(self, df: pd.DataFrame) -> pd.Series:
        """Analisar sinais do Volume Price Trend"""
        try:
            vpt = df['vpt']
            vpt_ma = vpt.rolling(window=14).mean()
            
            signals = pd.Series(0.5, index=df.index)
            
            # VPT subindo = bullish
            bullish = vpt > vpt.shift(1)
            signals.loc[bullish] = 0.7
            
            # VPT descendo = bearish
            bearish = vpt < vpt.shift(1)
            signals.loc[bearish] = 0.3
            
            return signals
            
        except Exception:
            return pd.Series(0.5, index=df.index)
    
    def _calculate_vwma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calcular Volume Weighted Moving Average"""
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwma = (typical_price * df['volume']).rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
            return vwma
        except Exception:
            return df['close']
    
    def _detect_volume_breakouts(self, df: pd.DataFrame) -> pd.Series:
        """Detectar breakouts de volume"""
        try:
            volume_avg = df['volume'].rolling(window=20).mean()
            volume_threshold = volume_avg * 1.5  # 50% acima da média
            
            breakouts = pd.Series(0, index=df.index)
            breakouts.loc[df['volume'] > volume_threshold] = 1
            
            return breakouts
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _calculate_money_flow_quality(self, df: pd.DataFrame) -> pd.Series:
        """Calcular qualidade do fluxo de dinheiro"""
        try:
            # Combinar MFI com volume
            if 'mfi' in df.columns:
                mfi = df['mfi']
                volume_ratio = df['volume'] / df['volume'].rolling(window=14).mean()
                
                # Qualidade alta quando MFI e volume estão alinhados
                quality = (mfi / 100) * np.minimum(volume_ratio, 2.0) / 2.0
                return quality
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception:
            return pd.Series(0.5, index=df.index)
    
    def _detect_volume_price_divergence(self, df: pd.DataFrame) -> pd.Series:
        """Detectar divergências entre volume e preço"""
        try:
            price_trend = df['close'].pct_change(periods=5)
            volume_trend = df['volume'].pct_change(periods=5)
            
            # Divergência quando preço e volume movem em direções opostas
            divergence = pd.Series(0, index=df.index)
            
            # Divergência bearish: preço sobe, volume cai
            bearish_div = (price_trend > 0.02) & (volume_trend < -0.1)
            divergence.loc[bearish_div] = -1
            
            # Divergência bullish: preço cai, volume sobe
            bullish_div = (price_trend < -0.02) & (volume_trend > 0.1)
            divergence.loc[bullish_div] = 1
            
            return divergence
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _add_advanced_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        MELHORIA 3: Padrões de Candlestick Automáticos Avançados
        Detecta padrões complexos com alta precisão
        """
        try:
            # === PADRÕES BULLISH (ALTA) ===
            
            # 1. Hammer (Martelo)
            df['hammer_advanced'] = self._detect_hammer_advanced(df)
            
            # 2. Morning Star (Estrela da Manhã)
            df['morning_star_advanced'] = self._detect_morning_star_advanced(df)
            
            # 3. Bullish Engulfing (Engolfo de Alta)
            df['bullish_engulfing_advanced'] = self._detect_bullish_engulfing_advanced(df)
            
            # 4. Piercing Pattern (Padrão Perfurante)
            df['piercing_pattern'] = self._detect_piercing_pattern(df)
            
            # 5. Three White Soldiers (Três Soldados Brancos)
            df['three_white_soldiers'] = self._detect_three_white_soldiers(df)
            
            # 6. Inverted Hammer (Martelo Invertido)
            df['inverted_hammer'] = self._detect_inverted_hammer(df)
            
            # === PADRÕES BEARISH (BAIXA) ===
            
            # 7. Shooting Star (Estrela Cadente)
            df['shooting_star_advanced'] = self._detect_shooting_star_advanced(df)
            
            # 8. Evening Star (Estrela da Tarde)
            df['evening_star_advanced'] = self._detect_evening_star_advanced(df)
            
            # 9. Bearish Engulfing (Engolfo de Baixa)
            df['bearish_engulfing_advanced'] = self._detect_bearish_engulfing_advanced(df)
            
            # 10. Dark Cloud Cover (Cobertura de Nuvem Escura)
            df['dark_cloud_cover'] = self._detect_dark_cloud_cover(df)
            
            # 11. Three Black Crows (Três Corvos Pretos)
            df['three_black_crows'] = self._detect_three_black_crows(df)
            
            # 12. Hanging Man (Homem Enforcado)
            df['hanging_man'] = self._detect_hanging_man(df)
            
            # === PADRÕES DE REVERSÃO/INDECISÃO ===
            
            # 13. Doji Avançado
            df['doji_advanced'] = self._detect_doji_advanced(df)
            
            # 14. Spinning Top (Pião)
            df['spinning_top'] = self._detect_spinning_top(df)
            
            # 15. Long-Legged Doji (Doji de Pernas Longas)
            df['long_legged_doji'] = self._detect_long_legged_doji(df)
            
            # === SCORES CONSOLIDADOS ===
            
            # Score geral de padrões bullish
            df['bullish_patterns_score'] = self._calculate_bullish_patterns_score(df)
            
            # Score geral de padrões bearish
            df['bearish_patterns_score'] = self._calculate_bearish_patterns_score(df)
            
            # Score de indecisão/reversão
            df['reversal_patterns_score'] = self._calculate_reversal_patterns_score(df)
            
            logger.info("✅ Padrões avançados de candlestick calculados")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao calcular padrões avançados de candlestick: {e}")
            return df    
    # === MÉTODOS DE DETECÇÃO AVANÇADOS ===
    
    def _detect_hammer_advanced(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Hammer com critérios mais flexíveis"""
        try:
            signals = pd.Series(0, index=df.index)
            
            for i in range(1, len(df)):
                high = df.iloc[i]['high']
                low = df.iloc[i]['low']
                open_price = df.iloc[i]['open']
                close = df.iloc[i]['close']
                
                # Corpo do candle
                body = abs(close - open_price)
                # Sombra inferior
                lower_shadow = min(open_price, close) - low
                # Sombra superior
                upper_shadow = high - max(open_price, close)
                # Range total
                total_range = high - low
                
                if total_range > 0 and body > 0:
                    # Critérios flexíveis para Hammer:
                    # 1. Sombra inferior >= 1.5x o corpo
                    # 2. Sombra superior <= corpo
                    # 3. Corpo pequeno em relação ao range
                    
                    condition1 = lower_shadow >= (body * 1.5)
                    condition2 = upper_shadow <= body
                    condition3 = body <= (total_range * 0.4)  # Corpo pequeno
                    
                    if condition1 and condition2 and condition3:
                        signals.iloc[i] = 1
            
            return signals
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_morning_star_advanced(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Morning Star (padrão de 3 candles)"""
        try:
            signals = pd.Series(0, index=df.index)
            
            for i in range(2, len(df)):
                # Três candles: primeiro (i-2), segundo (i-1), terceiro (i)
                candle1 = df.iloc[i-2]  # Primeiro: bearish
                candle2 = df.iloc[i-1]  # Segundo: pequeno corpo (star)
                candle3 = df.iloc[i]    # Terceiro: bullish
                
                # Corpos dos candles
                body1 = abs(candle1['close'] - candle1['open'])
                body2 = abs(candle2['close'] - candle2['open'])
                body3 = abs(candle3['close'] - candle3['open'])
                
                # Critérios para Morning Star:
                # 1. Primeiro candle: bearish forte
                # 2. Segundo candle: corpo pequeno (gap down)
                # 3. Terceiro candle: bullish forte (gap up)
                
                condition1 = candle1['close'] < candle1['open']  # Bearish
                condition2 = body1 > body2 * 3  # Primeiro corpo >> segundo corpo
                condition3 = candle2['high'] < candle1['low']  # Gap down
                condition4 = candle3['close'] > candle3['open']  # Bullish
                condition5 = candle3['open'] > candle2['high']  # Gap up
                condition6 = candle3['close'] > (candle1['open'] + candle1['close']) / 2  # Recuperação significativa
                
                if condition1 and condition2 and condition3 and condition4 and condition5 and condition6:
                    signals.iloc[i] = 1
            
            return signals
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_shooting_star_advanced(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Shooting Star (martelo invertido bearish)"""
        try:
            signals = pd.Series(0, index=df.index)
            
            for i in range(1, len(df)):
                high = df.iloc[i]['high']
                low = df.iloc[i]['low']
                open_price = df.iloc[i]['open']
                close = df.iloc[i]['close']
                
                # Corpo do candle
                body = abs(close - open_price)
                # Sombra superior
                upper_shadow = high - max(open_price, close)
                # Sombra inferior
                lower_shadow = min(open_price, close) - low
                # Range total
                total_range = high - low
                
                if total_range > 0 and body > 0:
                    # Critérios para Shooting Star:
                    # 1. Sombra superior >= 1.5x o corpo
                    # 2. Sombra inferior <= corpo
                    # 3. Corpo pequeno em relação ao range
                    
                    condition1 = upper_shadow >= (body * 1.5)
                    condition2 = lower_shadow <= body
                    condition3 = body <= (total_range * 0.4)
                    
                    if condition1 and condition2 and condition3:
                        signals.iloc[i] = 1
            
            return signals
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_doji_advanced(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Doji (indecisão)"""
        try:
            signals = pd.Series(0, index=df.index)
            
            for i in range(len(df)):
                high = df.iloc[i]['high']
                low = df.iloc[i]['low']
                open_price = df.iloc[i]['open']
                close = df.iloc[i]['close']
                
                # Range total
                total_range = high - low
                # Corpo do candle
                body = abs(close - open_price)
                
                if total_range > 0:
                    # Doji: corpo muito pequeno em relação ao range
                    body_ratio = body / total_range
                    
                    if body_ratio <= 0.1:  # Corpo <= 10% do range total
                        signals.iloc[i] = 1
            
            return signals
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_bullish_engulfing_advanced(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Bullish Engulfing simplificado"""
        try:
            signals = pd.Series(0, index=df.index)
            
            for i in range(1, len(df)):
                prev_candle = df.iloc[i-1]
                curr_candle = df.iloc[i]
                
                # Candle anterior bearish, atual bullish
                prev_bearish = prev_candle['close'] < prev_candle['open']
                curr_bullish = curr_candle['close'] > curr_candle['open']
                
                # Corpo atual maior que o anterior
                prev_body = abs(prev_candle['close'] - prev_candle['open'])
                curr_body = abs(curr_candle['close'] - curr_candle['open'])
                bigger_body = curr_body > prev_body * 1.1
                
                # Fechamento atual acima da abertura anterior
                closes_above = curr_candle['close'] > prev_candle['open']
                
                if prev_bearish and curr_bullish and bigger_body and closes_above:
                    signals.iloc[i] = 1
            
            return signals
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_bearish_engulfing_advanced(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Bearish Engulfing simplificado"""
        try:
            signals = pd.Series(0, index=df.index)
            
            for i in range(1, len(df)):
                prev_candle = df.iloc[i-1]
                curr_candle = df.iloc[i]
                
                # Candle anterior bullish, atual bearish
                prev_bullish = prev_candle['close'] > prev_candle['open']
                curr_bearish = curr_candle['close'] < curr_candle['open']
                
                # Corpo atual maior que o anterior
                prev_body = abs(prev_candle['close'] - prev_candle['open'])
                curr_body = abs(curr_candle['close'] - curr_candle['open'])
                bigger_body = curr_body > prev_body * 1.1
                
                # Fechamento atual abaixo da abertura anterior
                closes_below = curr_candle['close'] < prev_candle['open']
                
                if prev_bullish and curr_bearish and bigger_body and closes_below:
                    signals.iloc[i] = 1
            
            return signals
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_evening_star_advanced(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Evening Star simplificado"""
        try:
            signals = pd.Series(0, index=df.index)
            return signals  # Implementação simplificada por ora
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_piercing_pattern(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Piercing Pattern simplificado"""
        try:
            signals = pd.Series(0, index=df.index)
            return signals  # Implementação simplificada por ora
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_three_white_soldiers(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Three White Soldiers simplificado"""
        try:
            signals = pd.Series(0, index=df.index)
            return signals  # Implementação simplificada por ora
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_inverted_hammer(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Inverted Hammer (igual ao shooting star mas bullish)"""
        try:
            signals = pd.Series(0, index=df.index)
            return signals  # Implementação simplificada por ora
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_dark_cloud_cover(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Dark Cloud Cover simplificado"""
        try:
            signals = pd.Series(0, index=df.index)
            return signals  # Implementação simplificada por ora
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_three_black_crows(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Three Black Crows simplificado"""
        try:
            signals = pd.Series(0, index=df.index)
            return signals  # Implementação simplificada por ora
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_hanging_man(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Hanging Man simplificado"""
        try:
            signals = pd.Series(0, index=df.index)
            return signals  # Implementação simplificada por ora
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_spinning_top(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Spinning Top (corpo pequeno, sombras grandes)"""
        try:
            signals = pd.Series(0, index=df.index)
            
            for i in range(len(df)):
                high = df.iloc[i]['high']
                low = df.iloc[i]['low']
                open_price = df.iloc[i]['open']
                close = df.iloc[i]['close']
                
                # Corpo e sombras
                body = abs(close - open_price)
                upper_shadow = high - max(open_price, close)
                lower_shadow = min(open_price, close) - low
                total_range = high - low
                
                if total_range > 0 and body > 0:
                    # Spinning Top: corpo pequeno, sombras grandes
                    body_ratio = body / total_range
                    min_shadow = min(upper_shadow, lower_shadow)
                    
                    if body_ratio <= 0.3 and min_shadow >= body:
                        signals.iloc[i] = 1
            
            return signals
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _detect_long_legged_doji(self, df: pd.DataFrame) -> pd.Series:
        """Detectar Long-Legged Doji"""
        try:
            signals = pd.Series(0, index=df.index)
            
            for i in range(len(df)):
                high = df.iloc[i]['high']
                low = df.iloc[i]['low']
                open_price = df.iloc[i]['open']
                close = df.iloc[i]['close']
                
                # Corpo e sombras
                body = abs(close - open_price)
                upper_shadow = high - max(open_price, close)
                lower_shadow = min(open_price, close) - low
                total_range = high - low
                
                if total_range > 0:
                    # Long-Legged Doji: corpo minúsculo, sombras muito longas
                    body_ratio = body / total_range
                    min_shadow_ratio = min(upper_shadow, lower_shadow) / total_range
                    
                    if body_ratio <= 0.05 and min_shadow_ratio >= 0.3:
                        signals.iloc[i] = 1
            
            return signals
            
        except Exception:
            return pd.Series(0, index=df.index)
    
    def _calculate_bullish_patterns_score(self, df: pd.DataFrame) -> pd.Series:
        """Calcular score consolidado de padrões bullish"""
        try:
            bullish_columns = [
                'hammer_advanced', 'morning_star_advanced', 'bullish_engulfing_advanced',
                'piercing_pattern', 'three_white_soldiers', 'inverted_hammer'
            ]
            
            score = pd.Series(0.0, index=df.index)
            weights = {'hammer_advanced': 0.3, 'morning_star_advanced': 0.25, 
                      'bullish_engulfing_advanced': 0.3, 'piercing_pattern': 0.05,
                      'three_white_soldiers': 0.05, 'inverted_hammer': 0.05}
            
            for col in bullish_columns:
                if col in df.columns:
                    score += df[col] * weights.get(col, 0.1)
            
            return score
            
        except Exception:
            return pd.Series(0.0, index=df.index)

    def _calculate_bearish_patterns_score(self, df: pd.DataFrame) -> pd.Series:
        """Calcular score consolidado de padrões bearish"""
        try:
            bearish_columns = [
                'shooting_star_advanced', 'evening_star_advanced', 'bearish_engulfing_advanced',
                'dark_cloud_cover', 'three_black_crows', 'hanging_man'
            ]
            
            score = pd.Series(0.0, index=df.index)
            weights = {'shooting_star_advanced': 0.3, 'evening_star_advanced': 0.25,
                      'bearish_engulfing_advanced': 0.3, 'dark_cloud_cover': 0.05,
                      'three_black_crows': 0.05, 'hanging_man': 0.05}
            
            for col in bearish_columns:
                if col in df.columns:
                    score += df[col] * weights.get(col, 0.1)
            
            return score
            
        except Exception:
            return pd.Series(0.0, index=df.index)
    
    def _calculate_reversal_patterns_score(self, df: pd.DataFrame) -> pd.Series:
        """Calcular score de padrões de reversão/indecisão"""
        try:
            reversal_columns = ['doji_advanced', 'spinning_top', 'long_legged_doji']
            
            score = pd.Series(0.0, index=df.index)
            weights = {'doji_advanced': 0.4, 'spinning_top': 0.3, 'long_legged_doji': 0.3}
            
            for col in reversal_columns:
                if col in df.columns:
                    score += df[col] * weights.get(col, 0.33)
            
            return score
            
        except Exception:
            return pd.Series(0.0, index=df.index)
    
    def _add_market_sentiment_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """MELHORIA 5: Adicionar indicadores de sentimento de mercado"""
        try:
            from .market_sentiment import MarketSentimentAnalyzer
            
            sentiment_analyzer = MarketSentimentAnalyzer()
            df = sentiment_analyzer.calculate_market_sentiment(df)
            
            logger.info("✅ Indicadores de sentimento de mercado calculados")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao calcular sentimento de mercado: {e}")
            return df
