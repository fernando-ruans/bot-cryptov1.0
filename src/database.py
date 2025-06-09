#!/usr/bin/env python3
"""
Gerenciador de banco de dados para o trading bot
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador principal do banco de dados"""
    
    def __init__(self, db_path: str = 'data/trading_bot.db'):
        self.db_path = db_path
        self.ensure_directory_exists()
        
    def ensure_directory_exists(self):
        """Garantir que o diretório do banco existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões com o banco"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro na conexão com banco: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def initialize(self):
        """Inicializar banco de dados e criar tabelas"""
        try:
            with self.get_connection() as conn:
                self._create_tables(conn)
                logger.info("Banco de dados inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco: {e}")
            raise
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Criar todas as tabelas necessárias"""
        
        # Tabela de dados de mercado
        conn.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe, timestamp)
            )
        ''')
        
        # Tabela de sinais
        conn.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                entry_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                reasons TEXT,
                status TEXT DEFAULT 'active',
                ai_prediction TEXT,
                technical_analysis TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de posições
        conn.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0,
                status TEXT DEFAULT 'open',
                open_time DATETIME NOT NULL,
                close_time DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de trades executados
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                close_price REAL NOT NULL,
                realized_pnl REAL NOT NULL,
                return_pct REAL NOT NULL,
                open_time DATETIME NOT NULL,
                close_time DATETIME NOT NULL,
                close_reason TEXT,
                commission REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de performance diária
        conn.execute('''
            CREATE TABLE IF NOT EXISTS daily_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                total_pnl REAL DEFAULT 0,
                realized_pnl REAL DEFAULT 0,
                unrealized_pnl REAL DEFAULT 0,
                num_trades INTEGER DEFAULT 0,
                num_winning_trades INTEGER DEFAULT 0,
                num_losing_trades INTEGER DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de indicadores técnicos
        conn.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                indicators TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe, timestamp)
            )
        ''')
        
        # Tabela de configurações
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de logs do sistema
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar índices para melhor performance
        self._create_indexes(conn)
        
        conn.commit()
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Criar índices para otimização"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time ON market_data(symbol, timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_signals_symbol_time ON signals(symbol, timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)',
            'CREATE INDEX IF NOT EXISTS idx_trades_symbol_time ON trades(symbol, close_time)',
            'CREATE INDEX IF NOT EXISTS idx_daily_performance_date ON daily_performance(date)',
            'CREATE INDEX IF NOT EXISTS idx_technical_indicators_symbol_time ON technical_indicators(symbol, timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)'
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    
    # Métodos para dados de mercado
    def save_market_data(self, symbol: str, timeframe: str, df: pd.DataFrame):
        """Salvar dados de mercado"""
        try:
            with self.get_connection() as conn:
                for index, row in df.iterrows():
                    conn.execute('''
                        INSERT OR REPLACE INTO market_data 
                        (symbol, timeframe, timestamp, open_price, high_price, low_price, close_price, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol, timeframe, index, 
                        row['open'], row['high'], row['low'], row['close'], row['volume']
                    ))
                conn.commit()
                logger.debug(f"Dados de mercado salvos: {symbol} {timeframe} - {len(df)} registros")
        except Exception as e:
            logger.error(f"Erro ao salvar dados de mercado: {e}")
    
    def get_market_data(self, symbol: str, timeframe: str, 
                       start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Obter dados de mercado"""
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT timestamp, open_price as open, high_price as high, 
                           low_price as low, close_price as close, volume
                    FROM market_data 
                    WHERE symbol = ? AND timeframe = ?
                '''
                params = [symbol, timeframe]
                
                if start_date:
                    query += ' AND timestamp >= ?'
                    params.append(start_date)
                
                if end_date:
                    query += ' AND timestamp <= ?'
                    params.append(end_date)
                
                query += ' ORDER BY timestamp'
                
                df = pd.read_sql_query(query, conn, params=params, parse_dates=['timestamp'])
                df.set_index('timestamp', inplace=True)
                
                return df
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {e}")
            return pd.DataFrame()
    
    # Métodos para sinais
    def save_signal(self, signal_data: Dict):
        """Salvar sinal"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO signals 
                    (id, symbol, signal_type, confidence, entry_price, stop_loss, take_profit, 
                     timeframe, timestamp, reasons, status, ai_prediction, technical_analysis)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal_data['id'],
                    signal_data['symbol'],
                    signal_data['signal_type'],
                    signal_data['confidence'],
                    signal_data['entry_price'],
                    signal_data['stop_loss'],
                    signal_data['take_profit'],
                    signal_data['timeframe'],
                    signal_data['timestamp'],
                    json.dumps(signal_data.get('reasons', [])),
                    signal_data.get('status', 'active'),
                    json.dumps(signal_data.get('ai_prediction', {})),
                    json.dumps(signal_data.get('technical_analysis', {}))
                ))
                conn.commit()
                logger.debug(f"Sinal salvo: {signal_data['id']}")
        except Exception as e:
            logger.error(f"Erro ao salvar sinal: {e}")
    
    def get_signals(self, symbol: Optional[str] = None, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   status: Optional[str] = None) -> List[Dict]:
        """Obter sinais"""
        try:
            with self.get_connection() as conn:
                query = 'SELECT * FROM signals WHERE 1=1'
                params = []
                
                if symbol:
                    query += ' AND symbol = ?'
                    params.append(symbol)
                
                if start_date:
                    query += ' AND timestamp >= ?'
                    params.append(start_date)
                
                if end_date:
                    query += ' AND timestamp <= ?'
                    params.append(end_date)
                
                if status:
                    query += ' AND status = ?'
                    params.append(status)
                
                query += ' ORDER BY timestamp DESC'
                
                cursor = conn.execute(query, params)
                signals = []
                
                for row in cursor.fetchall():
                    signal = dict(row)
                    signal['reasons'] = json.loads(signal['reasons']) if signal['reasons'] else []
                    signal['ai_prediction'] = json.loads(signal['ai_prediction']) if signal['ai_prediction'] else {}
                    signal['technical_analysis'] = json.loads(signal['technical_analysis']) if signal['technical_analysis'] else {}
                    signals.append(signal)
                
                return signals
        except Exception as e:
            logger.error(f"Erro ao obter sinais: {e}")
            return []
    
    def update_signal_status(self, signal_id: str, status: str):
        """Atualizar status do sinal"""
        try:
            with self.get_connection() as conn:
                conn.execute('UPDATE signals SET status = ? WHERE id = ?', (status, signal_id))
                conn.commit()
                logger.debug(f"Status do sinal {signal_id} atualizado para {status}")
        except Exception as e:
            logger.error(f"Erro ao atualizar status do sinal: {e}")
    
    # Métodos para posições
    def save_position(self, position_data: Dict):
        """Salvar posição"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO positions 
                    (id, symbol, side, size, entry_price, current_price, stop_loss, 
                     take_profit, unrealized_pnl, status, open_time, close_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    position_data['id'],
                    position_data['symbol'],
                    position_data['side'],
                    position_data['size'],
                    position_data['entry_price'],
                    position_data.get('current_price'),
                    position_data['stop_loss'],
                    position_data['take_profit'],
                    position_data.get('unrealized_pnl', 0),
                    position_data.get('status', 'open'),
                    position_data['open_time'],
                    position_data.get('close_time')
                ))
                conn.commit()
                logger.debug(f"Posição salva: {position_data['id']}")
        except Exception as e:
            logger.error(f"Erro ao salvar posição: {e}")
    
    def get_positions(self, status: Optional[str] = None) -> List[Dict]:
        """Obter posições"""
        try:
            with self.get_connection() as conn:
                query = 'SELECT * FROM positions'
                params = []
                
                if status:
                    query += ' WHERE status = ?'
                    params.append(status)
                
                query += ' ORDER BY open_time DESC'
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter posições: {e}")
            return []
    
    def update_position(self, position_id: str, updates: Dict):
        """Atualizar posição"""
        try:
            with self.get_connection() as conn:
                set_clause = ', '.join([f'{key} = ?' for key in updates.keys()])
                values = list(updates.values()) + [position_id]
                
                conn.execute(f'UPDATE positions SET {set_clause} WHERE id = ?', values)
                conn.commit()
                logger.debug(f"Posição {position_id} atualizada")
        except Exception as e:
            logger.error(f"Erro ao atualizar posição: {e}")
    
    # Métodos para trades
    def save_trade(self, trade_data: Dict):
        """Salvar trade executado"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO trades 
                    (position_id, symbol, side, size, entry_price, close_price, 
                     realized_pnl, return_pct, open_time, close_time, close_reason, commission)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade_data['position_id'],
                    trade_data['symbol'],
                    trade_data['side'],
                    trade_data['size'],
                    trade_data['entry_price'],
                    trade_data['close_price'],
                    trade_data['realized_pnl'],
                    trade_data['return_pct'],
                    trade_data['open_time'],
                    trade_data['close_time'],
                    trade_data.get('close_reason'),
                    trade_data.get('commission', 0)
                ))
                conn.commit()
                logger.debug(f"Trade salvo: {trade_data['position_id']}")
        except Exception as e:
            logger.error(f"Erro ao salvar trade: {e}")
    
    def get_trades(self, symbol: Optional[str] = None,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None) -> List[Dict]:
        """Obter trades"""
        try:
            with self.get_connection() as conn:
                query = 'SELECT * FROM trades WHERE 1=1'
                params = []
                
                if symbol:
                    query += ' AND symbol = ?'
                    params.append(symbol)
                
                if start_date:
                    query += ' AND close_time >= ?'
                    params.append(start_date)
                
                if end_date:
                    query += ' AND close_time <= ?'
                    params.append(end_date)
                
                query += ' ORDER BY close_time DESC'
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter trades: {e}")
            return []
    
    # Métodos para performance
    def save_daily_performance(self, date: datetime.date, performance_data: Dict):
        """Salvar performance diária"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO daily_performance 
                    (date, total_pnl, realized_pnl, unrealized_pnl, num_trades, 
                     num_winning_trades, num_losing_trades, max_drawdown)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date,
                    performance_data.get('total_pnl', 0),
                    performance_data.get('realized_pnl', 0),
                    performance_data.get('unrealized_pnl', 0),
                    performance_data.get('num_trades', 0),
                    performance_data.get('num_winning_trades', 0),
                    performance_data.get('num_losing_trades', 0),
                    performance_data.get('max_drawdown', 0)
                ))
                conn.commit()
                logger.debug(f"Performance diária salva: {date}")
        except Exception as e:
            logger.error(f"Erro ao salvar performance diária: {e}")
    
    def get_performance_history(self, days: int = 30) -> List[Dict]:
        """Obter histórico de performance"""
        try:
            with self.get_connection() as conn:
                start_date = datetime.now().date() - timedelta(days=days)
                
                cursor = conn.execute('''
                    SELECT * FROM daily_performance 
                    WHERE date >= ? 
                    ORDER BY date DESC
                ''', (start_date,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter histórico de performance: {e}")
            return []
    
    # Métodos para indicadores técnicos
    def save_technical_indicators(self, symbol: str, timeframe: str, 
                                timestamp: datetime, indicators: Dict):
        """Salvar indicadores técnicos"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO technical_indicators 
                    (symbol, timeframe, timestamp, indicators)
                    VALUES (?, ?, ?, ?)
                ''', (symbol, timeframe, timestamp, json.dumps(indicators)))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar indicadores técnicos: {e}")
    
    # Métodos para configurações
    def save_setting(self, key: str, value: Any):
        """Salvar configuração"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value)))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def get_setting(self, key: str, default=None):
        """Obter configuração"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT value FROM settings WHERE key = ?', (key,))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row['value'])
                return default
        except Exception as e:
            logger.error(f"Erro ao obter configuração: {e}")
            return default
    
    # Métodos para logs
    def save_log(self, level: str, message: str, module: Optional[str] = None):
        """Salvar log do sistema"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO system_logs (level, message, module)
                    VALUES (?, ?, ?)
                ''', (level, message, module))
                conn.commit()
        except Exception as e:
            # Não logar erro de log para evitar recursão
            pass
    
    def get_logs(self, level: Optional[str] = None, 
                hours: int = 24) -> List[Dict]:
        """Obter logs do sistema"""
        try:
            with self.get_connection() as conn:
                start_time = datetime.now() - timedelta(hours=hours)
                
                query = 'SELECT * FROM system_logs WHERE timestamp >= ?'
                params = [start_time]
                
                if level:
                    query += ' AND level = ?'
                    params.append(level)
                
                query += ' ORDER BY timestamp DESC LIMIT 1000'
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao obter logs: {e}")
            return []
    
    # Métodos de limpeza
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Limpar dados antigos"""
        try:
            with self.get_connection() as conn:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Limpar dados de mercado antigos
                conn.execute('DELETE FROM market_data WHERE created_at < ?', (cutoff_date,))
                
                # Limpar logs antigos
                conn.execute('DELETE FROM system_logs WHERE timestamp < ?', (cutoff_date,))
                
                # Limpar indicadores técnicos antigos
                conn.execute('DELETE FROM technical_indicators WHERE created_at < ?', (cutoff_date,))
                
                conn.commit()
                logger.info(f"Dados antigos limpos (mais de {days_to_keep} dias)")
        except Exception as e:
            logger.error(f"Erro ao limpar dados antigos: {e}")
    
    def backup_database(self, backup_path: str):
        """Fazer backup do banco de dados"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Backup criado: {backup_path}")
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
    
    def get_database_stats(self) -> Dict:
        """Obter estatísticas do banco de dados"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                tables = ['market_data', 'signals', 'positions', 'trades', 
                         'daily_performance', 'technical_indicators', 'system_logs']
                
                for table in tables:
                    cursor = conn.execute(f'SELECT COUNT(*) as count FROM {table}')
                    stats[table] = cursor.fetchone()['count']
                
                # Tamanho do arquivo
                stats['file_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                
                return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do banco: {e}")
            return {}