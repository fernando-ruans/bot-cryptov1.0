"""Módulo de análise de mercado com IA para trading de alta precisão"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging
import requests
import json
import time

# Importações para análise de sentimento
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    logging.warning("TextBlob não disponível. Análise de sentimento limitada.")

# Importações para processamento de dados
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# Importações locais
from .technical_indicators import TechnicalIndicators
from .market_data import MarketDataManager
from .ai_engine import AITradingEngine
from .config import Config

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analisador de mercado com IA para identificar oportunidades de alta precisão"""
    
    def __init__(self, config: Config, market_data_manager: MarketDataManager, ai_engine: AITradingEngine):
        self.config = config
        self.market_data = market_data_manager
        self.ai_engine = ai_engine
        self.technical_indicators = TechnicalIndicators(config)
        self.market_context = {}
        self.last_analysis_time = {}
        self.market_regimes = {}
        self.correlation_matrix = None
        self.volatility_levels = {}
        self.sentiment_scores = {}
        self.liquidity_scores = {}
        
    def analyze_market_context(self, symbol: str, timeframe: str) -> Dict:
        """Analisa o contexto geral do mercado para o ativo"""
        try:
            # Verificar se precisamos atualizar a análise
            current_time = datetime.now()
            key = f"{symbol}_{timeframe}"
            
            # Atualizar apenas a cada 15 minutos para timeframes maiores que 1h
            # ou a cada 5 minutos para timeframes menores
            update_interval = 15 if timeframe in ['1h', '4h', '1d'] else 5
            
            if (key in self.last_analysis_time and 
                (current_time - self.last_analysis_time[key]).total_seconds() < update_interval * 60):
                return self.market_context.get(key, {})
            
            # Obter dados históricos
            df = self.market_data.get_historical_data(symbol, timeframe, limit=500)
            if df.empty:
                logger.error(f"Sem dados para análise de mercado: {symbol} {timeframe}")
                return {}
            
            # Calcular indicadores técnicos
            df = self.technical_indicators.calculate_all_indicators(df)
            
            # Análises específicas
            market_context = {}
            
            # 1. Análise de regime de mercado
            market_context['market_regime'] = self._detect_market_regime(df)
            
            # 2. Análise de volatilidade
            market_context['volatility'] = self._analyze_volatility(df)
            
            # 3. Análise de volume
            market_context['volume_analysis'] = self._analyze_volume(df)
            
            # 4. Análise de momentum
            market_context['momentum'] = self._analyze_momentum(df)
            
            # 5. Análise de correlação
            market_context['correlation'] = self._get_correlation_data(symbol)
            
            # 6. Análise de sentimento (se disponível)
            if self.config.AI_MARKET_ANALYSIS.get('sentiment_analysis', False):
                market_context['sentiment'] = self._get_market_sentiment(symbol)
            
            # 7. Análise de liquidez
            market_context['liquidity'] = self._analyze_liquidity(symbol)
            
            # 8. Análise de padrões
            market_context['patterns'] = self._detect_patterns(df)
            
            # 9. Índice de medo e ganância
            if self.config.AI_MARKET_ANALYSIS.get('fear_greed_index', False):
                market_context['fear_greed'] = self._get_fear_greed_index()
            
            # 10. Análise de dominância (para criptomoedas)
            if self.config.is_crypto_pair(symbol) and self.config.AI_MARKET_ANALYSIS.get('dominance_analysis', False):
                market_context['dominance'] = self._get_crypto_dominance(symbol)
            
            # Calcular score geral de mercado (0-1)
            market_context['market_score'] = self._calculate_market_score(market_context)
            
            # Armazenar contexto e tempo de análise
            self.market_context[key] = market_context
            self.last_analysis_time[key] = current_time
            
            logger.info(f"Análise de mercado concluída para {symbol} {timeframe}. Score: {market_context['market_score']:.2f}")
            return market_context
            
        except Exception as e:
            logger.error(f"Erro na análise de mercado: {e}")
            return {}
    
    def _detect_market_regime(self, df: pd.DataFrame) -> Dict:
        """Detecta o regime atual do mercado (tendência, range, volatilidade)"""
        try:
            # Calcular ADX para força de tendência
            adx_value = df['adx'].iloc[-1] if 'adx' in df.columns else 0
            
            # Calcular volatilidade usando ATR normalizado
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else 0
            atr_pct = atr / df['close'].iloc[-1]
            
            # Calcular direção da tendência usando EMAs
            ema_short = df['ema_12'].iloc[-1] if 'ema_12' in df.columns else df['close'].iloc[-1]
            ema_long = df['ema_50'].iloc[-1] if 'ema_50' in df.columns else df['close'].iloc[-1]
            trend_direction = 1 if ema_short > ema_long else -1 if ema_short < ema_long else 0
            
            # Verificar se está em range usando Bollinger Bands
            bb_width = (df['bb_upper'].iloc[-1] - df['bb_lower'].iloc[-1]) / df['bb_middle'].iloc[-1] \
                if all(x in df.columns for x in ['bb_upper', 'bb_lower', 'bb_middle']) else 0.05
            
            # Determinar regime
            if adx_value > 25 and trend_direction > 0:
                regime = "uptrend"
                strength = min(adx_value / 50, 1.0)
            elif adx_value > 25 and trend_direction < 0:
                regime = "downtrend"
                strength = min(adx_value / 50, 1.0)
            elif bb_width < 0.05:
                regime = "tight_range"
                strength = 1.0 - bb_width / 0.05
            elif atr_pct > 0.03:
                regime = "volatile"
                strength = min(atr_pct / 0.05, 1.0)
            else:
                regime = "range"
                strength = 1.0 - (adx_value / 25)
              # Armazenar regime para o símbolo
            symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else "unknown"
            self.market_regimes[symbol] = regime
            
            return {
                "regime": regime,
                "strength": strength,
                "adx": adx_value,
                "volatility": atr_pct,
                "trend_direction": trend_direction,
                "bb_width": bb_width
            }
        except Exception as e:
            logger.error(f"Erro na detecção de regime de mercado: {e}")
            return {"regime": "unknown", "strength": 0.5}
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """Analisa a volatilidade do mercado"""
        try:
            # Calcular volatilidade histórica (corrigido)
            returns = df['close'].pct_change(fill_method=None).dropna()
            hist_vol = returns.std() * np.sqrt(252)  # Anualizada
            
            # Comparar com ATR
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else 0
            atr_pct = atr / df['close'].iloc[-1]
            
            # Calcular percentis de volatilidade
            vol_20d = returns.rolling(20).std().iloc[-1] * np.sqrt(252) if len(returns) >= 20 else hist_vol
            vol_50d = returns.rolling(50).std().iloc[-1] * np.sqrt(252) if len(returns) >= 50 else hist_vol
            
            # Determinar nível de volatilidade
            if vol_20d > vol_50d * 1.5:
                vol_level = "very_high"
                vol_score = 0.9
            elif vol_20d > vol_50d * 1.2:
                vol_level = "high"
                vol_score = 0.75
            elif vol_20d < vol_50d * 0.8:
                vol_level = "low"
                vol_score = 0.25
            elif vol_20d < vol_50d * 0.5:
                vol_level = "very_low"
                vol_score = 0.1
            else:
                vol_level = "normal"
                vol_score = 0.5
            
            # Armazenar nível de volatilidade
            symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else "unknown"
            self.volatility_levels[symbol] = vol_level
            
            return {
                "level": vol_level,
                "score": vol_score,
                "historical": hist_vol,
                "current": vol_20d,
                "atr_pct": atr_pct,
                "change": (vol_20d / vol_50d) - 1 if vol_50d > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de volatilidade: {e}")
            return {"level": "normal", "score": 0.5}
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analisa o volume de negociação"""
        try:
            if 'volume' not in df.columns:
                return {"level": "unknown", "score": 0.5}
            
            # Calcular médias de volume
            vol_current = df['volume'].iloc[-1]
            vol_avg_20 = df['volume'].rolling(20).mean().iloc[-1] if len(df) >= 20 else vol_current
            vol_avg_50 = df['volume'].rolling(50).mean().iloc[-1] if len(df) >= 50 else vol_current
              # Calcular relação com preço (corrigido)
            price_change = df['close'].pct_change(fill_method=None).iloc[-1] if len(df) > 1 else 0
            vol_change = df['volume'].pct_change(fill_method=None).iloc[-1] if len(df) > 1 else 0
            
            # Volume em relação à média
            vol_ratio_20 = vol_current / vol_avg_20 if vol_avg_20 > 0 else 1.0
            vol_ratio_50 = vol_current / vol_avg_50 if vol_avg_50 > 0 else 1.0
            
            # Determinar nível de volume
            if vol_ratio_20 > 2.0:
                vol_level = "very_high"
                vol_score = 0.9
            elif vol_ratio_20 > 1.5:
                vol_level = "high"
                vol_score = 0.75
            elif vol_ratio_20 < 0.7:
                vol_level = "low"
                vol_score = 0.25
            elif vol_ratio_20 < 0.5:
                vol_level = "very_low"
                vol_score = 0.1
            else:
                vol_level = "normal"
                vol_score = 0.5
            
            # Verificar divergência de volume/preço
            if abs(price_change) > 0.01 and abs(vol_change) > 0.2:
                if (price_change > 0 and vol_change > 0) or (price_change < 0 and vol_change > 0):
                    divergence = "confirming"
                else:
                    divergence = "diverging"
            else:
                divergence = "neutral"
            
            return {
                "level": vol_level,
                "score": vol_score,
                "current_ratio": vol_ratio_20,
                "trend_ratio": vol_ratio_50,
                "divergence": divergence,
                "price_vol_correlation": np.sign(price_change) * np.sign(vol_change) * min(abs(vol_change), 1.0)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de volume: {e}")
            return {"level": "normal", "score": 0.5}
    
    def _analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Analisa o momentum do mercado"""
        try:
            # Verificar indicadores de momentum
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
            macd = df['macd'].iloc[-1] if 'macd' in df.columns else 0
            macd_signal = df['macd_signal'].iloc[-1] if 'macd_signal' in df.columns else 0
            macd_hist = df['macd_hist'].iloc[-1] if 'macd_hist' in df.columns else 0
              # Calcular retornos
            ret_1d = df['close'].pct_change(1, fill_method=None).iloc[-1] if len(df) > 1 else 0
            ret_5d = df['close'].pct_change(5, fill_method=None).iloc[-1] if len(df) > 5 else 0
            ret_20d = df['close'].pct_change(20, fill_method=None).iloc[-1] if len(df) > 20 else 0
            
            # Determinar força e direção do momentum
            if rsi > 70:
                momentum_level = "overbought"
                momentum_score = 0.2  # Baixo score para overbought (potencial reversão)
            elif rsi < 30:
                momentum_level = "oversold"
                momentum_score = 0.8  # Alto score para oversold (potencial reversão)
            elif rsi > 60 and macd > 0 and macd > macd_signal:
                momentum_level = "strong_bullish"
                momentum_score = 0.9
            elif rsi < 40 and macd < 0 and macd < macd_signal:
                momentum_level = "strong_bearish"
                momentum_score = 0.1
            elif rsi > 50 and macd > 0:
                momentum_level = "bullish"
                momentum_score = 0.7
            elif rsi < 50 and macd < 0:
                momentum_level = "bearish"
                momentum_score = 0.3
            else:
                momentum_level = "neutral"
                momentum_score = 0.5
            
            # Verificar divergências
            price_making_higher_high = df['high'].iloc[-1] > df['high'].iloc[-2] if len(df) > 2 else False
            price_making_lower_low = df['low'].iloc[-1] < df['low'].iloc[-2] if len(df) > 2 else False
            
            rsi_making_higher_high = False
            rsi_making_lower_low = False
            
            if 'rsi' in df.columns and len(df) > 2:
                rsi_making_higher_high = df['rsi'].iloc[-1] > df['rsi'].iloc[-2]
                rsi_making_lower_low = df['rsi'].iloc[-1] < df['rsi'].iloc[-2]
            
            # Detectar divergências
            bullish_divergence = price_making_lower_low and not rsi_making_lower_low
            bearish_divergence = price_making_higher_high and not rsi_making_higher_high
            
            return {
                "level": momentum_level,
                "score": momentum_score,
                "rsi": rsi,
                "macd": macd,
                "macd_hist": macd_hist,
                "return_1d": ret_1d,
                "return_5d": ret_5d,
                "return_20d": ret_20d,
                "bullish_divergence": bullish_divergence,
                "bearish_divergence": bearish_divergence
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de momentum: {e}")
            return {"level": "neutral", "score": 0.5}
    
    def _get_correlation_data(self, symbol: str) -> Dict:
        """Obtém dados de correlação com outros ativos"""
        try:
            # Se não tivermos matriz de correlação ou se ela estiver desatualizada (>1 hora)
            if self.correlation_matrix is None or \
               (hasattr(self.correlation_matrix, 'last_update') and \
                (datetime.now() - self.correlation_matrix.last_update).total_seconds() > 3600):
                
                # Obter dados de fechamento para todos os pares
                all_pairs = self.config.get_all_pairs()
                close_data = {}
                
                for pair in all_pairs:
                    df = self.market_data.get_historical_data(pair, '1d', limit=30)
                    if not df.empty:
                        close_data[pair] = df['close']
                
                # Criar DataFrame com todos os preços de fechamento                if close_data:
                    price_df = pd.DataFrame(close_data)
                    # Calcular retornos (corrigido para evitar FutureWarning)
                    returns_df = price_df.pct_change(fill_method=None).dropna()
                    # Calcular matriz de correlação
                    self.correlation_matrix = returns_df.corr()
                    self.correlation_matrix.last_update = datetime.now()
            
            # Se não temos dados de correlação
            if self.correlation_matrix is None or symbol not in self.correlation_matrix.columns:
                return {"correlated_assets": [], "correlation_score": 0.5}
            
            # Obter correlações para o símbolo
            correlations = self.correlation_matrix[symbol].sort_values(ascending=False)
            
            # Remover auto-correlação
            correlations = correlations[correlations.index != symbol]
            
            # Obter os 5 ativos mais correlacionados e os 5 menos correlacionados
            top_correlated = correlations.head(5).to_dict()
            bottom_correlated = correlations.tail(5).to_dict()
            
            # Calcular score de correlação (média das correlações absolutas)
            correlation_score = correlations.abs().mean()
            
            return {
                "top_correlated": top_correlated,
                "bottom_correlated": bottom_correlated,
                "correlation_score": correlation_score,
                "btc_correlation": correlations.get("BTCUSDT", 0) if symbol != "BTCUSDT" else 0,
                "eth_correlation": correlations.get("ETHUSDT", 0) if symbol != "ETHUSDT" else 0
            }
            
        except Exception as e:
            logger.error(f"Erro na obtenção de dados de correlação: {e}")
            return {"correlated_assets": [], "correlation_score": 0.5}
    
    def _get_market_sentiment(self, symbol: str) -> Dict:
        """Obtém sentimento de mercado para o ativo"""
        try:
            # Verificar se já temos dados de sentimento recentes (< 1 hora)
            current_time = datetime.now()
            if symbol in self.sentiment_scores and \
               (current_time - self.sentiment_scores[symbol].get('timestamp', datetime.min)).total_seconds() < 3600:
                return self.sentiment_scores[symbol]
            
            # Implementar análise de sentimento básica
            # Em um sistema real, isso seria conectado a APIs de notícias/social media
            
            # Simulação de sentimento baseado em indicadores técnicos
            df = self.market_data.get_historical_data(symbol, '1h', limit=24)
            if df.empty:
                return {"sentiment": "neutral", "score": 0.5}
            
            # Usar RSI e MACD como proxy para sentimento
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
            macd_hist = df['macd_hist'].iloc[-1] if 'macd_hist' in df.columns else 0
            
            # Calcular retornos recentes
            returns = df['close'].pct_change().dropna()
            recent_returns = returns.iloc[-5:].mean() if len(returns) >= 5 else 0
            
            # Calcular score de sentimento (0-1)
            sentiment_score = 0.5  # Neutro por padrão
            
            # Ajustar com base no RSI (0-100 -> 0-1)
            sentiment_score += (rsi - 50) / 100
            
            # Ajustar com base no MACD
            if abs(macd_hist) > 0:
                sentiment_score += np.sign(macd_hist) * min(abs(macd_hist) / 10, 0.1)
            
            # Ajustar com base nos retornos recentes
            sentiment_score += np.sign(recent_returns) * min(abs(recent_returns) * 10, 0.1)
            
            # Limitar entre 0 e 1
            sentiment_score = max(0, min(1, sentiment_score))
            
            # Determinar categoria de sentimento
            if sentiment_score > 0.8:
                sentiment = "very_bullish"
            elif sentiment_score > 0.6:
                sentiment = "bullish"
            elif sentiment_score < 0.2:
                sentiment = "very_bearish"
            elif sentiment_score < 0.4:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            # Armazenar resultado
            result = {
                "sentiment": sentiment,
                "score": sentiment_score,
                "rsi_component": (rsi - 50) / 100,
                "macd_component": np.sign(macd_hist) * min(abs(macd_hist) / 10, 0.1) if abs(macd_hist) > 0 else 0,
                "returns_component": np.sign(recent_returns) * min(abs(recent_returns) * 10, 0.1),
                "timestamp": current_time
            }
            
            self.sentiment_scores[symbol] = result
            return result
            
        except Exception as e:
            logger.error(f"Erro na obtenção de sentimento de mercado: {e}")
            return {"sentiment": "neutral", "score": 0.5}
    
    def _analyze_liquidity(self, symbol: str) -> Dict:
        """Analisa a liquidez do mercado para o ativo"""
        try:
            # Verificar se já temos dados de liquidez recentes (< 1 hora)
            current_time = datetime.now()
            if symbol in self.liquidity_scores and \
               (current_time - self.liquidity_scores[symbol].get('timestamp', datetime.min)).total_seconds() < 3600:
                return self.liquidity_scores[symbol]
            
            # Em um sistema real, isso usaria dados de order book e volume
            # Aqui vamos simular com base no volume
            
            df = self.market_data.get_historical_data(symbol, '1h', limit=24)
            if df.empty or 'volume' not in df.columns:
                return {"liquidity": "medium", "score": 0.5}
            
            # Calcular volume médio
            avg_volume = df['volume'].mean()
            
            # Calcular volume em USD
            avg_price = df['close'].mean()
            volume_usd = avg_volume * avg_price
            
            # Determinar nível de liquidez com base no volume USD
            # Valores são exemplos e devem ser ajustados por ativo
            if volume_usd > 100000000:  # $100M
                liquidity = "very_high"
                liquidity_score = 0.9
            elif volume_usd > 10000000:  # $10M
                liquidity = "high"
                liquidity_score = 0.75
            elif volume_usd > 1000000:  # $1M
                liquidity = "medium"
                liquidity_score = 0.5
            elif volume_usd > 100000:  # $100K
                liquidity = "low"
                liquidity_score = 0.25
            else:
                liquidity = "very_low"
                liquidity_score = 0.1
            
            # Calcular volatilidade do volume
            volume_volatility = df['volume'].std() / avg_volume if avg_volume > 0 else 1.0
            
            # Resultado
            result = {
                "liquidity": liquidity,
                "score": liquidity_score,
                "volume_usd": volume_usd,
                "volume_volatility": volume_volatility,
                "timestamp": current_time
            }
            
            self.liquidity_scores[symbol] = result
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de liquidez: {e}")
            return {"liquidity": "medium", "score": 0.5}
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict:
        """Detecta padrões de preço no gráfico"""
        try:
            if len(df) < 10:
                return {"patterns": [], "pattern_score": 0.5}
            
            patterns = []
            pattern_scores = []
            
            # Detectar padrões de candle
            # Doji
            last_candle = df.iloc[-1]
            if abs(last_candle['open'] - last_candle['close']) / (last_candle['high'] - last_candle['low']) < 0.1:
                patterns.append("doji")
                pattern_scores.append(0.5)  # Neutro
            
            # Martelo/Enforcado
            body_size = abs(last_candle['open'] - last_candle['close'])
            lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
            upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
            
            if lower_wick > body_size * 2 and upper_wick < body_size * 0.5:
                if last_candle['close'] > last_candle['open']:
                    patterns.append("hammer")
                    pattern_scores.append(0.7)  # Bullish
                else:
                    patterns.append("hanging_man")
                    pattern_scores.append(0.3)  # Bearish
            
            # Engolfo
            if len(df) > 1:
                prev_candle = df.iloc[-2]
                curr_candle = last_candle
                
                # Engolfo de alta
                if prev_candle['close'] < prev_candle['open'] and \
                   curr_candle['close'] > curr_candle['open'] and \
                   curr_candle['open'] <= prev_candle['close'] and \
                   curr_candle['close'] >= prev_candle['open']:
                    patterns.append("bullish_engulfing")
                    pattern_scores.append(0.8)  # Muito bullish
                
                # Engolfo de baixa
                elif prev_candle['close'] > prev_candle['open'] and \
                     curr_candle['close'] < curr_candle['open'] and \
                     curr_candle['open'] >= prev_candle['close'] and \
                     curr_candle['close'] <= prev_candle['open']:
                    patterns.append("bearish_engulfing")
                    pattern_scores.append(0.2)  # Muito bearish
            
            # Detectar padrões de indicadores
            # Cruzamento de médias móveis
            if 'ema_12' in df.columns and 'ema_26' in df.columns and len(df) > 1:
                curr = df.iloc[-1]
                prev = df.iloc[-2]
                
                if prev['ema_12'] <= prev['ema_26'] and curr['ema_12'] > curr['ema_26']:
                    patterns.append("golden_cross_small")
                    pattern_scores.append(0.7)  # Bullish
                
                elif prev['ema_12'] >= prev['ema_26'] and curr['ema_12'] < curr['ema_26']:
                    patterns.append("death_cross_small")
                    pattern_scores.append(0.3)  # Bearish
            
            # Cruzamento de médias móveis maiores
            if 'sma_50' in df.columns and 'sma_200' in df.columns and len(df) > 1:
                curr = df.iloc[-1]
                prev = df.iloc[-2]
                
                if prev['sma_50'] <= prev['sma_200'] and curr['sma_50'] > curr['sma_200']:
                    patterns.append("golden_cross")
                    pattern_scores.append(0.8)  # Muito bullish
                
                elif prev['sma_50'] >= prev['sma_200'] and curr['sma_50'] < curr['sma_200']:
                    patterns.append("death_cross")
                    pattern_scores.append(0.2)  # Muito bearish
            
            # Calcular score médio dos padrões
            pattern_score = sum(pattern_scores) / len(pattern_scores) if pattern_scores else 0.5
            
            return {
                "patterns": patterns,
                "pattern_score": pattern_score,
                "pattern_count": len(patterns)
            }
            
        except Exception as e:
            logger.error(f"Erro na detecção de padrões: {e}")
            return {"patterns": [], "pattern_score": 0.5}
    
    def _get_fear_greed_index(self) -> Dict:
        """Obtém o índice de medo e ganância do mercado"""
        try:
            # Em um sistema real, isso seria conectado a uma API externa
            # Aqui vamos simular com base em indicadores técnicos do BTC
            
            df = self.market_data.get_historical_data("BTCUSDT", '1d', limit=30)
            if df.empty:
                return {"value": 50, "classification": "neutral"}
            
            # Calcular componentes do índice
            # 1. Volatilidade (20%)
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Anualizada
            volatility_score = max(0, min(100, 100 - volatility * 100))
            
            # 2. Momentum (20%)
            momentum = df['close'].iloc[-1] / df['close'].iloc[-7] - 1 if len(df) >= 7 else 0
            momentum_score = max(0, min(100, 50 + momentum * 500))
            
            # 3. RSI (20%)
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
            rsi_score = rsi  # RSI já é 0-100
            
            # 4. Tendência de preço (20%)
            price_trend = df['close'].iloc[-1] / df['close'].iloc[-30] - 1 if len(df) >= 30 else 0
            price_trend_score = max(0, min(100, 50 + price_trend * 200))
            
            # 5. Volume (20%)
            if 'volume' in df.columns and len(df) >= 7:
                volume_change = df['volume'].iloc[-1] / df['volume'].iloc[-7:].mean() - 1
                volume_score = max(0, min(100, 50 + volume_change * 100))
            else:
                volume_score = 50
            
            # Calcular índice final (média ponderada)
            fear_greed_value = int(0.2 * volatility_score + 0.2 * momentum_score + 
                                  0.2 * rsi_score + 0.2 * price_trend_score + 
                                  0.2 * volume_score)
            
            # Classificar
            if fear_greed_value >= 80:
                classification = "extreme_greed"
            elif fear_greed_value >= 60:
                classification = "greed"
            elif fear_greed_value > 40:
                classification = "neutral"
            elif fear_greed_value > 20:
                classification = "fear"
            else:
                classification = "extreme_fear"
            
            return {
                "value": fear_greed_value,
                "classification": classification,
                "components": {
                    "volatility": volatility_score,
                    "momentum": momentum_score,
                    "rsi": rsi_score,
                    "price_trend": price_trend_score,
                    "volume": volume_score
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na obtenção do índice de medo e ganância: {e}")
            return {"value": 50, "classification": "neutral"}
    
    def _get_crypto_dominance(self, symbol: str) -> Dict:
        """Obtém dados de dominância para criptomoedas"""
        try:
            # Em um sistema real, isso seria conectado a uma API externa
            # Aqui vamos retornar valores simulados
            
            # Extrair a moeda do par (ex: BTCUSDT -> BTC)
            coin = symbol.replace("USDT", "").replace("USD", "")
            
            # Valores padrão
            dominance = 0.0
            market_cap = 0.0
            rank = 0
            
            # Valores simulados para moedas comuns
            if coin == "BTC":
                dominance = 0.45  # 45%
                market_cap = 1000000000000  # $1T
                rank = 1
            elif coin == "ETH":
                dominance = 0.18  # 18%
                market_cap = 400000000000  # $400B
                rank = 2
            elif coin == "BNB":
                dominance = 0.03  # 3%
                market_cap = 70000000000  # $70B
                rank = 3
            elif coin == "XRP":
                dominance = 0.02  # 2%
                market_cap = 50000000000  # $50B
                rank = 4
            elif coin == "ADA":
                dominance = 0.01  # 1%
                market_cap = 30000000000  # $30B
                rank = 5
            else:
                dominance = 0.005  # 0.5%
                market_cap = 10000000000  # $10B
                rank = 10
            
            return {
                "dominance": dominance,
                "market_cap": market_cap,
                "rank": rank,
                "top_10": rank <= 10
            }
            
        except Exception as e:
            logger.error(f"Erro na obtenção de dados de dominância: {e}")
            return {"dominance": 0.01, "market_cap": 0, "rank": 100}
    
    def _calculate_market_score(self, market_context: Dict) -> float:
        """Calcula um score geral para o contexto de mercado (0-1)"""
        try:
            scores = []
            weights = []
            
            # Regime de mercado
            if 'market_regime' in market_context:
                regime = market_context['market_regime']
                regime_score = 0.5  # Neutro por padrão
                
                # Ajustar com base no regime
                if regime.get('regime') == "uptrend":
                    regime_score = 0.7 + (regime.get('strength', 0) * 0.3)  # 0.7-1.0
                elif regime.get('regime') == "downtrend":
                    regime_score = 0.3 - (regime.get('strength', 0) * 0.3)  # 0.0-0.3
                elif regime.get('regime') == "volatile":
                    regime_score = 0.4  # Volátil é ligeiramente negativo
                elif regime.get('regime') == "tight_range":
                    regime_score = 0.6  # Range apertado é ligeiramente positivo
                
                scores.append(regime_score)
                weights.append(0.25)  # 25% do peso
            
            # Volatilidade
            if 'volatility' in market_context:
                vol_score = market_context['volatility'].get('score', 0.5)
                scores.append(vol_score)
                weights.append(0.15)  # 15% do peso
            
            # Volume
            if 'volume_analysis' in market_context:
                vol_score = market_context['volume_analysis'].get('score', 0.5)
                scores.append(vol_score)
                weights.append(0.15)  # 15% do peso
            
            # Momentum
            if 'momentum' in market_context:
                mom_score = market_context['momentum'].get('score', 0.5)
                scores.append(mom_score)
                weights.append(0.20)  # 20% do peso
            
            # Padrões
            if 'patterns' in market_context:
                pattern_score = market_context['patterns'].get('pattern_score', 0.5)
                scores.append(pattern_score)
                weights.append(0.10)  # 10% do peso
            
            # Sentimento
            if 'sentiment' in market_context:
                sent_score = market_context['sentiment'].get('score', 0.5)
                scores.append(sent_score)
                weights.append(0.10)  # 10% do peso
            
            # Liquidez
            if 'liquidity' in market_context:
                liq_score = market_context['liquidity'].get('score', 0.5)
                scores.append(liq_score)
                weights.append(0.05)  # 5% do peso
            
            # Calcular média ponderada
            if not scores:
                return 0.5
            
            # Normalizar pesos
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            
            # Calcular score final
            final_score = sum(s * w for s, w in zip(scores, weights))
            
            return final_score
            
        except Exception as e:
            logger.error(f"Erro no cálculo do score de mercado: {e}")
            return 0.5
    
    def get_trade_recommendation(self, symbol: str, timeframe: str) -> Dict:
        """Gera uma recomendação de trade com base na análise de mercado e IA"""
        try:
            # Analisar contexto de mercado
            market_context = self.analyze_market_context(symbol, timeframe)
            market_score = market_context.get('market_score', 0.5)
            
            # Verificar se o score de mercado atende ao mínimo configurado
            min_market_score = self.config.SIGNAL_CONFIG.get('min_market_score', 0.0)
            if market_score < min_market_score:
                logger.info(f"Score de mercado {market_score:.2f} abaixo do mínimo {min_market_score:.2f} para {symbol} {timeframe}")
                return {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "recommendation": "hold",  # Manter HOLD quando score insuficiente
                    "confidence": 0.3,
                    "market_score": market_score,
                    "ai_score": 0.0,
                    "entry_price": 0.0,
                    "stop_loss": 0.0,
                    "take_profit": 0.0,
                    "risk_reward": 0.0,
                    "reasons": ["Score de mercado insuficiente - mantendo HOLD"]
                }
            
            # Obter dados históricos
            df = self.market_data.get_historical_data(symbol, timeframe, limit=500)
            if df.empty:
                logger.error(f"Sem dados para recomendação de trade: {symbol} {timeframe}")
                return {}
              # Preparar features para o modelo de IA
            df = self.ai_engine.prepare_features(df)            # Obter previsão do modelo de IA (sem timeframe - não usado pelo método)
            ai_prediction = self.ai_engine.predict_signal(df, symbol)
            
            # Extrair sinal e confiança do modelo de IA
            signal_text = ai_prediction.get('signal', 'hold')  # IA retorna string
            confidence = ai_prediction.get('confidence', 0.0)
            
            # Mapear sinal da IA para recomendação respeitando a decisão
            recommendation = signal_text  # Respeitar decisão da IA sem sobrescrita
            
            # IMPORTANTE: Respeitar decisão da IA e não sobrescrever BUY/SELL explícitos
            logger.info(f"🧠 IA decidiu: '{signal_text}' → Recomendação final: '{recommendation}' (confiança: {confidence:.3f})")            # Se IA decidiu HOLD, tentar usar análise técnica como backup
            if recommendation == 'hold':  # Sempre tentar melhorar HOLD, independente da confiança
                # Calcular indicadores técnicos se ainda não foi feito
                if 'df_with_tech' not in locals():
                    from .technical_indicators import TechnicalIndicators
                    tech_indicators = TechnicalIndicators(self.config)
                    df_with_tech = tech_indicators.calculate_all_indicators(df.copy())
                
                # Análise técnica como backup para HOLD
                tech_backup = self._simple_technical_analysis(df_with_tech)
                tech_signal = tech_backup.get('signal', 'hold')
                tech_confidence = tech_backup.get('confidence', 0)
                
                # Se análise técnica tem uma direção clara, usar ela
                if tech_signal in ['buy', 'sell'] and tech_confidence > 0.2:  # Threshold baixo
                    recommendation = tech_signal
                    # Combinar confiança da IA + técnica
                    confidence = min(confidence * 0.7 + tech_confidence * 0.6, 0.8)  # Boost significativo
                    logger.info(f"🔄 HOLD convertido para {tech_signal.upper()} usando análise técnica (IA: {ai_prediction.get('confidence', 0):.3f}, Técnica: {tech_confidence:.3f}, Final: {confidence:.3f})")
                else:
                    logger.info(f"🟡 Mantendo HOLD - análise técnica também neutra")
            
            # Ajustar confiança baseado no score de mercado (penalizar scores baixos)
            market_confidence_factor = min(1.0, market_score / 0.7)  # Fator máximo quando score >= 0.7
            confidence = confidence * market_confidence_factor
            logger.info(f"📊 Confiança ajustada pelo mercado: {confidence:.3f} (fator: {market_confidence_factor:.2f})")
            
            # Verificar APENAS confiança mínima geral (não específica da IA)
            min_confidence = self.config.SIGNAL_CONFIG.get('min_confidence', 0.0)
            if confidence < min_confidence:
                logger.info(f"Confiança {confidence:.2f} abaixo do mínimo {min_confidence:.2f} para {symbol}")
                # Se confiança muito baixa, converter para HOLD
                if confidence < 0.4:
                    recommendation = 'hold'
                    confidence = 0.4
                    logger.info(f"Convertendo para HOLD devido à baixa confiança")
                else:
                    confidence = max(confidence, 0.3)  # Mínimo de 30% confiança
            
            # Calcular preço atual
            current_price = df['close'].iloc[-1]
            
            # Calcular níveis de stop loss e take profit (1:1 ratio)
            stop_loss_pct = self.config.RISK_MANAGEMENT.get('stop_loss_pct', 0.025)  # 2.5%
            take_profit_pct = self.config.RISK_MANAGEMENT.get('take_profit_pct', 0.025)  # 2.5%
            
            # Ajustar com base no ATR para maior precisão
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.01
            atr_multiplier = 1.5  # Multiplicador de ATR
            
            # Calcular níveis
            if recommendation == "buy":
                stop_loss = current_price * (1 - stop_loss_pct)
                take_profit = current_price * (1 + take_profit_pct)
                
                # Ajustar com ATR
                stop_loss = current_price - (atr * atr_multiplier)
                take_profit = current_price + (atr * atr_multiplier)
            elif recommendation == "sell":
                stop_loss = current_price * (1 + stop_loss_pct)
                take_profit = current_price * (1 - take_profit_pct)
                
                # Ajustar com ATR
                stop_loss = current_price + (atr * atr_multiplier)
                take_profit = current_price - (atr * atr_multiplier)
            else:
                stop_loss = 0.0
                take_profit = 0.0
              # Calcular risk/reward ratio
            risk_reward = 1.0  # 1:1 por padrão
            if abs(current_price - stop_loss) > 0:  # Sempre há recomendação válida agora
                risk_reward = abs(take_profit - current_price) / abs(current_price - stop_loss)
              # Obter análise técnica separadamente para incluir no resultado
            if 'df_with_tech' not in locals():
                from .technical_indicators import TechnicalIndicators
                tech_indicators = TechnicalIndicators(self.config)
                df_with_tech = tech_indicators.calculate_all_indicators(df.copy())
            
            # Análise técnica simplificada para usar como tiebreaker
            tech_analysis = self._simple_technical_analysis(df_with_tech)
            
            # Gerar razões para a recomendação
            reasons = self._generate_recommendation_reasons(recommendation, df, market_context, ai_prediction)
            
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "recommendation": recommendation,
                "confidence": confidence,
                "market_score": market_score,
                "ai_score": confidence,
                "entry_price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "risk_reward": risk_reward,
                "reasons": reasons,
                "market_context": market_context,
                "ai_prediction": ai_prediction,
                "technical_analysis": tech_analysis  # Adicionar análise técnica
            }
            
        except Exception as e:
            logger.error(f"Erro na geração de recomendação de trade: {e}")
            return {}
    
    def _detectar_tendencia(self, df: pd.DataFrame) -> str:
        """Detecta a tendência atual do mercado (alta, baixa, lateral)"""
        try:
            if df.empty or 'close' not in df.columns:
                return "lateral"
            
            # Calcular médias móveis
            media_curta = df['close'].rolling(window=20).mean()
            media_longa = df['close'].rolling(window=50).mean()
            
            # Últimos valores
            ultimo_preco = df['close'].iloc[-1]
            ultima_media_curta = media_curta.iloc[-1]
            ultima_media_longa = media_longa.iloc[-1]
              # Detectar cruzamentos
            if ultima_media_curta > ultima_media_longa:
                return "alta"
            elif ultima_media_curta < ultima_media_longa:
                return "baixa"
            else:
                return "lateral"
        except Exception as e:
            logger.error(f"Erro na detecção de tendência: {e}")
            return "lateral"
    
    def _simple_technical_analysis(self, df: pd.DataFrame) -> Dict:
        """Análise técnica simplificada para usar como tiebreaker"""
        try:
            if df.empty:
                return {'signal': 'hold', 'confidence': 0}
            
            latest = df.iloc[-1]
            buy_signals = 0
            sell_signals = 0
            total_signals = 0
            
            # RSI
            if 'rsi' in latest and not pd.isna(latest['rsi']):
                rsi = latest['rsi']
                total_signals += 1
                if rsi < 35:
                    buy_signals += 2
                elif rsi < 45:
                    buy_signals += 1
                elif rsi > 65:
                    sell_signals += 2
                elif rsi > 55:
                    sell_signals += 1
            
            # MACD
            if ('macd' in latest and 'macd_signal' in latest and 
                not pd.isna(latest['macd']) and not pd.isna(latest['macd_signal'])):
                total_signals += 1
                if latest['macd'] > latest['macd_signal']:
                    buy_signals += 1
                else:
                    sell_signals += 1
            
            # EMA
            if ('ema_12' in latest and 'ema_26' in latest and 
                not pd.isna(latest['ema_12']) and not pd.isna(latest['ema_26'])):
                total_signals += 1
                if latest['ema_12'] > latest['ema_26']:
                    buy_signals += 1
                else:
                    sell_signals += 1
            
            # Bollinger Bands
            if ('bb_lower' in latest and 'bb_upper' in latest and 'close' in latest and
                not pd.isna(latest['bb_lower']) and not pd.isna(latest['bb_upper'])):
                total_signals += 1
                close_price = latest['close']
                bb_position = (close_price - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
                if bb_position <= 0.2:  # Próximo à banda inferior
                    buy_signals += 1
                elif bb_position >= 0.8:  # Próximo à banda superior
                    sell_signals += 1
              # Determinar sinal com base na força
            if total_signals == 0:
                return {'signal': 'hold', 'confidence': 0}
            
            buy_strength = buy_signals / max(total_signals, 1)
            sell_strength = sell_signals / max(total_signals, 1)
            
            logger.info(f"📊 Análise técnica simples: Buy:{buy_signals}, Sell:{sell_signals}, Total:{total_signals}")
            logger.info(f"📊 Força: Buy:{buy_strength:.2f}, Sell:{sell_strength:.2f}")
            
            if buy_signals > sell_signals and buy_strength > 0.3:
                confidence = min(buy_strength, 0.8)
                logger.info(f"📊 Técnica → BUY (confiança: {confidence:.2f})")
                return {'signal': 'buy', 'confidence': confidence}
            elif sell_signals > buy_signals and sell_strength > 0.3:
                confidence = min(sell_strength, 0.8)
                logger.info(f"📊 Técnica → SELL (confiança: {confidence:.2f})")
                return {'signal': 'sell', 'confidence': confidence}
            else:
                logger.info(f"📊 Técnica → HOLD (sinais equilibrados)")
                return {'signal': 'hold', 'confidence': 0}
                
        except Exception as e:
            logger.error(f"Erro na análise técnica simples: {e}")
            return {'signal': 'hold', 'confidence': 0}

    def _generate_recommendation_reasons(self, recommendation: str, df: pd.DataFrame, 
                                        market_context: Dict, ai_prediction: Dict) -> List[str]:
        """Gera razões para a recomendação de trade"""
        reasons = []
        
        try:
            # Razões baseadas no tipo de recomendação
            confidence_pct = ai_prediction.get('confidence', 0) * 100  # Converter para porcentagem
            
            if recommendation == "buy":
                reasons.append(f"IA prevê movimento de alta com {confidence_pct:.1f}% de confiança")
            elif recommendation == "sell":
                reasons.append(f"IA prevê movimento de baixa com {confidence_pct:.1f}% de confiança")
            
            # Razões baseadas no regime de mercado
            if 'market_regime' in market_context:
                regime = market_context['market_regime'].get('regime', "unknown")
                strength = market_context['market_regime'].get('strength', 0)
                
                if regime == "uptrend" and strength > 0.7:
                    reasons.append(f"Tendência de alta forte (força: {strength:.1%})")
                elif regime == "uptrend":
                    reasons.append(f"Tendência de alta (força: {strength:.1%})")
                elif regime == "downtrend" and strength > 0.7:
                    reasons.append(f"Tendência de baixa forte (força: {strength:.1%})")
                elif regime == "downtrend":
                    reasons.append(f"Tendência de baixa (força: {strength:.1%})")
                elif regime == "range":
                    reasons.append("Mercado em range lateral")
                elif regime == "volatile":
                    reasons.append("Mercado com alta volatilidade")
            
            # Razões baseadas em momentum
            if 'momentum' in market_context:
                momentum_level = market_context['momentum'].get('level', "neutral")
                rsi = market_context['momentum'].get('rsi', 50)
                
                if momentum_level == "strong_bullish":
                    reasons.append(f"Momentum fortemente positivo (RSI: {rsi:.1f})")
                elif momentum_level == "bullish":
                    reasons.append(f"Momentum positivo (RSI: {rsi:.1f})")
                elif momentum_level == "strong_bearish":
                    reasons.append(f"Momentum fortemente negativo (RSI: {rsi:.1f})")
                elif momentum_level == "bearish":
                    reasons.append(f"Momentum negativo (RSI: {rsi:.1f})")
                elif momentum_level == "overbought":
                    reasons.append(f"Mercado sobrecomprado (RSI: {rsi:.1f})")
                elif momentum_level == "oversold":
                    reasons.append(f"Mercado sobrevendido (RSI: {rsi:.1f})")
            
            # Razões baseadas em padrões
            if 'patterns' in market_context and market_context['patterns'].get('patterns'):
                patterns = market_context['patterns'].get('patterns', [])
                if patterns:
                    pattern_str = ", ".join(patterns[:3])  # Limitar a 3 padrões
                    if len(patterns) > 3:
                        pattern_str += f" e mais {len(patterns) - 3}"
                    reasons.append(f"Padrões detectados: {pattern_str}")
            
            # Razões baseadas em sentimento
            if 'sentiment' in market_context:
                sentiment = market_context['sentiment'].get('sentiment', "neutral")
                sentiment_score = market_context['sentiment'].get('score', 0.5)
                
                if sentiment == "very_bullish":
                    reasons.append(f"Sentimento de mercado muito positivo ({sentiment_score:.1%})")
                elif sentiment == "bullish":
                    reasons.append(f"Sentimento de mercado positivo ({sentiment_score:.1%})")
                elif sentiment == "very_bearish":
                    reasons.append(f"Sentimento de mercado muito negativo ({sentiment_score:.1%})")
                elif sentiment == "bearish":
                    reasons.append(f"Sentimento de mercado negativo ({sentiment_score:.1%})")
            
            # Razões baseadas em indicadores técnicos
            if 'ema_12' in df.columns and 'ema_26' in df.columns:
                ema_short = df['ema_12'].iloc[-1]
                ema_long = df['ema_26'].iloc[-1]
                
                if ema_short > ema_long:
                    reasons.append(f"EMA 12 acima da EMA 26 (diferença: {((ema_short/ema_long)-1)*100:.2f}%)")
                elif ema_short < ema_long:
                    reasons.append(f"EMA 12 abaixo da EMA 26 (diferença: {((ema_long/ema_short)-1)*100:.2f}%)")
            
            # Limitar a 5 razões
            return reasons[:5]
            
        except Exception as e:
            logger.error(f"Erro na geração de razões para recomendação: {e}")
            return ["Análise baseada em múltiplos fatores técnicos e IA"]