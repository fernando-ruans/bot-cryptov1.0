#!/usr/bin/env python3
"""
Engine de IA para geração de sinais de trading
"""

import numpy as np
import pandas as pd
import pickle
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# Machine Learning imports
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_selection import SelectKBest, f_classif
import xgboost as xgb
import lightgbm as lgb

# Deep Learning imports
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow não disponível. Modelos de deep learning desabilitados.")

from .technical_indicators import TechnicalIndicators
from .lstm_temporal_engine import LSTMTimeSeriesAnalyzer
from .market_regime import MarketRegimeDetector
from .cross_correlation import CrossCorrelationAnalyzer

logger = logging.getLogger(__name__)

class AITradingEngine:
    """Engine principal de IA para trading"""
    
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.technical_indicators = TechnicalIndicators(config)
        self.lstm_analyzer = LSTMTimeSeriesAnalyzer(config)  # MELHORIA 4: Analisador LSTM
        self.regime_detector = MarketRegimeDetector()  # MELHORIA 6: Detector de regime
        self.correlation_analyzer = CrossCorrelationAnalyzer()  # MELHORIA 7: Analisador de correlação
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preparar features para o modelo de IA"""
        try:
            # Calcular indicadores técnicos
            df = self.technical_indicators.calculate_all_indicators(df)
            
            # Adicionar features de preço
            df = self._add_price_features(df)
            
            # Adicionar features de volume
            df = self._add_volume_features(df)
            
            # Adicionar features de volatilidade
            df = self._add_volatility_features(df)
            
            # Adicionar features temporais
            df = self._add_temporal_features(df)
            
            # Adicionar features de momentum
            df = self._add_momentum_features(df)
              # Adicionar features de padrões
            df = self._add_pattern_features(df)
              # MELHORIA 6: Adicionar features de regime de mercado
            df = self._add_regime_features(df)
            
            # MELHORIA 7: Adicionar features de correlação cruzada
            df = self._add_correlation_features(df)
            
            # Tratar valores NaN - usar forward fill seguido de backward fill
            # e depois preencher valores restantes com a mediana
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                # Forward fill (corrigido para evitar FutureWarning)
                df[col] = df[col].ffill()
                # Backward fill para valores ainda NaN no início
                df[col] = df[col].bfill()
                # Se ainda houver NaN, preencher com mediana
                if df[col].isna().any():
                    df[col] = df[col].fillna(df[col].median())
                # Se mediana for NaN (coluna vazia), preencher com 0
                if df[col].isna().any():
                    df[col] = df[col].fillna(0)
            
            logger.info(f"Features preparadas: {len(df.columns)} colunas, {len(df)} linhas")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao preparar features: {e}")
            return df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features baseadas em preço"""
        # Retornos
        for period in [1, 3, 5, 10, 20]:
            df[f'return_{period}'] = df['close'].pct_change(period)
        
        # Distância das médias móveis
        for period in [10, 20, 50]:
            if f'sma_{period}' in df.columns:
                df[f'price_sma_{period}_ratio'] = df['close'] / df[f'sma_{period}']
        
        # High-Low ratio
        df['hl_ratio'] = (df['high'] - df['low']) / df['close']
        
        # Open-Close ratio
        df['oc_ratio'] = (df['close'] - df['open']) / df['open']
        
        # Posição dentro da range
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features baseadas em volume"""
        # Volume normalizado
        df['volume_norm'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Price-Volume trend
        df['pv_trend'] = df['close'].pct_change() * df['volume_norm']
        
        # Volume momentum
        for period in [5, 10, 20]:
            df[f'volume_momentum_{period}'] = df['volume'].pct_change(period)
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features de volatilidade"""
        # Volatilidade realizada
        for period in [5, 10, 20]:
            df[f'volatility_{period}'] = df['close'].pct_change().rolling(period).std()
        
        # True Range
        df['true_range'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        
        # Volatility ratio
        df['volatility_ratio'] = df['volatility_5'] / df['volatility_20']
        
        return df
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features temporais"""
        if df.index.dtype == 'datetime64[ns]':
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek
            df['month'] = df.index.month
            
            # Sessões de trading
            df['asian_session'] = ((df['hour'] >= 0) & (df['hour'] < 8)).astype(int)
            df['european_session'] = ((df['hour'] >= 8) & (df['hour'] < 16)).astype(int)
            df['american_session'] = ((df['hour'] >= 16) & (df['hour'] < 24)).astype(int)
        
        return df
    
    def _add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features de momentum"""
        # Rate of Change para diferentes períodos
        for period in [5, 10, 20]:
            df[f'roc_{period}'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
        
        # Momentum
        for period in [5, 10, 20]:
            df[f'momentum_{period}'] = df['close'] - df['close'].shift(period)
          # Acceleration
        df['acceleration'] = df['momentum_5'] - df['momentum_5'].shift(1)
        
        return df
    
    def _add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features de padrões"""
        # Sequências de alta/baixa
        df['up_days'] = (df['close'] > df['close'].shift(1)).astype(int)
        df['down_days'] = (df['close'] < df['close'].shift(1)).astype(int)
        
        # Contagem de dias consecutivos
        df['consecutive_up'] = df['up_days'].groupby((df['up_days'] != df['up_days'].shift()).cumsum()).cumsum()
        df['consecutive_down'] = df['down_days'].groupby((df['down_days'] != df['down_days'].shift()).cumsum()).cumsum()
        
        # Gap analysis
        df['gap_up'] = (df['open'] > df['close'].shift(1)).astype(int)
        df['gap_down'] = (df['open'] < df['close'].shift(1)).astype(int)
        df['gap_size'] = abs(df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        
        # === MELHORIAS: PADRÕES DE CANDLESTICK ===
        
        # Features de padrões individuais (já calculados pelos indicadores técnicos)
        pattern_columns = [
            'hammer_advanced', 'shooting_star_advanced', 'doji_advanced',
            'bullish_engulfing_advanced', 'bearish_engulfing_advanced',
            'spinning_top', 'long_legged_doji'
        ]
        
        # Adicionar features de padrões se existirem
        for pattern in pattern_columns:
            if pattern in df.columns:
                # Padrão atual
                df[f'{pattern}_current'] = df[pattern]
                
                # Padrões recentes (últimos 3 períodos)
                df[f'{pattern}_recent'] = df[pattern].rolling(window=3).sum()
                
                # Força do padrão (baseado em volume se disponível)
                if 'volume' in df.columns:
                    volume_avg = df['volume'].rolling(window=20).mean()
                    df[f'{pattern}_strength'] = df[pattern] * (df['volume'] / volume_avg)
                else:
                    df[f'{pattern}_strength'] = df[pattern]
        
        # Features de scores consolidados
        if 'bullish_patterns_score' in df.columns:
            df['bullish_score_current'] = df['bullish_patterns_score']
            df['bullish_score_momentum'] = df['bullish_patterns_score'].diff()
            df['bullish_score_sma'] = df['bullish_patterns_score'].rolling(window=5).mean()
        
        if 'bearish_patterns_score' in df.columns:
            df['bearish_score_current'] = df['bearish_patterns_score']
            df['bearish_score_momentum'] = df['bearish_patterns_score'].diff()
            df['bearish_score_sma'] = df['bearish_patterns_score'].rolling(window=5).mean()
        
        if 'reversal_patterns_score' in df.columns:
            df['reversal_score_current'] = df['reversal_patterns_score']
            df['reversal_score_momentum'] = df['reversal_patterns_score'].diff()
            df['reversal_score_sma'] = df['reversal_patterns_score'].rolling(window=5).mean()
        
        # Features combinadas
        if 'bullish_patterns_score' in df.columns and 'bearish_patterns_score' in df.columns:
            # Saldo líquido de padrões
            df['pattern_balance'] = df['bullish_patterns_score'] - df['bearish_patterns_score']
            
            # Dominância de padrões
            total_patterns = df['bullish_patterns_score'] + df['bearish_patterns_score'] + df.get('reversal_patterns_score', 0)
            df['bullish_dominance'] = df['bullish_patterns_score'] / (total_patterns + 0.001)  # Evitar divisão por zero
            df['bearish_dominance'] = df['bearish_patterns_score'] / (total_patterns + 0.001)
            
            # Intensidade total de padrões
            df['pattern_intensity'] = total_patterns
        
        # Features de contexto de mercado baseadas em padrões
        if 'pattern_balance' in df.columns:
            # Tendência de padrões
            df['pattern_trend'] = df['pattern_balance'].rolling(window=5).mean()
            
            # Mudança de momentum de padrões
            df['pattern_momentum_change'] = df['pattern_balance'].diff()
            
            # Divergência de padrões (quando padrões contradizem preço)
            price_momentum = df['close'].pct_change(periods=3)
            df['pattern_price_divergence'] = (
                (df['pattern_balance'] > 0) & (price_momentum < 0) |
                (df['pattern_balance'] < 0) & (price_momentum > 0)
            ).astype(int)
        
        # Features de força de reversão
        if 'reversal_patterns_score' in df.columns and 'volatility_5' in df.columns:
            # Força de indecisão ponderada pela volatilidade
            df['reversal_strength'] = df['reversal_patterns_score'] * df['volatility_5']
            
            # Sinal de mudança iminente
            df['reversal_warning'] = (
                (df['reversal_patterns_score'] > 0.3) & 
                (df['volatility_5'] > df['volatility_5'].rolling(10).mean())
            ).astype(int)
        
        logger.info("✅ Features de padrões de candlestick adicionadas ao modelo de IA")
        
        return df
    
    def _add_regime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """MELHORIA 6: Adicionar features de regime de mercado"""
        try:
            logger.info("🏛️ Adicionando features de regime de mercado...")
            
            # Aplicar detecção de regimes de mercado
            df = self.regime_detector.detect_market_regimes(df)
            
            # === FEATURES DE REGIME CONSOLIDADAS ===
            
            # Scores numéricos dos regimes
            regime_scores = ['trend_regime_score', 'volatility_regime_score', 
                           'momentum_regime_score', 'ensemble_regime_score']
            
            for score_col in regime_scores:
                if score_col in df.columns:
                    # Score atual
                    df[f'{score_col}_current'] = df[score_col]
                    
                    # Mudanças de regime
                    df[f'{score_col}_change'] = df[score_col].diff()
                    
                    # Estabilidade do regime (volatilidade do score)
                    df[f'{score_col}_stability'] = df[score_col].rolling(10).std()
                    
                    # Extremos do regime (percentis)
                    rolling_window = 50
                    df[f'{score_col}_percentile'] = df[score_col].rolling(rolling_window).rank(pct=True)
            
            # === FEATURES DE TRANSIÇÃO DE REGIME ===
            
            # Probabilidades de transição (se disponíveis)
            transition_cols = [col for col in df.columns if 'transition_prob' in col]
            for col in transition_cols:
                # Suavização das probabilidades
                df[f'{col}_smooth'] = df[col].rolling(5).mean()
                
                # Mudanças abruptas de probabilidade
                df[f'{col}_shock'] = abs(df[col].diff()) > df[col].rolling(20).std() * 2
            
            # === FEATURES DE CLUSTERING E CORRELAÇÃO ===
            
            # Features de clustering se disponíveis
            if 'cluster_regime' in df.columns:
                # Estabilidade do cluster
                df['cluster_stability'] = (df['cluster_regime'] == df['cluster_regime'].shift(1)).astype(int)
                
                # Tempo no cluster atual
                df['time_in_cluster'] = df.groupby((df['cluster_regime'] != df['cluster_regime'].shift()).cumsum()).cumcount() + 1
            
            # Features de correlação se disponíveis
            if 'correlation_regime' in df.columns:
                # Força da correlação
                df['correlation_strength'] = abs(df['correlation_regime'])
                
                # Mudanças de correlação
                df['correlation_change'] = df['correlation_regime'].diff()
            
            # === FEATURES COMPOSTAS DE REGIME ===
            
            # Alinhamento entre diferentes tipos de regime
            if all(col in df.columns for col in ['trend_regime_score', 'volatility_regime_score', 'momentum_regime_score']):
                # Consenso entre regimes
                df['regime_consensus'] = (
                    df['trend_regime_score'].abs() + 
                    (df['volatility_regime_score'] - 2) +  # Normalizar volatilidade (0-4 para -2 a 2)
                    df['momentum_regime_score']
                ) / 3
                
                # Divergência entre regimes
                regime_matrix = df[['trend_regime_score', 'volatility_regime_score', 'momentum_regime_score']]
                df['regime_divergence'] = regime_matrix.std(axis=1)
            
            # === FEATURES TEMPORAIS DE REGIME ===
            
            # Persistência do regime
            if 'ensemble_regime_score' in df.columns:
                # Tempo no regime atual
                regime_changes = (df['ensemble_regime_score'].round() != df['ensemble_regime_score'].round().shift()).cumsum()
                df['time_in_regime'] = df.groupby(regime_changes).cumcount() + 1
                
                # Força do regime (distância do neutro)
                df['regime_strength'] = abs(df['ensemble_regime_score'])
                
                # Aceleração do regime
                df['regime_acceleration'] = df['ensemble_regime_score'].diff(2)
            
            # === FEATURES DE ESTABILIDADE GERAL ===
            
            # Volatilidade geral dos regimes
            regime_volatility_cols = [col for col in df.columns if 'regime' in col and 'score' in col]
            if regime_volatility_cols:
                regime_volatility = df[regime_volatility_cols].std(axis=1)
                df['overall_regime_volatility'] = regime_volatility
                
                # Mudanças abruptas no sistema de regimes
                df['regime_system_shock'] = regime_volatility > regime_volatility.rolling(20).mean() + regime_volatility.rolling(20).std() * 2
            
            logger.info("✅ Features de regime de mercado adicionadas ao modelo de IA")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar features de regime: {e}")
            return df
    
    # === MELHORIA 5: ADICIONANDO FEATURES DE SENTIMENTO DE MERCADO ===
    def _add_sentiment_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features de sentimento de mercado"""
        try:
            # === MELHORIAS: FEATURES DE SENTIMENTO DE MERCADO ===
        
            # Features de sentimento individual
            sentiment_components = [
                'fear_greed_index', 'volume_sentiment', 'volatility_sentiment',
                'momentum_sentiment', 'breakout_sentiment', 'divergence_sentiment',
                'relative_strength_sentiment'
            ]
            
            for component in sentiment_components:
                if component in df.columns:
                    # Sentimento atual
                    df[f'{component}_current'] = df[component]
                    
                    # Momentum do sentimento
                    df[f'{component}_momentum'] = df[component].diff()
                    
                    # Média móvel do sentimento
                    df[f'{component}_sma'] = df[component].rolling(window=5).mean()
                    
                    # Extremos de sentimento
                    if component != 'fear_greed_index':  # Já está normalizado
                        df[f'{component}_extreme'] = (abs(df[component]) > 0.7).astype(int)
            
            # Features de sentimento consolidado
            if 'overall_sentiment' in df.columns:
                df['sentiment_current'] = df['overall_sentiment']
                df['sentiment_momentum'] = df['overall_sentiment'].diff()
                df['sentiment_trend'] = df['overall_sentiment'].rolling(window=10).mean()
                df['sentiment_volatility'] = df['overall_sentiment'].rolling(window=10).std()
                
                # Mudanças de regime de sentimento
                df['sentiment_regime_change'] = (
                    (df['overall_sentiment'] > 0.3) & (df['overall_sentiment'].shift(1) <= 0.3) |
                    (df['overall_sentiment'] < -0.3) & (df['overall_sentiment'].shift(1) >= -0.3)
                ).astype(int)
            
            # Features de força de sentimento
            if 'sentiment_strength' in df.columns:
                df['sentiment_strength_current'] = df['sentiment_strength']
                df['sentiment_strength_momentum'] = df['sentiment_strength'].diff()
                
                # Alta convicção quando sentimento é forte
                df['sentiment_conviction'] = (df['sentiment_strength'] > 0.6).astype(int)
            
            # Features de Fear & Greed específicas
            if 'fear_greed_index' in df.columns:
                # Normalizar Fear & Greed para features
                fg_normalized = (df['fear_greed_index'] - 50) / 50
                
                # Extremos de Fear & Greed
                df['extreme_fear'] = (df['fear_greed_index'] < 25).astype(int)
                df['extreme_greed'] = (df['fear_greed_index'] > 75).astype(int)
                
                # Mudanças significativas no Fear & Greed
                fg_change = df['fear_greed_index'].diff()
                df['fg_significant_change'] = (abs(fg_change) > 10).astype(int)
            
            # Features de contradição de sentimento
            if 'momentum_sentiment' in df.columns and 'close' in df.columns:
                price_momentum = df['close'].pct_change(periods=5)
                
                # Divergência entre sentimento e preço
                df['sentiment_price_divergence'] = (
                    (df['momentum_sentiment'] > 0.3) & (price_momentum < -0.02) |
                    (df['momentum_sentiment'] < -0.3) & (price_momentum > 0.02)
                ).astype(int)
            
            logger.info("✅ Features de sentimento de mercado adicionadas ao modelo de IA")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao adicionar features de sentimento: {e}")
            return df
    
    def create_labels(self, df: pd.DataFrame, lookahead_periods: int = 24) -> pd.Series:
        """Criar labels para treinamento"""
        try:
            # Calcular retorno futuro
            future_return = df['close'].shift(-lookahead_periods) / df['close'] - 1
            
            # Definir thresholds
            buy_threshold = 0.02   # 2% de alta
            sell_threshold = -0.02 # 2% de queda
            
            # Criar labels
            labels = pd.Series(index=df.index, dtype=int)
            labels[future_return > buy_threshold] = 1   # Buy signal
            labels[future_return < sell_threshold] = -1 # Sell signal
            labels[(future_return >= sell_threshold) & (future_return <= buy_threshold)] = 0  # Hold            
            return labels
            
        except Exception as e:
            logger.error(f"Erro ao criar labels: {e}")
            return pd.Series(index=df.index, dtype=int)
    
    # === MELHORIA 4: MÉTODOS LSTM INTEGRADOS ===
            logger.info("�️ Iniciando análise temporal LSTM...")
            lstm_result = self.lstm_analyzer.analyze_temporal_patterns(df, symbol)
            
            if lstm_result['success']:
                logger.info(f"✅ LSTM treinado: Trend={lstm_result['trend_strength']:.3f}, "
                          f"Momentum={lstm_result['momentum_score']:.3f}")
                
                # Adicionar métricas LSTM aos resultados
                results['lstm_analysis'] = {
                    'trend_strength': lstm_result['trend_strength'],
                    'momentum_score': lstm_result['momentum_score'],
                    'volatility_forecast': lstm_result['volatility_forecast'],
                    'next_prediction': lstm_result['next_prediction'],
                    'features_used': lstm_result['features_used']
                }
            else:
                logger.warning(f"⚠️ LSTM não pôde ser treinado: {lstm_result.get('message', 'Erro desconhecido')}")
                results['lstm_analysis'] = None
            
            # Salvar modelos
            self.lstm_models[symbol] = lstm_models
            
            logger.info(f"🎯 Treinamento LSTM concluído para {symbol}")
            
            return {
                'models': lstm_models,
                'evaluations': evaluations,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento LSTM: {e}")
            return {'models': {}, 'evaluations': {}, 'success': False}
    
    def get_lstm_predictions(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Obter previsões dos modelos LSTM"""
        try:
            if symbol not in self.lstm_models:
                logger.warning(f"⚠️ Modelos LSTM não treinados para {symbol}")
                return {}
            
            predictions = {}
            price_data = df['close'].values
            
            # Obter previsões de cada modelo
            for term, model in self.lstm_models[symbol].items():
                try:
                    # Fazer previsões
                    if term == 'short_term':
                        steps = 5
                    elif term == 'medium_term':
                        steps = 15
                    else:  # long_term
                        steps = 30
                    
                    pred = model.predict(price_data, steps_ahead=steps)
                    
                    if len(pred) > 0:
                        predictions[term] = {
                            'values': pred,
                            'direction': 'up' if pred[-1] > price_data[-1] else 'down',
                            'confidence': min(abs(pred[-1] - price_data[-1]) / price_data[-1] * 10, 1.0),
                            'steps_ahead': steps
                        }
                    
                except Exception as e:
                    logger.error(f"❌ Erro na previsão LSTM {term}: {e}")
                    continue
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter previsões LSTM: {e}")
            return {}
    
    def _add_lstm_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Adicionar features baseadas em previsões LSTM"""
        try:
            # Obter previsões LSTM
            lstm_predictions = self.get_lstm_predictions(df, symbol)
            
            if not lstm_predictions:
                logger.info("⚠️ Nenhuma previsão LSTM disponível")
                return df
            
            # Adicionar features de previsão
            for term, pred_data in lstm_predictions.items():
                # Direção da previsão
                df[f'lstm_{term}_direction'] = 1 if pred_data['direction'] == 'up' else -1
                
                # Confiança da previsão
                df[f'lstm_{term}_confidence'] = pred_data['confidence']
                
                # Magnitude da mudança prevista
                current_price = df['close'].iloc[-1]
                predicted_price = pred_data['values'][-1] if len(pred_data['values']) > 0 else current_price
                change_magnitude = abs(predicted_price - current_price) / current_price
                df[f'lstm_{term}_magnitude'] = change_magnitude
                
                # Força do sinal LSTM
                df[f'lstm_{term}_signal_strength'] = pred_data['confidence'] * change_magnitude
            
            # Features consolidadas
            if len(lstm_predictions) >= 2:
                # Consenso entre modelos
                directions = [pred['direction'] for pred in lstm_predictions.values()]
                consensus = 1 if directions.count('up') > directions.count('down') else -1
                df['lstm_consensus'] = consensus
                
                # Confiança média
                confidences = [pred['confidence'] for pred in lstm_predictions.values()]
                df['lstm_avg_confidence'] = np.mean(confidences)
                
                # Força combinada
                strengths = [pred['confidence'] * 
                           (1 if pred['direction'] == 'up' else -1) 
                           for pred in lstm_predictions.values()]
                df['lstm_combined_strength'] = np.mean(strengths)
            
            logger.info("✅ Features LSTM adicionadas ao modelo")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar features LSTM: {e}")
            return df
        
    def _add_temporal_lstm_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adicionar features temporais avançadas para LSTM"""
        try:
            from .lstm_engine import TimeSeriesFeatureExtractor
            df = TimeSeriesFeatureExtractor.create_temporal_features(df, target_col='close')
            logger.info("✅ Features temporais LSTM adicionadas ao pipeline de IA")
            return df
        except Exception as e:
            logger.error(f"Erro ao adicionar features temporais LSTM: {e}")
            return df

    def train_lstm_model(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Treinar modelo LSTM para previsão de séries temporais"""
        try:
            from .lstm_engine import SimpleLSTM
            
            logger.info(f"🧠 Iniciando treinamento LSTM para {symbol}")
            
            # Preparar dados de preço
            price_data = df['close'].values
            
            if len(price_data) < 100:
                logger.warning("❌ Dados insuficientes para treinar LSTM")
                return {'model': None, 'accuracy': 0, 'predictions': None}
            
            # Dividir dados em treino e teste
            train_size = int(len(price_data) * 0.8)
            train_data = price_data[:train_size]
            test_data = price_data[train_size:]
            
            # Criar e treinar modelo LSTM
            lstm_model = SimpleLSTM(
                input_size=1,
                hidden_size=50,
                num_layers=1,
                sequence_length=60
            )
            
            # Treinar modelo
            lstm_model.fit(train_data, epochs=50, learning_rate=0.001)
            
            # Avaliar modelo
            evaluation = lstm_model.evaluate(test_data)
            
            # Fazer previsões para próximos períodos
            predictions = lstm_model.predict(price_data, steps_ahead=5)
            
            # Salvar modelo
            model_key = f'lstm_{symbol}'
            self.models[model_key] = lstm_model
            
            logger.info(f"✅ LSTM treinado para {symbol}: Accuracy={evaluation['directional_accuracy']:.3f}")
            
            return {
                'model': lstm_model,
                'accuracy': evaluation['directional_accuracy'],
                'predictions': predictions,
                'evaluation': evaluation,
                'mse': evaluation['mse'],
                'mae': evaluation['mae']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento LSTM: {e}")
            return {'model': None, 'accuracy': 0, 'predictions': None}

    def predict_with_lstm(self, df: pd.DataFrame, symbol: str, steps_ahead: int = 1) -> np.ndarray:
        """Fazer previsões usando modelo LSTM"""
        try:
            model_key = f'lstm_{symbol}'
            
            if model_key not in self.models or self.models[model_key] is None:
                logger.warning(f"❌ Modelo LSTM não encontrado para {symbol}")
                return np.array([])
            
            lstm_model = self.models[model_key]
            price_data = df['close'].values
            
            predictions = lstm_model.predict(price_data, steps_ahead=steps_ahead)
            
            logger.info(f"🔮 LSTM predição para {symbol}: próximos {steps_ahead} valores")
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Erro na previsão LSTM: {e}")
            return np.array([])

    def get_lstm_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Gerar sinal de trading baseado em LSTM"""
        try:
            # Fazer previsão LSTM
            predictions = self.predict_with_lstm(df, symbol, steps_ahead=3)
            
            if len(predictions) == 0:
                return {'signal': 0, 'confidence': 0.0, 'price_target': None}
            
            current_price = df['close'].iloc[-1]
            next_prediction = predictions[0]
            
            # Calcular mudança percentual esperada
            price_change = (next_prediction - current_price) / current_price
            
            # Gerar sinal baseado na mudança esperada
            if price_change > 0.01:  # 1% de alta
                signal = 1
                confidence = min(abs(price_change) * 10, 1.0)
            elif price_change < -0.01:  # 1% de baixa
                signal = -1
                confidence = min(abs(price_change) * 10, 1.0)
            else:
                signal = 0
                confidence = 0.5
            
            return {
                'signal': signal,
                'confidence': confidence,
                'price_target': next_prediction,
                'price_change': price_change,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar sinal LSTM: {e}")
            return {'signal': 0, 'confidence': 0.0, 'price_target': None}
    
    def _add_correlation_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """MELHORIA 7: Adicionar features de correlação cruzada"""
        try:
            logger.info("🔗 Adicionando features de correlação cruzada...")
            
            # Para features de correlação cruzada, precisamos dos dados de outros ativos
            # Por enquanto, vamos trabalhar com as features existentes de correlation_regime
            # que podem vir de análises anteriores ou de fonte externa
            
            # === FEATURES DE CORRELAÇÃO EXISTENTES ===
              # Features de correlação se disponíveis (vindas de análise externa)
            if 'correlation_regime' in df.columns:
                logger.info("📊 Processando features de correlação existentes...")
                
                # Verificar se correlation_regime é numérico ou categórico
                if pd.api.types.is_numeric_dtype(df['correlation_regime']):
                    # Numérico: pode calcular features diretamente
                    df['correlation_strength'] = abs(df['correlation_regime'])
                    
                    # Mudanças de correlação
                    df['correlation_change'] = df['correlation_regime'].diff()
                    df['correlation_change_abs'] = abs(df['correlation_change'])
                    
                    # Aceleração da correlação
                    df['correlation_acceleration'] = df['correlation_change'].diff()
                    
                    # === CLASSIFICAÇÃO DE REGIME DE CORRELAÇÃO ===
                    
                    # Regime categórico baseado em thresholds
                    correlation_abs = df['correlation_strength']
                    df['correlation_class_numeric'] = 0  # Medium por padrão
                    df.loc[correlation_abs < 0.3, 'correlation_class_numeric'] = -1  # Low
                    df.loc[correlation_abs > 0.7, 'correlation_class_numeric'] = 1   # High
                    
                else:
                    # Categórico: converter para numérico primeiro
                    logger.info("🔤 correlation_regime é categórico, convertendo...")
                    
                    # Mapear strings para valores numéricos
                    correlation_map = {
                        'Low': 0.2, 'Low Correlation': 0.2,
                        'Medium': 0.5, 'Medium Correlation': 0.5,
                        'High': 0.8, 'High Correlation': 0.8
                    }
                    
                    # Tentar mapear, senão usar valor padrão
                    df['correlation_regime_numeric'] = df['correlation_regime'].map(correlation_map)
                    df['correlation_regime_numeric'] = df['correlation_regime_numeric'].fillna(0.5)
                    
                    # Usar versão numérica para features
                    df['correlation_strength'] = df['correlation_regime_numeric']
                    df['correlation_change'] = df['correlation_regime_numeric'].diff()
                    df['correlation_change_abs'] = abs(df['correlation_change'])
                    df['correlation_acceleration'] = df['correlation_change'].diff()
                    
                    # Classificação baseada nos valores mapeados
                    df['correlation_class_numeric'] = 0  # Medium por padrão
                    df.loc[df['correlation_regime_numeric'] < 0.3, 'correlation_class_numeric'] = -1  # Low
                    df.loc[df['correlation_regime_numeric'] > 0.7, 'correlation_class_numeric'] = 1   # High
                  # === FEATURES TEMPORAIS DE CORRELAÇÃO ===
                
                # Usar versão numérica para cálculos
                correlation_numeric = df.get('correlation_regime_numeric', df.get('correlation_regime', pd.Series([0.5] * len(df), index=df.index)))
                
                # Estabilidade da correlação (inverso da volatilidade)
                correlation_volatility = correlation_numeric.rolling(20).std()
                df['correlation_stability'] = 1 / (1 + correlation_volatility.fillna(1))
                
                # Persistência da correlação (tempo no regime atual)
                correlation_regime_changes = (df['correlation_class_numeric'] != df['correlation_class_numeric'].shift()).cumsum()
                df['time_in_correlation_regime'] = df.groupby(correlation_regime_changes).cumcount() + 1
                  # === FEATURES DE BREAKDOWN DE CORRELAÇÃO ===
                
                # Detecção de breakdowns (mudanças abruptas)
                correlation_rolling_std = correlation_numeric.rolling(20).std()
                threshold = correlation_rolling_std * 2
                df['correlation_breakdown'] = abs(df['correlation_change']) > threshold
                
                # Intensidade do breakdown
                df['correlation_breakdown_intensity'] = abs(df['correlation_change']) / correlation_rolling_std.fillna(1)
                
                # === FEATURES DE CONVERGÊNCIA/DIVERGÊNCIA ===
                
                # Média móvel da correlação (tendência)
                df['correlation_ma_short'] = correlation_numeric.rolling(5).mean()
                df['correlation_ma_long'] = correlation_numeric.rolling(20).mean()
                
                # Divergência entre correlação atual e média móvel
                df['correlation_trend_divergence'] = correlation_numeric - df['correlation_ma_long']
                
                # Momentum da correlação
                df['correlation_momentum'] = df['correlation_ma_short'] - df['correlation_ma_long']
                
                # === FEATURES ESTATÍSTICAS DE CORRELAÇÃO ===
                
                # Percentil da correlação (posição relativa)
                df['correlation_percentile'] = correlation_numeric.rolling(100).rank(pct=True)
                
                # Z-score da correlação
                correlation_mean = correlation_numeric.rolling(50).mean()
                correlation_std = correlation_numeric.rolling(50).std()
                df['correlation_zscore'] = (correlation_numeric - correlation_mean) / correlation_std.fillna(1)
                
                # === FEATURES DE EXTREMOS ===
                
                # Extremos de correlação
                df['correlation_at_extreme'] = (
                    (df['correlation_percentile'] < 0.1) | 
                    (df['correlation_percentile'] > 0.9)
                ).astype(int)
                
                # Reversão de extremos
                df['correlation_reversal_signal'] = (
                    (df['correlation_at_extreme'] == 1) & 
                    (df['correlation_change'].shift(1) * df['correlation_change'] < 0)
                ).astype(int)
                
                logger.info("✅ Features de correlação processadas")
            else:
                logger.info("⚠️ Nenhuma feature de correlação_regime encontrada")
                
                # === FEATURES PLACEHOLDER ===
                # Adicionar features placeholder para manter consistência
                df['correlation_strength'] = 0.5  # Correlação neutra
                df['correlation_change'] = 0.0
                df['correlation_class_numeric'] = 0
                df['correlation_stability'] = 1.0
                df['correlation_breakdown'] = False
                
            # === FEATURES DERIVADAS ADICIONAIS ===
            
            # Interação correlação-volatilidade
            if 'volatility' in df.columns:
                df['correlation_volatility_interaction'] = df['correlation_strength'] * df['volatility']
            
            # Interação correlação-volume
            if 'volume_ratio' in df.columns:
                df['correlation_volume_interaction'] = df['correlation_strength'] * df['volume_ratio']
              # Interação correlação-momentum
            if 'momentum_score' in df.columns:
                correlation_value = df.get('correlation_regime_numeric', df.get('correlation_regime', 0.5))
                df['correlation_momentum_interaction'] = correlation_value * df['momentum_score']
                
            logger.info("✅ Features de correlação cruzada adicionadas ao modelo de IA")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar features de correlação: {e}")
            return df
        
    def add_cross_correlation_data(self, df: pd.DataFrame, symbol: str, all_market_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        MELHORIA 7: Integrar dados de correlação cruzada de múltiplos ativos ao DataFrame principal
        
        Args:
            df: DataFrame principal do ativo
            symbol: Símbolo do ativo principal
            all_market_data: Dicionário com dados de todos os ativos {símbolo: DataFrame}
        
        Returns:
            DataFrame com features de correlação cruzada adicionadas
        """
        try:
            logger.info(f"🔗 Integrando correlação cruzada para {symbol}...")
            
            # Verificar se temos dados suficientes
            if len(all_market_data) < 2:
                logger.warning("Dados insuficientes para análise de correlação cruzada")
                return df
            
            # Obter features de correlação
            correlation_features = self.correlation_analyzer.get_correlation_features(
                all_market_data, 
                base_symbol='BTCUSDT'
            )
            
            # Se o símbolo atual tem features de correlação, integrar ao DataFrame
            if symbol in correlation_features:
                features_df = correlation_features[symbol]
                
                # Alinhar índices e integrar features
                df = df.copy()
                
                # Merge das features de correlação
                correlation_cols = features_df.columns
                for col in correlation_cols:
                    if col not in df.columns:  # Evitar sobrescrever colunas existentes
                        df[col] = features_df[col].reindex(df.index)
                
                logger.info(f"✅ Features de correlação integradas para {symbol}: {list(correlation_cols)}")
            else:
                logger.info(f"⚠️ Nenhuma feature de correlação disponível para {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao integrar correlação cruzada para {symbol}: {e}")
            return df
            
    def get_correlation_summary_for_symbol(self, symbol: str, all_market_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Obter resumo de correlação para um símbolo específico
        """
        try:
            summary = self.correlation_analyzer.get_correlation_summary(all_market_data)
            symbol_key = f'{symbol}_vs_BTC'
            
            if symbol_key in summary:
                return summary[symbol_key]
            else:
                return {
                    'mean_correlation': 0.0,
                    'current_correlation': 0.0,
                    'high_correlation_pct': 0.0
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter resumo de correlação para {symbol}: {e}")
            return {}
    
    def load_models(self):
        """Carregar modelos salvos"""
        try:
            import os
            model_dir = getattr(self.config, 'AI_MODEL_PATH', 'models')
            
            if not os.path.exists(model_dir):
                logger.info("Diretório de modelos não encontrado")
                return
            
            # Carregar modelos para cada símbolo
            symbols = getattr(self.config, 'CRYPTO_PAIRS', ['BTCUSDT', 'ETHUSDT'])
            
            for symbol in symbols:
                model_path = os.path.join(model_dir, f"{symbol}_models.pkl")
                scaler_path = os.path.join(model_dir, f"{symbol}_scaler.pkl")
                selector_path = os.path.join(model_dir, f"{symbol}_selector.pkl")
                
                if os.path.exists(model_path):
                    try:
                        self.models[symbol] = joblib.load(model_path)
                        
                        if os.path.exists(scaler_path):
                            self.scalers[symbol] = joblib.load(scaler_path)
                        
                        if os.path.exists(selector_path):
                            self.feature_selectors[symbol] = joblib.load(selector_path)
                        
                        # Carregar neural network se disponível
                        nn_path = os.path.join(model_dir, f"{symbol}_neural_network.h5")
                        if os.path.exists(nn_path) and TENSORFLOW_AVAILABLE:
                            nn_model = load_model(nn_path)
                            if symbol not in self.models:
                                self.models[symbol] = {}
                            self.models[symbol]['neural_network'] = {
                                'model': nn_model,
                                'accuracy': 0.8  # Placeholder
                            }
                        
                        logger.info(f"✅ Modelos carregados para {symbol}")
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao carregar modelos para {symbol}: {e}")
            
            if self.models:
                self.is_trained = True
                logger.info("✅ Modelos carregados com sucesso")
            else:
                logger.info("⚠️ Nenhum modelo encontrado - sistema funcionará com features apenas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelos: {e}")
    
    def predict_signal(self, df: pd.DataFrame, symbol: str = None) -> Dict:
        """
        Método principal para gerar sinais de trading usando a IA
        
        Args:
            df: DataFrame com dados de mercado e features
            symbol: Símbolo do ativo (opcional)
        
        Returns:
            Dicionário com sinal de trading e confiança
        """
        try:
            logger.info(f"🧠 Gerando sinal de IA para {symbol or 'ativo'}...")
            
            # Preparar features se ainda não estão preparadas
            if len(df.columns) < 50:  # Se tem poucas colunas, precisa preparar features
                df = self.prepare_features(df)
            
            # Verificar se temos dados suficientes
            if len(df) < 50:
                logger.warning(f"Dados insuficientes para previsão: {len(df)} períodos")
                return {
                    'signal': 'hold',
                    'confidence': 0.5,
                    'reason': 'Dados insuficientes',
                    'ai_features': 0
                }
            
            # Usar apenas as últimas features (período mais recente)
            latest_features = df.iloc[-1]
            
            # === ANÁLISE BASEADA EM FEATURES ===
            
            # 1. Análise de momentum
            momentum_signals = []
            if 'momentum_5' in latest_features:
                momentum_signals.append(1 if latest_features['momentum_5'] > 0 else -1)
            if 'roc_5' in latest_features:
                momentum_signals.append(1 if latest_features['roc_5'] > 2 else -1 if latest_features['roc_5'] < -2 else 0)
            
            # 2. Análise de padrões
            pattern_signals = []
            if 'bullish_patterns_score' in latest_features and 'bearish_patterns_score' in latest_features:
                pattern_balance = latest_features['bullish_patterns_score'] - latest_features['bearish_patterns_score']
                pattern_signals.append(1 if pattern_balance > 0.3 else -1 if pattern_balance < -0.3 else 0)
            
            # 3. Análise de regime de mercado
            regime_signals = []
            if 'ensemble_regime_score' in latest_features:
                regime_score = latest_features['ensemble_regime_score']
                regime_signals.append(1 if regime_score > 1 else -1 if regime_score < -1 else 0)
            
            # 4. Análise de correlação (MELHORIA 7)
            correlation_signals = []
            if 'correlation_strength' in latest_features:
                corr_strength = latest_features['correlation_strength']
                if 'correlation_trend_divergence' in latest_features:
                    corr_divergence = latest_features['correlation_trend_divergence']
                    # Sinal baseado na força e direção da correlação
                    if corr_strength > 0.7 and corr_divergence > 0:
                        correlation_signals.append(1)  # Alta correlação + divergência positiva
                    elif corr_strength > 0.7 and corr_divergence < 0:
                        correlation_signals.append(-1)  # Alta correlação + divergência negativa
                    else:
                        correlation_signals.append(0)
            
            # 5. Análise de volatilidade
            volatility_signals = []
            if 'volatility_ratio' in latest_features:
                vol_ratio = latest_features['volatility_ratio']
                # Sinal baseado em volatilidade (alta vol = incerteza = hold)
                volatility_signals.append(0 if vol_ratio > 2 else 1 if vol_ratio < 0.5 else 0)
            
            # === CONSOLIDAÇÃO DOS SINAIS ===
            
            all_signals = []
            all_signals.extend(momentum_signals)
            all_signals.extend(pattern_signals)
            all_signals.extend(regime_signals)
            all_signals.extend(correlation_signals)
            all_signals.extend(volatility_signals)
            
            # Remover sinais neutros para calcular consenso
            active_signals = [s for s in all_signals if s != 0]
            
            if not active_signals:
                # Nenhum sinal ativo
                signal = 'hold'
                confidence = 0.5
                reason = 'Sinais neutros'
            else:
                # Calcular consenso
                bullish_count = sum(1 for s in active_signals if s > 0)
                bearish_count = sum(1 for s in active_signals if s < 0)
                total_active = len(active_signals)
                
                # Determinar sinal principal
                if bullish_count > bearish_count:
                    signal = 'buy'
                    confidence = min(0.95, 0.5 + (bullish_count / total_active) * 0.4)
                    reason = f'Consenso bullish ({bullish_count}/{total_active})'
                elif bearish_count > bullish_count:
                    signal = 'sell'
                    confidence = min(0.95, 0.5 + (bearish_count / total_active) * 0.4)
                    reason = f'Consenso bearish ({bearish_count}/{total_active})'
                else:
                    signal = 'hold'
                    confidence = 0.5
                    reason = 'Sinais divididos'
            
            # === AJUSTES DE CONFIANÇA ===
            
            # Reduzir confiança se volatilidade muito alta
            if 'volatility_ratio' in latest_features:
                if latest_features['volatility_ratio'] > 3:
                    confidence *= 0.7
                    reason += ' (vol alta)'
            
            # Aumentar confiança se múltiplas features concordam
            feature_count = len([col for col in latest_features.index if not pd.isna(latest_features[col])])
            if feature_count > 100:
                confidence = min(0.95, confidence * 1.1)
            
            result = {
                'signal': signal,
                'confidence': round(confidence, 3),
                'reason': reason,
                'ai_features': feature_count,
                'signals_breakdown': {
                    'momentum': momentum_signals,
                    'patterns': pattern_signals,
                    'regime': regime_signals,
                    'correlation': correlation_signals,
                    'volatility': volatility_signals
                }
            }
            
            logger.info(f"✅ Sinal gerado: {signal} (confiança: {confidence:.3f}) - {reason}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de sinal de IA: {e}")
            return {
                'signal': 'hold',
                'confidence': 0.5,
                'reason': f'Erro: {str(e)}',
                'ai_features': 0
            }