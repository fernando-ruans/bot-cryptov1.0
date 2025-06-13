import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from .utils import calculate_correlation
import logging

logger = logging.getLogger(__name__)

class CrossCorrelationAnalyzer:
    """
    Calcula correlação cruzada (rolling) entre pares de ativos e gera features para o pipeline de IA.
    
    Features geradas:
    - Rolling correlations para múltiplas janelas
    - Regime de correlação (alta/média/baixa)
    - Força da correlação (valor absoluto)
    - Mudanças na correlação
    - Breakdown de correlação (detecta mudanças abruptas)
    """
    def __init__(self, 
                 window_sizes: List[int] = [7, 14, 30, 60],
                 price_column: str = 'close',
                 correlation_thresholds: Tuple[float, float] = (0.3, 0.7)):
        """
        Args:
            window_sizes: Janelas para rolling correlation
            price_column: Coluna de preço a usar ('close', 'high', 'low', etc.)
            correlation_thresholds: (baixa, alta) para classificar regime de correlação
        """
        self.window_sizes = sorted(window_sizes)
        self.price_column = price_column
        self.low_corr_threshold, self.high_corr_threshold = correlation_thresholds

    def _validate_input(self, price_dfs: Dict[str, pd.DataFrame]) -> bool:
        """Valida se os DataFrames de entrada têm a estrutura esperada"""
        try:
            for symbol, df in price_dfs.items():
                if not isinstance(df, pd.DataFrame):
                    logger.error(f"Dados para {symbol} não são um DataFrame")
                    return False
                if self.price_column not in df.columns:
                    logger.error(f"Coluna '{self.price_column}' não encontrada em {symbol}")
                    return False
                if len(df) < self.window_sizes[-1]:
                    logger.warning(f"DataFrame para {symbol} tem poucos dados ({len(df)} < {self.window_sizes[-1]})")
            return True
        except Exception as e:
            logger.error(f"Erro na validação de entrada: {e}")
            return False

    def _classify_correlation_regime(self, correlation: pd.Series) -> pd.Series:
        """Classifica regime de correlação em 'Low', 'Medium', 'High'"""
        abs_corr = correlation.abs()
        regime = pd.Series('Medium', index=correlation.index)
        regime[abs_corr < self.low_corr_threshold] = 'Low'
        regime[abs_corr > self.high_corr_threshold] = 'High'
        return regime

    def _detect_correlation_breakdown(self, correlation: pd.Series, window: int = 10) -> pd.Series:
        """Detecta mudanças abruptas na correlação (breakdown/regime change)"""
        try:
            # Mudança absoluta na correlação
            corr_change = correlation.diff().abs()
            
            # Threshold dinâmico baseado na volatilidade histórica da correlação
            volatility = correlation.rolling(window * 2).std()
            threshold = volatility * 2  # 2 desvios padrão
            
            # Breakdown quando mudança > threshold
            breakdown = corr_change > threshold
            return breakdown.fillna(False)
        except Exception as e:
            logger.error(f"Erro na detecção de breakdown: {e}")
            return pd.Series(False, index=correlation.index)

    def compute_pairwise_correlation(self, price_dfs: Dict[str, pd.DataFrame], pairs: List[Tuple[str, str]]) -> Dict[str, pd.DataFrame]:
        """
        Para cada par de ativos, calcula rolling correlation e features derivadas.
        Retorna um dicionário: { 'BTCUSDT-ETHUSDT': DataFrame, ... }
        """
        if not self._validate_input(price_dfs):
            return {}
        
        results = {}
        
        for sym1, sym2 in pairs:
            try:
                # Verificar se os símbolos existem
                if sym1 not in price_dfs or sym2 not in price_dfs:
                    logger.warning(f"Par {sym1}-{sym2} não disponível nos dados")
                    continue
                
                df1 = price_dfs[sym1].copy()
                df2 = price_dfs[sym2].copy()
                
                # Alinhar datas e tratar dados faltantes
                df = pd.DataFrame(index=df1.index.union(df2.index))
                df[f'{sym1}_price'] = df1[self.price_column].reindex(df.index)
                df[f'{sym2}_price'] = df2[self.price_column].reindex(df.index)
                  # Forward fill para preencher gaps pequenos (máximo 3 períodos)
                df = df.ffill(limit=3)
                
                # Verificar se há dados suficientes após alinhamento
                valid_data = df.dropna()
                if len(valid_data) < self.window_sizes[0]:
                    logger.warning(f"Dados insuficientes para par {sym1}-{sym2} após alinhamento")
                    continue
                  # === ROLLING CORRELATIONS ===
                correlations = {}
                new_features = {}
                
                # Calcular rolling correlations
                for w in self.window_sizes:
                    corr_col = f'corr_{w}d'
                    new_features[corr_col] = df[f'{sym1}_price'].rolling(w).corr(df[f'{sym2}_price'])
                    correlations[w] = corr_col
                
                # === FEATURES PRINCIPAIS ===
                # Feature principal: correlation regime (janela maior)
                main_corr_col = correlations[self.window_sizes[-1]]
                correlation_regime = new_features[main_corr_col]
                new_features['correlation_regime'] = correlation_regime
                new_features['correlation_strength'] = correlation_regime.abs()
                new_features['correlation_change'] = correlation_regime.diff()
                
                # === FEATURES AVANÇADAS ===
                # Regime de correlação (categórico)
                new_features['correlation_class'] = self._classify_correlation_regime(correlation_regime)
                
                # Breakdown de correlação
                new_features['correlation_breakdown'] = self._detect_correlation_breakdown(correlation_regime)
                
                # Estabilidade da correlação (baixa variância = mais estável)
                new_features['correlation_stability'] = 1 / (1 + correlation_regime.rolling(20).std().fillna(1))
                
                # Convergência/divergência entre janelas curtas e longas
                if len(self.window_sizes) >= 2:
                    short_corr = new_features[correlations[self.window_sizes[0]]]
                    long_corr = new_features[correlations[self.window_sizes[-1]]]
                    new_features['correlation_divergence'] = short_corr - long_corr
                
                # === ESTATÍSTICAS ADICIONAIS ===
                # Média móvel da correlação (suavização)
                new_features['correlation_ma'] = correlation_regime.rolling(10).mean()
                
                # Percentil da correlação (posição relativa)
                new_features['correlation_percentile'] = correlation_regime.rolling(100).rank(pct=True)
                
                # Concatenar todas as features de uma vez (otimização de performance)
                features_df = pd.DataFrame(new_features, index=df.index)
                df = pd.concat([df, features_df], axis=1)
                
                # Limpeza final
                pair_key = f'{sym1}-{sym2}'
                results[pair_key] = df
                
                logger.info(f"✅ Correlação calculada para par {pair_key}: {len(df)} períodos")
                
            except Exception as e:
                logger.error(f"Erro ao calcular correlação para par {sym1}-{sym2}: {e}")
                continue
        
        return results

    def get_correlation_features(self, 
                                price_dfs: Dict[str, pd.DataFrame], 
                                base_symbol: str = 'BTCUSDT',
                                feature_names: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Para cada ativo (exceto o base), calcula rolling correlation com o base 
        e retorna features para merge no pipeline.
        
        Args:
            price_dfs: Dicionário com DataFrames de preços por símbolo
            base_symbol: Símbolo base para correlação (default: BTCUSDT)
            feature_names: Lista de features a retornar (default: principais)
        
        Returns:
            Dict com DataFrames de features por símbolo: {símbolo: DataFrame}
        """
        if feature_names is None:
            feature_names = [
                'correlation_regime', 'correlation_strength', 'correlation_change',
                'correlation_class', 'correlation_breakdown', 'correlation_stability'
            ]
        
        if base_symbol not in price_dfs:
            logger.error(f"Símbolo base {base_symbol} não encontrado nos dados")
            return {}
        
        features_by_symbol = {}
        
        # Calcular pares: cada ativo vs base
        pairs = [(sym, base_symbol) for sym in price_dfs.keys() if sym != base_symbol]
        
        if not pairs:
            logger.warning("Nenhum par para análise de correlação")
            return {}
        
        # Calcular correlações
        correlations = self.compute_pairwise_correlation(price_dfs, pairs)
        
        # Extrair features para cada símbolo
        for sym, _ in pairs:
            pair_key = f'{sym}-{base_symbol}'
            if pair_key not in correlations:
                logger.warning(f"Correlação não disponível para {pair_key}")
                continue
            
            pair_df = correlations[pair_key]
            
            # Extrair apenas as features solicitadas
            symbol_features = pd.DataFrame(index=pair_df.index)
            
            for feature in feature_names:
                if feature in pair_df.columns:
                    symbol_features[feature] = pair_df[feature]
                else:
                    logger.warning(f"Feature '{feature}' não encontrada para {pair_key}")
            
            features_by_symbol[sym] = symbol_features
            logger.info(f"✅ Features de correlação extraídas para {sym}: {list(symbol_features.columns)}")
        
        return features_by_symbol

    def get_correlation_matrix(self, price_dfs: Dict[str, pd.DataFrame], window: int = 30) -> pd.DataFrame:
        """
        Calcula matriz de correlação rolling entre todos os ativos.
        
        Returns:
            DataFrame com correlações: linhas=datas, colunas=pares de ativos
        """
        symbols = list(price_dfs.keys())
        if len(symbols) < 2:
            logger.warning("Menos de 2 símbolos disponíveis para matriz de correlação")
            return pd.DataFrame()
        
        # Criar todas as combinações de pares
        pairs = []
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                pairs.append((sym1, sym2))
        
        # Calcular correlações
        correlations = self.compute_pairwise_correlation(price_dfs, pairs)
        
        # Construir matriz
        matrix_df = pd.DataFrame()
        for pair_key, pair_df in correlations.items():
            matrix_df[pair_key] = pair_df[f'corr_{window}d'] if f'corr_{window}d' in pair_df.columns else pair_df['correlation_regime']
        
        return matrix_df

    def get_correlation_summary(self, price_dfs: Dict[str, pd.DataFrame]) -> Dict[str, dict]:
        """
        Retorna resumo estatístico das correlações para análise exploratória.
        """
        summary = {}
        
        # Correlações com base (BTCUSDT)
        base_features = self.get_correlation_features(price_dfs)
        
        for symbol, features_df in base_features.items():
            if 'correlation_regime' in features_df.columns:
                corr_series = features_df['correlation_regime'].dropna()
                
                summary[f'{symbol}_vs_BTC'] = {
                    'mean_correlation': corr_series.mean(),
                    'std_correlation': corr_series.std(),
                    'min_correlation': corr_series.min(),
                    'max_correlation': corr_series.max(),
                    'current_correlation': corr_series.iloc[-1] if len(corr_series) > 0 else np.nan,
                    'positive_correlation_pct': (corr_series > 0).mean() * 100,
                    'high_correlation_pct': (corr_series.abs() > self.high_corr_threshold).mean() * 100
                }
        
        return summary
