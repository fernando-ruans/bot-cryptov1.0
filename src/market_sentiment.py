#!/usr/bin/env python3
"""
MELHORIA 5: Análise de Sentimento de Mercado
Implementa indicadores de sentimento baseados em dados de mercado
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MarketSentimentAnalyzer:
    """Analisador de sentimento de mercado baseado em dados técnicos"""
    
    def __init__(self):
        self.sentiment_cache = {}
        self.fear_greed_cache = {}
        
    def calculate_market_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular todos os indicadores de sentimento"""
        try:
            logger.info("🧠 Calculando indicadores de sentimento de mercado...")
            
            # 1. Fear & Greed Index baseado em indicadores técnicos
            df = self._calculate_fear_greed_index(df)
            
            # 2. Sentiment baseado em volume
            df = self._calculate_volume_sentiment(df)
            
            # 3. Sentiment baseado em volatilidade
            df = self._calculate_volatility_sentiment(df)
            
            # 4. Sentiment baseado em momentum
            df = self._calculate_momentum_sentiment(df)
            
            # 5. Sentiment de breakout/breakdown
            df = self._calculate_breakout_sentiment(df)
            
            # 6. Sentiment de divergências
            df = self._calculate_divergence_sentiment(df)
            
            # 7. Sentiment de força relativa
            df = self._calculate_relative_strength_sentiment(df)
            
            # 8. Score consolidado de sentimento
            df = self._calculate_overall_sentiment(df)
            
            logger.info("✅ Indicadores de sentimento calculados")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao calcular sentimento: {e}")
            return df
    
    def _calculate_fear_greed_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular Fear & Greed Index baseado em múltiplos fatores"""
        try:
            # Componentes do Fear & Greed Index
            
            # 1. Momentum (25% do peso)
            rsi = df.get('rsi', pd.Series(50, index=df.index))
            momentum_score = (rsi - 50) / 50  # Normalizar entre -1 e 1
            
            # 2. Volatilidade (25% do peso)
            if 'close' in df.columns:
                returns = df['close'].pct_change()
                volatility_20 = returns.rolling(20).std()
                volatility_50 = returns.rolling(50).std()
                vol_ratio = volatility_20 / (volatility_50 + 0.001)
                volatility_score = np.clip(1 - vol_ratio, -1, 1)  # Baixa vol = greed, alta vol = fear
            else:
                volatility_score = pd.Series(0, index=df.index)
            
            # 3. Volume (15% do peso)
            if 'volume' in df.columns:
                volume_sma_20 = df['volume'].rolling(20).mean()
                volume_ratio = df['volume'] / (volume_sma_20 + 1)
                volume_score = np.clip((volume_ratio - 1) * 2, -1, 1)
            else:
                volume_score = pd.Series(0, index=df.index)
            
            # 4. Relative Strength (20% do peso)
            if 'close' in df.columns:
                high_20 = df['high'].rolling(20).max()
                low_20 = df['low'].rolling(20).min()
                rs_position = (df['close'] - low_20) / (high_20 - low_20 + 0.001)
                rs_score = (rs_position - 0.5) * 2  # Normalizar entre -1 e 1
            else:
                rs_score = pd.Series(0, index=df.index)
            
            # 5. Trend Strength (15% do peso)
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                trend_score = np.where(df['sma_20'] > df['sma_50'], 1, -1)
                trend_score = pd.Series(trend_score, index=df.index)
            else:
                trend_score = pd.Series(0, index=df.index)
            
            # Calcular Fear & Greed Index (0-100)
            fg_index = (
                momentum_score * 0.25 +
                volatility_score * 0.25 +
                volume_score * 0.15 +
                rs_score * 0.20 +
                trend_score * 0.15
            )
            
            # Converter para escala 0-100
            df['fear_greed_index'] = ((fg_index + 1) * 50).clip(0, 100)
            
            # Classificações
            df['fear_greed_label'] = pd.cut(
                df['fear_greed_index'],
                bins=[0, 25, 45, 55, 75, 100],
                labels=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
            ).astype(str)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no Fear & Greed Index: {e}")
            df['fear_greed_index'] = 50
            df['fear_greed_label'] = 'Neutral'
            return df
    
    def _calculate_volume_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sentiment baseado em análise de volume"""
        try:
            if 'volume' not in df.columns:
                df['volume_sentiment'] = 0
                return df
            
            # Volume trending
            volume_sma_10 = df['volume'].rolling(10).mean()
            volume_sma_30 = df['volume'].rolling(30).mean()
            volume_trend = (volume_sma_10 / (volume_sma_30 + 1) - 1)
            
            # Volume spikes
            volume_mean = df['volume'].rolling(20).mean()
            volume_std = df['volume'].rolling(20).std()
            volume_spikes = (df['volume'] - volume_mean) / (volume_std + 1)
            
            # On Balance Volume trend
            if 'close' in df.columns:
                price_change = df['close'].diff()
                obv_direction = np.where(price_change > 0, 1, np.where(price_change < 0, -1, 0))
                obv = (df['volume'] * obv_direction).cumsum()
                obv_trend = obv.diff(10) / (obv.rolling(10).std() + 1)
            else:
                obv_trend = pd.Series(0, index=df.index)
            
            # Combinar indicadores de volume
            df['volume_sentiment'] = (
                np.tanh(volume_trend) * 0.4 +
                np.tanh(volume_spikes) * 0.3 +
                np.tanh(obv_trend) * 0.3
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no volume sentiment: {e}")
            df['volume_sentiment'] = 0
            return df
    
    def _calculate_volatility_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sentiment baseado em volatilidade"""
        try:
            if 'close' not in df.columns:
                df['volatility_sentiment'] = 0
                return df
            
            # Volatilidade realizada
            returns = df['close'].pct_change()
            vol_5 = returns.rolling(5).std()
            vol_20 = returns.rolling(20).std()
            vol_ratio = vol_5 / (vol_20 + 0.001)
            
            # VIX-like indicator (volatilidade implícita simulada)
            atr = df.get('atr', pd.Series(0, index=df.index))
            atr_normalized = atr / df['close'] * 100
            atr_percentile = atr_normalized.rolling(50).rank(pct=True)
            
            # Volatility clustering
            vol_cluster = vol_5.rolling(10).std()
            vol_cluster_norm = vol_cluster / (vol_cluster.rolling(50).mean() + 0.001)
            
            # Sentiment: baixa volatilidade = greed, alta volatilidade = fear
            vol_sentiment = (
                (1 - np.tanh(vol_ratio - 1)) * 0.4 +
                (1 - (atr_percentile - 0.5) * 2) * 0.3 +
                (1 - np.tanh(vol_cluster_norm - 1)) * 0.3
            )
            
            df['volatility_sentiment'] = vol_sentiment.clip(-1, 1)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no volatility sentiment: {e}")
            df['volatility_sentiment'] = 0
            return df
    
    def _calculate_momentum_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sentiment baseado em momentum"""
        try:
            momentum_indicators = []
            
            # RSI sentiment
            if 'rsi' in df.columns:
                rsi_sentiment = (df['rsi'] - 50) / 50
                momentum_indicators.append(rsi_sentiment * 0.3)
            
            # MACD sentiment
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                macd_sentiment = np.tanh((df['macd'] - df['macd_signal']) * 10)
                momentum_indicators.append(macd_sentiment * 0.25)
            
            # Stochastic sentiment
            if 'stoch_k' in df.columns:
                stoch_sentiment = (df['stoch_k'] - 50) / 50
                momentum_indicators.append(stoch_sentiment * 0.2)
            
            # Price momentum
            if 'close' in df.columns:
                price_mom_5 = df['close'].pct_change(5)
                price_mom_20 = df['close'].pct_change(20)
                price_sentiment = np.tanh(price_mom_5 * 100) * 0.15 + np.tanh(price_mom_20 * 50) * 0.1
                momentum_indicators.append(price_sentiment)
            
            # Combinar todos os momentums
            if momentum_indicators:
                df['momentum_sentiment'] = sum(momentum_indicators)
            else:
                df['momentum_sentiment'] = 0
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no momentum sentiment: {e}")
            df['momentum_sentiment'] = 0
            return df
    
    def _calculate_breakout_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sentiment baseado em breakouts/breakdowns"""
        try:
            if 'close' not in df.columns:
                df['breakout_sentiment'] = 0
                return df
            
            # Resistance/Support breakouts
            high_20 = df['high'].rolling(20).max()
            low_20 = df['low'].rolling(20).min()
            
            breakout_up = (df['close'] > high_20.shift(1)).astype(int)
            breakdown = (df['close'] < low_20.shift(1)).astype(int)
            
            # Bollinger Bands breakouts
            if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
                bb_breakout_up = (df['close'] > df['bb_upper']).astype(int)
                bb_breakdown = (df['close'] < df['bb_lower']).astype(int)
            else:
                bb_breakout_up = pd.Series(0, index=df.index)
                bb_breakdown = pd.Series(0, index=df.index)
            
            # Volume confirmation
            if 'volume' in df.columns:
                volume_conf = df['volume'] / df['volume'].rolling(20).mean()
                volume_conf = np.clip(volume_conf - 1, 0, 2)
            else:
                volume_conf = pd.Series(1, index=df.index)
            
            # Combinar breakouts
            breakout_sentiment = (
                (breakout_up - breakdown) * volume_conf * 0.6 +
                (bb_breakout_up - bb_breakdown) * volume_conf * 0.4
            )
            
            # Suavizar com média móvel
            df['breakout_sentiment'] = breakout_sentiment.rolling(3).mean().fillna(0)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no breakout sentiment: {e}")
            df['breakout_sentiment'] = 0
            return df
    
    def _calculate_divergence_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sentiment baseado em divergências"""
        try:
            divergence_signals = []
            
            if 'close' in df.columns and 'rsi' in df.columns:
                # Price vs RSI divergence
                price_trend = df['close'].rolling(10).apply(
                    lambda x: 1 if x.iloc[-1] > x.iloc[0] else -1, raw=False
                )
                rsi_trend = df['rsi'].rolling(10).apply(
                    lambda x: 1 if x.iloc[-1] > x.iloc[0] else -1, raw=False
                )
                
                price_rsi_div = (price_trend != rsi_trend).astype(int) * np.sign(price_trend)
                divergence_signals.append(price_rsi_div * 0.5)
            
            if 'close' in df.columns and 'macd' in df.columns:
                # Price vs MACD divergence
                price_trend = df['close'].rolling(10).apply(
                    lambda x: 1 if x.iloc[-1] > x.iloc[0] else -1, raw=False
                )
                macd_trend = df['macd'].rolling(10).apply(
                    lambda x: 1 if x.iloc[-1] > x.iloc[0] else -1, raw=False
                )
                
                price_macd_div = (price_trend != macd_trend).astype(int) * np.sign(price_trend)
                divergence_signals.append(price_macd_div * 0.5)
            
            # Combinar divergências
            if divergence_signals:
                df['divergence_sentiment'] = sum(divergence_signals)
            else:
                df['divergence_sentiment'] = 0
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no divergence sentiment: {e}")
            df['divergence_sentiment'] = 0
            return df
    
    def _calculate_relative_strength_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sentiment baseado em força relativa"""
        try:
            if 'close' not in df.columns:
                df['relative_strength_sentiment'] = 0
                return df
            
            # Position in recent range
            high_50 = df['high'].rolling(50).max()
            low_50 = df['low'].rolling(50).min()
            range_position = (df['close'] - low_50) / (high_50 - low_50 + 0.001)
            
            # Relative performance vs moving averages
            sma_signals = []
            for period in [20, 50, 200]:
                if f'sma_{period}' in df.columns:
                    sma_ratio = df['close'] / df[f'sma_{period}'] - 1
                    sma_signals.append(np.tanh(sma_ratio * 10))
            
            # Price momentum strength
            returns_5 = df['close'].pct_change(5)
            returns_20 = df['close'].pct_change(20)
            momentum_strength = np.tanh(returns_5 * 50) * 0.6 + np.tanh(returns_20 * 20) * 0.4
            
            # Combinar indicadores de força
            relative_strength = (
                (range_position - 0.5) * 2 * 0.4 +
                (sum(sma_signals) / len(sma_signals) if sma_signals else 0) * 0.3 +
                momentum_strength * 0.3
            )
            
            df['relative_strength_sentiment'] = relative_strength.clip(-1, 1)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no relative strength sentiment: {e}")
            df['relative_strength_sentiment'] = 0
            return df
    
    def _calculate_overall_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular score consolidado de sentimento"""
        try:
            # Componentes do sentimento
            sentiment_components = {
                'fear_greed_index': 0.25,
                'volume_sentiment': 0.15,
                'volatility_sentiment': 0.15,
                'momentum_sentiment': 0.20,
                'breakout_sentiment': 0.10,
                'divergence_sentiment': 0.05,
                'relative_strength_sentiment': 0.10
            }
            
            # Calcular score ponderado
            overall_sentiment = pd.Series(0, index=df.index)
            
            for component, weight in sentiment_components.items():
                if component in df.columns:
                    if component == 'fear_greed_index':
                        # Normalizar Fear & Greed para -1 a 1
                        normalized = (df[component] - 50) / 50
                    else:
                        normalized = df[component]
                    
                    overall_sentiment += normalized * weight
            
            df['overall_sentiment'] = overall_sentiment.clip(-1, 1)
            
            # Classificar sentimento
            df['sentiment_label'] = pd.cut(
                df['overall_sentiment'],
                bins=[-1, -0.5, -0.2, 0.2, 0.5, 1],
                labels=['Very Bearish', 'Bearish', 'Neutral', 'Bullish', 'Very Bullish']
            ).astype(str)
            
            # Strength do sentimento (absoluto)
            df['sentiment_strength'] = abs(df['overall_sentiment'])
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no overall sentiment: {e}")
            df['overall_sentiment'] = 0
            df['sentiment_label'] = 'Neutral'
            df['sentiment_strength'] = 0
            return df
    
    def get_market_regime(self, df: pd.DataFrame) -> str:
        """Determinar regime de mercado baseado em sentimento"""
        try:
            if 'overall_sentiment' not in df.columns:
                return "Unknown"
            
            recent_sentiment = df['overall_sentiment'].tail(10).mean()
            sentiment_volatility = df['overall_sentiment'].tail(20).std()
            
            if recent_sentiment > 0.3 and sentiment_volatility < 0.3:
                return "Bull Market"
            elif recent_sentiment < -0.3 and sentiment_volatility < 0.3:
                return "Bear Market"
            elif sentiment_volatility > 0.5:
                return "High Volatility"
            else:
                return "Sideways Market"
                
        except Exception:
            return "Unknown"
    
    def get_sentiment_summary(self, df: pd.DataFrame) -> Dict:
        """Obter resumo completo do sentimento"""
        try:
            if df.empty:
                return {}
            
            latest = df.iloc[-1]
            
            return {
                'overall_sentiment': float(latest.get('overall_sentiment', 0)),
                'sentiment_label': str(latest.get('sentiment_label', 'Neutral')),
                'sentiment_strength': float(latest.get('sentiment_strength', 0)),
                'fear_greed_index': float(latest.get('fear_greed_index', 50)),
                'fear_greed_label': str(latest.get('fear_greed_label', 'Neutral')),
                'market_regime': self.get_market_regime(df),
                'components': {
                    'volume_sentiment': float(latest.get('volume_sentiment', 0)),
                    'volatility_sentiment': float(latest.get('volatility_sentiment', 0)),
                    'momentum_sentiment': float(latest.get('momentum_sentiment', 0)),
                    'breakout_sentiment': float(latest.get('breakout_sentiment', 0)),
                    'divergence_sentiment': float(latest.get('divergence_sentiment', 0)),
                    'relative_strength_sentiment': float(latest.get('relative_strength_sentiment', 0))
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo de sentimento: {e}")
            return {}
