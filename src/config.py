#!/usr/bin/env python3
"""
Arquivo de configuração para o Trading Bot AI - OTIMIZADO PARA HEROKU
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Config:
    """Configurações do sistema de trading - OTIMIZADAS para startup rápido"""
    
    # Configurações de API
    BINANCE_API_KEY: str = field(default_factory=lambda: os.getenv('BINANCE_API_KEY', ''))
    BINANCE_SECRET_KEY: str = field(default_factory=lambda: os.getenv('BINANCE_SECRET_KEY', ''))
    
    # Configurações de timeframes - OTIMIZADO para startup rápido
    TIMEFRAMES: List[str] = field(default_factory=lambda: ['1h'])  # Apenas 1 timeframe para startup
    STARTUP_TIMEFRAMES: List[str] = field(default_factory=lambda: ['1h'])  # Timeframes mínimos para startup
    ALL_TIMEFRAMES: List[str] = field(default_factory=lambda: ['1m', '5m', '15m', '30m', '1h', '4h', '1d'])  # Todos os timeframes
    DEFAULT_TIMEFRAME: str = '1h'
    
    # Pares de trading - OTIMIZADO para startup rápido no Heroku
    CRYPTO_PAIRS: List[str] = field(default_factory=lambda: [
        # Apenas pares essenciais para startup rápido (reduzido de 20 para 3)
        'BTCUSDT', 'ETHUSDT', 'COMPUSDT'
    ])
    
    # Lista completa de pares - carregada sob demanda
    ALL_CRYPTO_PAIRS: List[str] = field(default_factory=lambda: [
        # Crypto Major (alta liquidez)
        'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT',
        'BNBUSDT', 'XRPUSDT', 'LTCUSDT', 'BCHUSDT', 'EOSUSDT',
        # Crypto Alt (média liquidez)  
        'SOLUSDT', 'MATICUSDT', 'AVAXUSDT', 'UNIUSDT', 'ATOMUSDT',
        'ALGOUSDT', 'FILUSDT', 'AAVEUSDT', 'SUSHIUSDT', 'COMPUSDT'
    ])
    
    # FOREX_PAIRS removido - sistema agora suporta apenas criptomoedas
    FOREX_PAIRS: List[str] = field(default_factory=lambda: [])
    
    # Configurações de IA
    AI_MODEL_PATH: str = 'models/'
    RETRAIN_INTERVAL_HOURS: int = 24
    MIN_TRAINING_SAMPLES: int = 100  # Reduzido para permitir treinamento com menos dados
    
    # Indicadores técnicos
    TECHNICAL_INDICATORS: Dict = field(default_factory=lambda: {
        'sma_periods': [10, 20, 50, 100, 200],
        'ema_periods': [12, 26, 50],
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'bb_period': 20,
        'bb_std': 2,
        'stoch_k': 14,
        'stoch_d': 3,
        'atr_period': 14,
        'adx_period': 14
    })
    
    # Configurações de volume
    VOLUME_INDICATORS: Dict = field(default_factory=lambda: {
        'volume_sma_period': 20,
        'volume_threshold_multiplier': 1.5,
        'obv_enabled': True,
        'vwap_enabled': True
    })
    
    # Configurações de risco - Nova estratégia IA 1:1 com alta assertividade
    RISK_MANAGEMENT: Dict = field(default_factory=lambda: {
        'max_risk_per_trade': 0.03,   # 3% por trade (maior exposição para 1:1)
        'max_daily_loss': 0.08,       # 8% perda diária máxima
        'max_open_positions': 2,      # Máximo 2 posições (foco em qualidade)
        'stop_loss_pct': 0.025,       # 2.5% stop loss (1:1 ratio)
        'take_profit_pct': 0.025,     # 2.5% take profit (1:1 ratio)
        'trailing_stop_pct': 0.008,   # 0.8% trailing stop
        'risk_reward_ratio': 1.0,     # Ratio 1:1 (risco:recompensa)
        'min_ai_confidence': 0.30     # Mínimo 30% confiança IA para executar (muito permissivo)
    })
    
    # Configurações de sinal - Nova estratégia IA com análise de mercado
    SIGNAL_CONFIG: Dict = field(default_factory=lambda: {
        'min_confidence': 0.01,      # 🎯 Confiança mínima 1% (extremamente permissivo)
        'min_ai_confidence': 0.01,   # 🤖 Confiança mínima da IA 1% (extremamente permissivo)
        'max_confidence': 0.98,      # 📊 Confiança máxima 98% (quase certeza)
        'signal_cooldown_minutes': 0, # ⏱️ Cooldown DESABILITADO para desenvolvimento
        'max_signals_per_hour': 20,    # 📈 Máximo 20 sinais por hora
        'enable_ai_analysis': True,   # ✅ Análise IA obrigatória
        'enable_market_context': True, # ✅ Contexto de mercado obrigatório
        'enable_confluence': False,   # ❌ Confluência desabilitada (nova estratégia IA)
        'min_confluence_count': 1,    # Mínimo de 1 indicador em confluência
        'min_market_score': 0.01,    # Mínimo 1% score de mercado (extremamente permissivo)
        'quality_over_quantity': True,  # Priorizar qualidade
        'min_score_difference': 0.05,  # Diferença mínima entre buy/sell scores
        'strong_signal_threshold': 0.25,  # Threshold para sinais fortes
        'medium_signal_threshold': 0.15,  # Threshold para sinais médios
        'weak_signal_threshold': 0.08     # Threshold para sinais fracos
    })
    
    # Configurações de notificação
    NOTIFICATION_CONFIG: Dict = field(default_factory=lambda: {
        'telegram_enabled': False,
        'telegram_token': os.getenv('TELEGRAM_TOKEN', ''),
        'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
        'email_enabled': False,
        'webhook_enabled': True,
        'webhook_url': os.getenv('WEBHOOK_URL', '')
    })
    
    # Configurações de análise de mercado com IA - NOVA INTEGRAÇÃO
    AI_MARKET_ANALYSIS: Dict = field(default_factory=lambda: {
        'sentiment_analysis': True,     # Análise de sentimento
        'volume_analysis': True,        # Análise de volume
        'volatility_analysis': True,    # Análise de volatilidade
        'correlation_analysis': True,   # Análise de correlação
        'momentum_analysis': True,      # Análise de momentum
        'pattern_recognition': True,    # Reconhecimento de padrões
        'market_regime_detection': True, # Detecção de regime de mercado
        'liquidity_analysis': True,     # Análise de liquidez
        'orderbook_analysis': False,    # Análise de order book (premium)
        'news_sentiment': False,        # Sentimento de notícias (premium)
        'social_sentiment': False,      # Sentimento social (premium)
        'macro_indicators': True,       # Indicadores macroeconômicos
        'fear_greed_index': True,       # Índice de medo e ganância
        'funding_rates': True,          # Taxas de funding
        'open_interest': True,          # Open interest
        'whale_movements': False,       # Movimentos de baleias (premium)
        'market_cap_analysis': True,    # Análise de market cap
        'dominance_analysis': True,     # Análise de dominância
        'cross_asset_correlation': True # Correlação entre ativos
    })
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        # Criar diretórios necessários
        os.makedirs(self.AI_MODEL_PATH, exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
    def get_all_pairs(self) -> List[str]:
        """Retorna todos os pares de trading disponíveis - apenas crypto"""
        return self.ALL_CRYPTO_PAIRS
    
    def get_startup_pairs(self) -> List[str]:
        """Retorna apenas pares essenciais para startup rápido"""
        return self.CRYPTO_PAIRS
    
    def get_startup_timeframes(self) -> List[str]:
        """Retorna timeframes mínimos para startup"""
        return self.STARTUP_TIMEFRAMES
    
    def get_all_timeframes(self) -> List[str]:
        """Retorna todos os timeframes disponíveis"""
        return self.ALL_TIMEFRAMES
    
    def is_crypto_pair(self, symbol: str) -> bool:
        """Verifica se é um par de criptomoeda"""
        return symbol in self.ALL_CRYPTO_PAIRS  # Verificar na lista completa
    
    def is_forex_pair(self, symbol: str) -> bool:
        """Verifica se é um par de forex - DESABILITADO"""
        return False  # Forex removido do sistema
    
    def get_asset_type(self, symbol: str) -> str:
        """Retorna o tipo de ativo (apenas crypto suportado)"""
        if self.is_crypto_pair(symbol):
            return 'crypto'
        else:
            return 'unknown'  # Forex não mais suportado
    
    def get_model_path(self, model_name: str) -> str:
        """Retorna o caminho completo do modelo"""
        return os.path.join(self.AI_MODEL_PATH, f"{model_name}.pkl")
