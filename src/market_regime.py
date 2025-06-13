#!/usr/bin/env python3
"""
MELHORIA 6: Detecção de Regime de Mercado
Implementa algoritmos para identificar automaticamente regimes de mercado
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MarketRegimeDetector:
    """Detector de regimes de mercado usando múltiplas metodologias"""
    
    def __init__(self):
        self.regime_history = []
        self.regime_models = {}
        self.scaler = StandardScaler()
        
    def detect_market_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detectar regimes de mercado usando múltiplas metodologias"""
        try:
            logger.info("🏛️ Detectando regimes de mercado...")
            
            # 1. Detecção baseada em tendência
            df = self._detect_trend_regimes(df)
            
            # 2. Detecção baseada em volatilidade
            df = self._detect_volatility_regimes(df)
            
            # 3. Detecção baseada em momentum
            df = self._detect_momentum_regimes(df)
            
            # 4. Detecção baseada em clustering
            df = self._detect_clustering_regimes(df)
            
            # 5. Detecção baseada em correlações
            df = self._detect_correlation_regimes(df)
            
            # 6. Regime consolidado usando ensemble
            df = self._calculate_ensemble_regime(df)
            
            # 7. Métricas de estabilidade do regime
            df = self._calculate_regime_stability(df)
            
            # 8. Probabilidades de transição
            df = self._calculate_transition_probabilities(df)
            
            logger.info("✅ Regimes de mercado detectados")
            return df
            
        except Exception as e:
            logger.error(f"Erro na detecção de regimes: {e}")
            return df
    
    def _detect_trend_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detectar regimes baseados em tendência"""
        try:
            if 'close' not in df.columns:
                df['trend_regime'] = 'Unknown'
                return df
            
            # Múltiplas médias móveis para detecção de tendência
            periods = [20, 50, 200]
            ma_signals = []
            
            for period in periods:
                if len(df) > period:
                    df[f'sma_{period}'] = df['close'].rolling(period).mean()
                    # Sinal: preço acima/abaixo da média
                    signal = np.where(df['close'] > df[f'sma_{period}'], 1, -1)
                    ma_signals.append(signal)
            
            # Slope das médias móveis
            slopes = []
            for period in periods:
                if f'sma_{period}' in df.columns:
                    slope = df[f'sma_{period}'].diff(5) / df[f'sma_{period}']
                    slopes.append(slope)
            
            # Combinar sinais
            if ma_signals:
                ma_consensus = np.mean(ma_signals, axis=0)
                slope_consensus = np.mean(slopes, axis=0) if slopes else np.zeros(len(df))
                  # Classificar regime de tendência
                trend_regime = []
                for i in range(len(df)):
                    ma_val = ma_consensus[i] if i < len(ma_consensus) else 0
                    slope_val = slope_consensus[i] if i < len(slope_consensus) else 0
                    
                    if ma_val > 0.5 and slope_val > 0.001:
                        regime = 'Strong Uptrend'
                    elif ma_val > 0 and slope_val > 0:
                        regime = 'Uptrend'
                    elif ma_val < -0.5 and slope_val < -0.001:
                        regime = 'Strong Downtrend'
                    elif ma_val < 0 and slope_val < 0:
                        regime = 'Downtrend'
                    else:
                        regime = 'Sideways'
                    
                    trend_regime.append(regime)
                
                df['trend_regime'] = trend_regime
            else:
                df['trend_regime'] = 'Unknown'
            
            # Score numérico do regime de tendência
            regime_scores = {
                'Strong Uptrend': 2, 'Uptrend': 1, 'Sideways': 0,
                'Downtrend': -1, 'Strong Downtrend': -2, 'Unknown': 0
            }
            df['trend_regime_score'] = df['trend_regime'].map(regime_scores)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro na detecção de regime de tendência: {e}")
            df['trend_regime'] = 'Unknown'
            df['trend_regime_score'] = 0
            return df
    
    def _detect_volatility_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detectar regimes baseados em volatilidade"""
        try:
            if 'close' not in df.columns:
                df['volatility_regime'] = 'Unknown'
                return df
            
            # Calcular volatilidade realizada
            returns = df['close'].pct_change()
            
            # Múltiplas janelas de volatilidade
            vol_windows = [5, 10, 20, 50]
            volatilities = {}
            
            for window in vol_windows:
                vol = returns.rolling(window).std() * np.sqrt(24)  # Anualizar (assumindo dados horários)
                volatilities[f'vol_{window}'] = vol
                df[f'volatility_{window}h'] = vol
            
            # Percentis de volatilidade para classificação
            vol_20 = volatilities['vol_20']
            vol_percentiles = vol_20.rolling(100).quantile([0.2, 0.4, 0.6, 0.8])
              # Classificar regime de volatilidade
            volatility_regime = []
            for i, vol in enumerate(vol_20):
                if pd.isna(vol):
                    regime = 'Unknown'
                elif i < 100:
                    # Usar percentis globais para início da série
                    percentiles = vol_20.quantile([0.2, 0.4, 0.6, 0.8])
                    p20, p40, p60, p80 = percentiles.iloc[0], percentiles.iloc[1], percentiles.iloc[2], percentiles.iloc[3]
                else:
                    # Usar percentis móveis
                    recent_vol = vol_20.iloc[max(0, i-100):i]
                    percentiles = recent_vol.quantile([0.2, 0.4, 0.6, 0.8])
                    p20, p40, p60, p80 = percentiles.iloc[0], percentiles.iloc[1], percentiles.iloc[2], percentiles.iloc[3]
                
                if vol <= p20:
                    regime = 'Very Low Vol'
                elif vol <= p40:
                    regime = 'Low Vol'
                elif vol <= p60:
                    regime = 'Normal Vol'
                elif vol <= p80:
                    regime = 'High Vol'
                else:
                    regime = 'Very High Vol'
                
                volatility_regime.append(regime)
            
            df['volatility_regime'] = volatility_regime
            
            # Score numérico da volatilidade
            vol_scores = {
                'Very Low Vol': 0, 'Low Vol': 1, 'Normal Vol': 2,
                'High Vol': 3, 'Very High Vol': 4, 'Unknown': 2
            }
            df['volatility_regime_score'] = df['volatility_regime'].map(vol_scores)
            
            # Regime de clustering de volatilidade
            df = self._detect_volatility_clustering(df, returns)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro na detecção de regime de volatilidade: {e}")
            df['volatility_regime'] = 'Unknown'
            df['volatility_regime_score'] = 2
            return df
    
    def _detect_volatility_clustering(self, df: pd.DataFrame, returns: pd.Series) -> pd.DataFrame:
        """Detectar clustering de volatilidade (períodos de alta/baixa vol persistente)"""
        try:
            # GARCH-like analysis
            vol_5 = returns.rolling(5).std()
            vol_20 = returns.rolling(20).std()
            
            # Persistence of volatility
            vol_ratio = vol_5 / (vol_20 + 0.001)
            vol_persistence = vol_ratio.rolling(10).std()
            
            # Clustering score
            clustering_score = []
            for i in range(len(vol_persistence)):
                if pd.isna(vol_persistence.iloc[i]):
                    clustering_score.append(0)
                else:
                    # Alta persistência = baixo clustering, baixa persistência = alto clustering
                    score = 1 / (1 + vol_persistence.iloc[i])
                    clustering_score.append(score)
            
            df['volatility_clustering'] = clustering_score
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no clustering de volatilidade: {e}")
            df['volatility_clustering'] = 0.5
            return df
    
    def _detect_momentum_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detectar regimes baseados em momentum"""
        try:
            momentum_indicators = []
            
            # RSI momentum
            if 'rsi' in df.columns:
                rsi_momentum = (df['rsi'] - 50) / 50
                momentum_indicators.append(rsi_momentum)
            
            # MACD momentum
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                macd_momentum = np.tanh((df['macd'] - df['macd_signal']) * 10)
                momentum_indicators.append(macd_momentum)
            
            # Price momentum múltiplos timeframes
            if 'close' in df.columns:
                for period in [5, 10, 20, 50]:
                    price_mom = df['close'].pct_change(period)
                    momentum_indicators.append(np.tanh(price_mom * 100))
            
            # Rate of Change
            if 'close' in df.columns:
                roc = (df['close'] / df['close'].shift(10) - 1) * 100
                momentum_indicators.append(np.tanh(roc / 10))
            
            # Combinar momentum
            if momentum_indicators:
                momentum_score = np.mean(momentum_indicators, axis=0)
                
                # Classificar regime de momentum
                momentum_regime = []
                for score in momentum_score:
                    if pd.isna(score):
                        regime = 'Unknown'
                    elif score > 0.5:
                        regime = 'Strong Bullish'
                    elif score > 0.2:
                        regime = 'Bullish'
                    elif score > -0.2:
                        regime = 'Neutral'
                    elif score > -0.5:
                        regime = 'Bearish'
                    else:
                        regime = 'Strong Bearish'
                    
                    momentum_regime.append(regime)
                
                df['momentum_regime'] = momentum_regime
                df['momentum_regime_score'] = momentum_score
            else:
                df['momentum_regime'] = 'Unknown'
                df['momentum_regime_score'] = 0
            
            return df
            
        except Exception as e:
            logger.error(f"Erro na detecção de regime de momentum: {e}")
            df['momentum_regime'] = 'Unknown'
            df['momentum_regime_score'] = 0
            return df
    
    def _detect_clustering_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detectar regimes usando clustering K-means"""
        try:
            # Features para clustering
            features = []
            feature_names = []
            
            if 'close' in df.columns:
                # Returns múltiplos timeframes
                for period in [1, 5, 10, 20]:
                    returns = df['close'].pct_change(period)
                    features.append(returns.fillna(0))
                    feature_names.append(f'returns_{period}')
                
                # Volatilidade
                vol = df['close'].pct_change().rolling(20).std()
                features.append(vol.fillna(vol.mean()))
                feature_names.append('volatility')
            
            # Volume se disponível
            if 'volume' in df.columns:
                volume_norm = df['volume'] / df['volume'].rolling(50).mean()
                features.append(volume_norm.fillna(1))
                feature_names.append('volume_norm')
            
            # RSI se disponível
            if 'rsi' in df.columns:
                rsi_norm = (df['rsi'] - 50) / 50
                features.append(rsi_norm.fillna(0))
                feature_names.append('rsi_norm')
            
            if len(features) >= 3:
                # Criar matriz de features
                feature_matrix = np.column_stack(features)
                
                # Remover linhas com NaN
                mask = ~np.isnan(feature_matrix).any(axis=1)
                clean_features = feature_matrix[mask]
                
                if len(clean_features) > 10:
                    # Normalizar features
                    scaled_features = self.scaler.fit_transform(clean_features)
                    
                    # K-means clustering (4 regimes)
                    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
                    clusters = kmeans.fit_predict(scaled_features)
                    
                    # Mapear clusters de volta para DataFrame
                    cluster_labels = np.full(len(df), -1)  # -1 para dados faltantes
                    cluster_labels[mask] = clusters
                    
                    # Interpretar clusters baseado nas características
                    cluster_interpretations = self._interpret_clusters(
                        scaled_features, clusters, feature_names
                    )
                    
                    # Mapear para nomes de regime
                    regime_names = [cluster_interpretations.get(c, f'Regime_{c}') 
                                  for c in cluster_labels]
                    
                    df['clustering_regime'] = regime_names
                    df['clustering_regime_id'] = cluster_labels
                else:
                    df['clustering_regime'] = 'Insufficient Data'
                    df['clustering_regime_id'] = -1
            else:
                df['clustering_regime'] = 'Insufficient Features'
                df['clustering_regime_id'] = -1
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no clustering de regimes: {e}")
            df['clustering_regime'] = 'Error'
            df['clustering_regime_id'] = -1
            return df
    
    def _interpret_clusters(self, features: np.ndarray, clusters: np.ndarray, feature_names: List[str]) -> Dict[int, str]:
        """Interpretar clusters baseado nas características médias"""
        try:
            interpretations = {}
            
            for cluster_id in np.unique(clusters):
                cluster_mask = clusters == cluster_id
                cluster_features = features[cluster_mask]
                mean_features = np.mean(cluster_features, axis=0)
                
                # Análise das características
                returns_short = mean_features[0] if len(mean_features) > 0 else 0  # returns_1
                returns_long = mean_features[3] if len(mean_features) > 3 else 0   # returns_20
                volatility = mean_features[4] if len(mean_features) > 4 else 0     # volatility
                
                # Classificação baseada em características
                if returns_long > 0.1 and volatility < 0:
                    regime = 'Bull Market'
                elif returns_long < -0.1 and volatility < 0:
                    regime = 'Bear Market'
                elif volatility > 0.5:
                    regime = 'High Volatility'
                elif abs(returns_long) < 0.05 and volatility < 0:
                    regime = 'Sideways Market'
                else:
                    regime = f'Regime_{cluster_id}'
                
                interpretations[cluster_id] = regime
            
            return interpretations
            
        except Exception as e:
            logger.error(f"Erro na interpretação de clusters: {e}")
            return {i: f'Regime_{i}' for i in np.unique(clusters)}
    
    def _detect_correlation_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detectar regimes baseados em correlações entre indicadores"""
        try:
            # Calcular correlações móveis entre indicadores
            correlation_features = []
            
            if all(col in df.columns for col in ['close', 'volume']):
                # Correlação preço-volume
                price_vol_corr = df['close'].rolling(50).corr(df['volume'])
                correlation_features.append(('price_volume_corr', price_vol_corr))
            
            if all(col in df.columns for col in ['close', 'rsi']):
                # Correlação preço-RSI (para detectar divergências)
                price_rsi_corr = df['close'].rolling(50).corr(df['rsi'])
                correlation_features.append(('price_rsi_corr', price_rsi_corr))
            
            if 'close' in df.columns:
                # Auto-correlação do preço (persistence)
                price_autocorr = df['close'].rolling(50).apply(
                    lambda x: x.autocorr(lag=1) if len(x) > 1 else 0, raw=False
                )
                correlation_features.append(('price_autocorr', price_autocorr))
            
            # Regime baseado em correlações
            if correlation_features:
                # Média das correlações absolutas
                corr_values = [abs(corr.fillna(0)) for _, corr in correlation_features]
                avg_correlation = np.mean(corr_values, axis=0)
                
                # Classificar regime de correlação
                correlation_regime = []
                for corr in avg_correlation:
                    if corr > 0.7:
                        regime = 'High Correlation'
                    elif corr > 0.4:
                        regime = 'Medium Correlation'
                    else:
                        regime = 'Low Correlation'
                    
                    correlation_regime.append(regime)
                
                df['correlation_regime'] = correlation_regime
                df['correlation_strength'] = avg_correlation
                
                # Adicionar correlações individuais
                for name, corr in correlation_features:
                    df[name] = corr.fillna(0)
            else:
                df['correlation_regime'] = 'Unknown'
                df['correlation_strength'] = 0.5
            
            return df
            
        except Exception as e:
            logger.error(f"Erro na detecção de regime de correlação: {e}")
            df['correlation_regime'] = 'Unknown'
            df['correlation_strength'] = 0.5
            return df
    
    def _calculate_ensemble_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular regime consolidado usando ensemble de métodos"""
        try:
            # Componentes do ensemble
            regime_components = {
                'trend_regime_score': 0.3,
                'volatility_regime_score': 0.2,
                'momentum_regime_score': 0.25,
                'correlation_strength': 0.15,
                'volatility_clustering': 0.1
            }
            
            # Score ponderado
            ensemble_score = pd.Series(0.0, index=df.index)
            weights_sum = 0
            
            for component, weight in regime_components.items():
                if component in df.columns:
                    normalized_component = df[component].fillna(0)
                    
                    # Normalizar componentes para escala similar
                    if component == 'volatility_regime_score':
                        normalized_component = (normalized_component - 2) / 2  # Escala 0-4 para -1 a 1
                    elif component in ['correlation_strength', 'volatility_clustering']:
                        normalized_component = (normalized_component - 0.5) * 2  # Escala 0-1 para -1 a 1
                    
                    ensemble_score += normalized_component * weight
                    weights_sum += weight
            
            # Normalizar pelo peso total usado
            if weights_sum > 0:
                ensemble_score /= weights_sum
            
            df['ensemble_regime_score'] = ensemble_score
            
            # Classificar regime consolidado
            ensemble_regime = []
            for score in ensemble_score:
                if pd.isna(score):
                    regime = 'Unknown'
                elif score > 0.5:
                    regime = 'Strong Bull'
                elif score > 0.2:
                    regime = 'Bull'
                elif score > -0.2:
                    regime = 'Neutral'
                elif score > -0.5:
                    regime = 'Bear'
                else:
                    regime = 'Strong Bear'
                
                ensemble_regime.append(regime)
            
            df['ensemble_regime'] = ensemble_regime
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no ensemble de regimes: {e}")
            df['ensemble_regime'] = 'Unknown'
            df['ensemble_regime_score'] = 0
            return df
    
    def _calculate_regime_stability(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular estabilidade e persistência dos regimes"""
        try:
            if 'ensemble_regime' not in df.columns:
                df['regime_stability'] = 0
                return df
            
            # Calcular mudanças de regime
            regime_changes = (df['ensemble_regime'] != df['ensemble_regime'].shift(1)).astype(int)
            df['regime_change'] = regime_changes
            
            # Calcular estabilidade (inverso da frequência de mudanças)
            stability_window = 20
            change_frequency = regime_changes.rolling(stability_window).mean()
            regime_stability = 1 - change_frequency
            df['regime_stability'] = regime_stability.fillna(0.5)
            
            # Duração do regime atual
            regime_duration = []
            current_duration = 0
            last_regime = None
            
            for regime in df['ensemble_regime']:
                if regime == last_regime:
                    current_duration += 1
                else:
                    current_duration = 1
                    last_regime = regime
                
                regime_duration.append(current_duration)
            
            df['regime_duration'] = regime_duration
            
            # Persistência (probabilidade de continuar no mesmo regime)
            persistence_window = 50
            if len(df) >= persistence_window:
                persistence_scores = []
                
                for i in range(len(df)):
                    if i < persistence_window:
                        persistence_scores.append(0.5)
                    else:
                        recent_regimes = df['ensemble_regime'].iloc[i-persistence_window:i]
                        current_regime = df['ensemble_regime'].iloc[i]
                        
                        # Calcular probabilidade de persistência
                        regime_counts = recent_regimes.value_counts()
                        total_periods = len(recent_regimes)
                        current_regime_count = regime_counts.get(current_regime, 0)
                        
                        persistence = current_regime_count / total_periods
                        persistence_scores.append(persistence)
                
                df['regime_persistence'] = persistence_scores
            else:
                df['regime_persistence'] = 0.5
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no cálculo de estabilidade: {e}")
            df['regime_stability'] = 0.5
            df['regime_duration'] = 1
            df['regime_persistence'] = 0.5
            return df
    
    def _calculate_transition_probabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular probabilidades de transição entre regimes"""
        try:
            if 'ensemble_regime' not in df.columns:
                df['transition_probability'] = 0
                return df
            
            # Calcular matriz de transição
            regimes = df['ensemble_regime'].dropna()
            unique_regimes = regimes.unique()
            
            transition_matrix = pd.DataFrame(
                index=unique_regimes, 
                columns=unique_regimes, 
                data=0.0
            )
            
            # Contar transições
            for i in range(len(regimes) - 1):
                current_regime = regimes.iloc[i]
                next_regime = regimes.iloc[i + 1]
                
                if current_regime in transition_matrix.index and next_regime in transition_matrix.columns:
                    transition_matrix.loc[current_regime, next_regime] += 1
            
            # Normalizar para probabilidades
            for regime in transition_matrix.index:
                row_sum = transition_matrix.loc[regime].sum()
                if row_sum > 0:
                    transition_matrix.loc[regime] = transition_matrix.loc[regime] / row_sum
            
            # Calcular probabilidade de mudança para próximo período
            transition_probs = []
            
            for i, current_regime in enumerate(df['ensemble_regime']):
                if pd.isna(current_regime) or current_regime not in transition_matrix.index:
                    transition_probs.append(0.5)
                else:
                    # Probabilidade de mudança = 1 - probabilidade de permanecer
                    stay_prob = transition_matrix.loc[current_regime, current_regime]
                    change_prob = 1 - stay_prob
                    transition_probs.append(change_prob)
            
            df['transition_probability'] = transition_probs
            
            # Salvar matriz de transição para referência
            self.regime_models['transition_matrix'] = transition_matrix
            
            return df
            
        except Exception as e:
            logger.error(f"Erro no cálculo de probabilidades de transição: {e}")
            df['transition_probability'] = 0.5
            return df
    
    def get_regime_summary(self, df: pd.DataFrame) -> Dict:
        """Obter resumo completo dos regimes detectados"""
        try:
            if df.empty:
                return {}
            
            latest = df.iloc[-1]
            
            return {
                'current_regime': str(latest.get('ensemble_regime', 'Unknown')),
                'regime_score': float(latest.get('ensemble_regime_score', 0)),
                'regime_stability': float(latest.get('regime_stability', 0.5)),
                'regime_duration': int(latest.get('regime_duration', 1)),
                'regime_persistence': float(latest.get('regime_persistence', 0.5)),
                'transition_probability': float(latest.get('transition_probability', 0.5)),
                'components': {
                    'trend_regime': str(latest.get('trend_regime', 'Unknown')),
                    'volatility_regime': str(latest.get('volatility_regime', 'Unknown')),
                    'momentum_regime': str(latest.get('momentum_regime', 'Unknown')),
                    'clustering_regime': str(latest.get('clustering_regime', 'Unknown')),
                    'correlation_regime': str(latest.get('correlation_regime', 'Unknown'))
                },
                'scores': {
                    'trend_score': float(latest.get('trend_regime_score', 0)),
                    'volatility_score': float(latest.get('volatility_regime_score', 2)),
                    'momentum_score': float(latest.get('momentum_regime_score', 0)),
                    'correlation_strength': float(latest.get('correlation_strength', 0.5))
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo de regime: {e}")
            return {}
    
    def predict_regime_change(self, df: pd.DataFrame, periods_ahead: int = 3) -> Dict:
        """Predizer mudanças de regime nos próximos períodos"""
        try:
            if 'transition_probability' not in df.columns:
                return {'change_probability': 0.5, 'confidence': 'Low'}
            
            # Usar últimas probabilidades de transição
            recent_transition_probs = df['transition_probability'].tail(10).mean()
            current_stability = df['regime_stability'].iloc[-1] if 'regime_stability' in df.columns else 0.5
            current_duration = df['regime_duration'].iloc[-1] if 'regime_duration' in df.columns else 1
            
            # Ajustar probabilidade baseada na duração (regimes longos têm maior chance de mudar)
            duration_factor = min(current_duration / 20, 1.0)  # Normalizar para max 20 períodos
            adjusted_prob = recent_transition_probs * (1 + duration_factor * 0.5)
            
            # Ajustar pela estabilidade (baixa estabilidade = maior chance de mudança)
            stability_factor = 1 - current_stability
            final_prob = adjusted_prob * (1 + stability_factor)
            
            # Clip probability
            final_prob = np.clip(final_prob, 0, 1)
            
            # Determinar confiança
            if current_stability > 0.8:
                confidence = 'High'
            elif current_stability > 0.6:
                confidence = 'Medium'
            else:
                confidence = 'Low'
            
            return {
                'change_probability': float(final_prob),
                'confidence': confidence,
                'current_duration': int(current_duration),
                'stability': float(current_stability),
                'factors': {
                    'base_transition_prob': float(recent_transition_probs),
                    'duration_adjustment': float(duration_factor),
                    'stability_adjustment': float(stability_factor)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na predição de mudança de regime: {e}")
            return {'change_probability': 0.5, 'confidence': 'Low'}
