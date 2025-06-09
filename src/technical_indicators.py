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
            
            # Indicadores de tendência
            df = self._add_trend_indicators(df)
            
            # Padrões de candlestick
            df = self._add_candlestick_patterns(df)
            
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
        
        # Aroon
        df['aroon_up'] = ta.trend.aroon_up(df['high'], df['low'], window=25)
        df['aroon_down'] = ta.trend.aroon_down(df['high'], df['low'], window=25)
        df['aroon_indicator'] = df['aroon_up'] - df['aroon_down']
        
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