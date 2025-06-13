#!/usr/bin/env python3
"""
Utilitários e funções auxiliares para o trading bot
"""

import hashlib
import uuid
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from functools import wraps
import os
import requests
from decimal import Decimal, ROUND_DOWN

logger = logging.getLogger(__name__)

def generate_signal_id(symbol: str, signal_type: str, timestamp: datetime) -> str:
    """Gerar ID único para sinal"""
    data = f"{symbol}_{signal_type}_{timestamp.isoformat()}"
    return hashlib.md5(data.encode()).hexdigest()[:12]

def generate_position_id() -> str:
    """Gerar ID único para posição"""
    return str(uuid.uuid4())[:8]

def format_currency(value: float, decimals: int = 2) -> str:
    """Formatar valor monetário"""
    return f"${value:,.{decimals}f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Formatar porcentagem"""
    return f"{value:.{decimals}f}%"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calcular mudança percentual"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """Divisão segura evitando divisão por zero"""
    return numerator / denominator if denominator != 0 else default

def normalize_symbol(symbol: str) -> str:
    """Normalizar símbolo de trading"""
    return symbol.upper().replace('/', '').replace('-', '')

def is_crypto_symbol(symbol: str) -> bool:
    """Verificar se é símbolo de criptomoeda"""
    crypto_suffixes = ['USDT', 'BTC', 'ETH', 'BNB', 'BUSD']
    return any(symbol.endswith(suffix) for suffix in crypto_suffixes)

def is_forex_symbol(symbol: str) -> bool:
    """Verificar se é símbolo de forex - DESABILITADO"""
    return False  # Forex removido do sistema

def get_timeframe_minutes(timeframe: str) -> int:
    """Converter timeframe para minutos"""
    timeframe_map = {
        '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
        '1h': 60, '2h': 120, '4h': 240, '6h': 360, '8h': 480, '12h': 720,
        '1d': 1440, '3d': 4320, '1w': 10080, '1M': 43200
    }
    return timeframe_map.get(timeframe, 60)

def get_next_timeframe_time(timeframe: str, current_time: datetime = None) -> datetime:
    """Obter próximo horário do timeframe"""
    if current_time is None:
        current_time = datetime.now()
    
    minutes = get_timeframe_minutes(timeframe)
    
    # Arredondar para o próximo intervalo
    current_minute = current_time.minute
    next_minute = ((current_minute // minutes) + 1) * minutes
    
    if next_minute >= 60:
        next_hour = current_time.hour + (next_minute // 60)
        next_minute = next_minute % 60
        next_time = current_time.replace(hour=next_hour % 24, minute=next_minute, second=0, microsecond=0)
        
        if next_hour >= 24:
            next_time += timedelta(days=1)
    else:
        next_time = current_time.replace(minute=next_minute, second=0, microsecond=0)
    
    return next_time

def calculate_position_size(account_balance: float, risk_per_trade: float, 
                          entry_price: float, stop_loss: float) -> float:
    """Calcular tamanho da posição baseado no risco"""
    risk_amount = account_balance * (risk_per_trade / 100)
    price_diff = abs(entry_price - stop_loss)
    
    if price_diff == 0:
        return 0
    
    position_size = risk_amount / price_diff
    return round(position_size, 8)

def calculate_stop_loss(entry_price: float, atr: float, multiplier: float = 2.0, 
                       side: str = 'buy') -> float:
    """Calcular stop loss baseado no ATR"""
    if side.lower() == 'buy':
        return entry_price - (atr * multiplier)
    else:
        return entry_price + (atr * multiplier)

def calculate_take_profit(entry_price: float, stop_loss: float, 
                         risk_reward_ratio: float = 2.0, side: str = 'buy') -> float:
    """Calcular take profit baseado no risco/recompensa"""
    risk = abs(entry_price - stop_loss)
    reward = risk * risk_reward_ratio
    
    if side.lower() == 'buy':
        return entry_price + reward
    else:
        return entry_price - reward

def round_to_tick_size(price: float, tick_size: float) -> float:
    """Arredondar preço para o tick size"""
    if tick_size == 0:
        return price
    
    decimal_places = len(str(tick_size).split('.')[-1]) if '.' in str(tick_size) else 0
    multiplier = 1 / tick_size
    
    return round(round(price * multiplier) / multiplier, decimal_places)

def validate_price_levels(entry: float, stop_loss: float, take_profit: float, 
                         side: str) -> bool:
    """Validar níveis de preço"""
    if side.lower() == 'buy':
        return stop_loss < entry < take_profit
    else:
        return take_profit < entry < stop_loss

def calculate_risk_reward_ratio(entry: float, stop_loss: float, take_profit: float) -> float:
    """Calcular ratio risco/recompensa"""
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)
    
    return safe_divide(reward, risk, 0)

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calcular Sharpe Ratio"""
    if not returns or len(returns) < 2:
        return 0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
    
    if np.std(excess_returns) == 0:
        return 0
    
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calcular Sortino Ratio"""
    if not returns or len(returns) < 2:
        return 0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - (risk_free_rate / 252)
    
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0 or np.std(downside_returns) == 0:
        return 0
    
    return np.mean(excess_returns) / np.std(downside_returns) * np.sqrt(252)

def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """Calcular máximo drawdown"""
    if not equity_curve or len(equity_curve) < 2:
        return 0
    
    peak = equity_curve[0]
    max_dd = 0
    
    for value in equity_curve:
        if value > peak:
            peak = value
        
        drawdown = (peak - value) / peak * 100
        max_dd = max(max_dd, drawdown)
    
    return max_dd

def calculate_win_rate(trades: List[Dict]) -> float:
    """Calcular taxa de acerto"""
    if not trades:
        return 0
    
    winning_trades = sum(1 for trade in trades if trade.get('realized_pnl', 0) > 0)
    return (winning_trades / len(trades)) * 100

def calculate_profit_factor(trades: List[Dict]) -> float:
    """Calcular fator de lucro"""
    if not trades:
        return 0
    
    gross_profit = sum(trade.get('realized_pnl', 0) for trade in trades if trade.get('realized_pnl', 0) > 0)
    gross_loss = abs(sum(trade.get('realized_pnl', 0) for trade in trades if trade.get('realized_pnl', 0) < 0))
    
    return safe_divide(gross_profit, gross_loss, 0)

def calculate_average_trade(trades: List[Dict]) -> float:
    """Calcular trade médio"""
    if not trades:
        return 0
    
    total_pnl = sum(trade.get('realized_pnl', 0) for trade in trades)
    return total_pnl / len(trades)

def detect_market_session(current_time: datetime = None) -> str:
    """Detectar sessão de mercado atual"""
    if current_time is None:
        current_time = datetime.utcnow()
    
    hour = current_time.hour
    
    # Sessões de mercado (UTC)
    if 22 <= hour or hour < 6:  # 22:00-06:00 UTC
        return 'sydney'
    elif 0 <= hour < 9:  # 00:00-09:00 UTC
        return 'tokyo'
    elif 7 <= hour < 16:  # 07:00-16:00 UTC
        return 'london'
    elif 13 <= hour < 22:  # 13:00-22:00 UTC
        return 'new_york'
    else:
        return 'overlap'

def is_market_open(symbol: str, current_time: datetime = None) -> bool:
    """Verificar se mercado está aberto"""
    if current_time is None:
        current_time = datetime.utcnow()
      # Crypto funciona 24/7
    if is_crypto_symbol(symbol):
        return True
    
    # Forex removido - apenas crypto suportado
    return True  # Assumir mercado aberto para compatibilidade

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator para retry em caso de falha"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Tentativa {attempt + 1} falhou para {func.__name__}: {e}")
                        time.sleep(delay * (attempt + 1))
                    else:
                        logger.error(f"Todas as {max_retries} tentativas falharam para {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator

def rate_limit(calls_per_second: float = 1.0):
    """Decorator para rate limiting"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

def log_execution_time(func):
    """Decorator para logar tempo de execução"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.debug(f"{func.__name__} executado em {execution_time:.4f}s")
        return result
    return wrapper

def safe_json_loads(json_str: str, default=None):
    """JSON loads seguro"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Conversão segura para float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Conversão segura para int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Limpar DataFrame removendo NaN e infinitos"""
    if df.empty:
        return df
    
    # Remover linhas com todos os valores NaN
    df = df.dropna(how='all')
    
    # Substituir infinitos por NaN e depois preencher
    df = df.replace([np.inf, -np.inf], np.nan)
      # Preencher NaN com método forward fill e depois backward fill
    df = df.ffill().bfill()
    
    return df

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validar se DataFrame tem as colunas necessárias"""
    if df.empty:
        return False
    
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        logger.warning(f"Colunas faltando no DataFrame: {missing_columns}")
        return False
    
    return True

def create_directory(path: str):
    """Criar diretório se não existir"""
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.error(f"Erro ao criar diretório {path}: {e}")

def get_file_size(file_path: str) -> float:
    """Obter tamanho do arquivo em MB"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except OSError:
        return 0

def format_timestamp(timestamp: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Formatar timestamp"""
    return timestamp.strftime(format_str)

def parse_timestamp(timestamp_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> datetime:
    """Parse timestamp string"""
    try:
        return datetime.strptime(timestamp_str, format_str)
    except ValueError:
        return datetime.now()

def get_system_info() -> Dict:
    """Obter informações do sistema"""
    import platform
    import psutil
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total / (1024**3),  # GB
        'memory_available': psutil.virtual_memory().available / (1024**3),  # GB
        'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
    }

def send_notification(message: str, webhook_url: Optional[str] = None):
    """Enviar notificação via webhook"""
    if not webhook_url:
        logger.info(f"Notificação: {message}")
        return
    
    try:
        payload = {
            'text': message,
            'timestamp': datetime.now().isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.debug("Notificação enviada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")

def calculate_correlation(series1: pd.Series, series2: pd.Series, 
                         method: str = 'pearson') -> float:
    """Calcular correlação entre duas séries"""
    try:
        if len(series1) != len(series2) or len(series1) < 2:
            return 0
        
        correlation = series1.corr(series2, method=method)
        return correlation if not np.isnan(correlation) else 0
    except Exception:
        return 0

def normalize_data(data: pd.Series, method: str = 'minmax') -> pd.Series:
    """Normalizar dados"""
    if method == 'minmax':
        return (data - data.min()) / (data.max() - data.min())
    elif method == 'zscore':
        return (data - data.mean()) / data.std()
    else:
        return data

def calculate_volatility(prices: pd.Series, window: int = 20) -> float:
    """Calcular volatilidade"""
    if len(prices) < window:
        return 0
    
    returns = prices.pct_change().dropna()
    volatility = returns.rolling(window=window).std().iloc[-1]
    
    return volatility * np.sqrt(252) if not np.isnan(volatility) else 0  # Anualizada

def detect_outliers(data: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """Detectar outliers"""
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((data - data.mean()) / data.std())
        return z_scores > threshold
    
    return pd.Series([False] * len(data), index=data.index)

def smooth_data(data: pd.Series, method: str = 'ema', window: int = 5) -> pd.Series:
    """Suavizar dados"""
    if method == 'sma':
        return data.rolling(window=window).mean()
    elif method == 'ema':
        return data.ewm(span=window).mean()
    elif method == 'median':
        return data.rolling(window=window).median()
    else:
        return data

class Timer:
    """Context manager para medir tempo"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        logger.debug(f"{self.name} completado em {elapsed_time:.4f}s")

class ConfigValidator:
    """Validador de configurações"""
    
    @staticmethod
    def validate_api_keys(config) -> List[str]:
        """Validar chaves de API"""
        errors = []
        
        if not config.BINANCE_API_KEY:
            errors.append("BINANCE_API_KEY não configurada")        
        if not config.BINANCE_SECRET_KEY:
            errors.append("BINANCE_SECRET_KEY não configurada")
        
        return errors
    
    @staticmethod
    def validate_trading_pairs(config) -> List[str]:
        """Validar pares de trading - apenas crypto suportado"""
        errors = []
        
        if not config.CRYPTO_PAIRS:
            errors.append("Nenhum par de crypto configurado")
        
        return errors
    
    @staticmethod
    def validate_risk_settings(config) -> List[str]:
        """Validar configurações de risco"""
        errors = []
        
        if config.RISK_PER_TRADE <= 0 or config.RISK_PER_TRADE > 10:
            errors.append("RISK_PER_TRADE deve estar entre 0 e 10")
        
        if config.MAX_DAILY_LOSS <= 0 or config.MAX_DAILY_LOSS > 50:
            errors.append("MAX_DAILY_LOSS deve estar entre 0 e 50")
        
        if config.MAX_DRAWDOWN <= 0 or config.MAX_DRAWDOWN > 50:
            errors.append("MAX_DRAWDOWN deve estar entre 0 e 50")
        
        return errors