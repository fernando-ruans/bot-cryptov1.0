#!/usr/bin/env python3
"""
Paper Trading Manager
Gerencia trades virtuais para simulação e tracking de performance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class PaperTrade:
    """Classe para representar um trade virtual"""
    
    def __init__(self, signal_id: str, symbol: str, trade_type: str, 
                 entry_price: float, stop_loss: float, take_profit: float,
                 timestamp: datetime, signal_confidence: float):
        self.id = str(uuid.uuid4())
        self.signal_id = signal_id
        self.symbol = symbol
        self.trade_type = trade_type  # 'buy' or 'sell'
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.timestamp = timestamp
        self.signal_confidence = signal_confidence
        
        # Status do trade
        self.status = 'active'  # 'active', 'closed', 'stopped'
        self.exit_price = None
        self.exit_timestamp = None
        self.exit_reason = None  # 'profit', 'loss', 'manual'
        self.pnl = 0.0
        self.pnl_percent = 0.0
        
        # Tracking de preços
        self.current_price = entry_price
        self.max_price = entry_price
        self.min_price = entry_price
        
    def update_price(self, current_price: float) -> bool:
        """
        Atualiza preço atual e verifica se deve fechar o trade
        Retorna True se o trade foi fechado
        """
        self.current_price = current_price
        self.max_price = max(self.max_price, current_price)
        self.min_price = min(self.min_price, current_price)
        
        if self.status != 'active':
            return False
            
        # Verificar stop loss e take profit
        if self.trade_type == 'buy':
            # Trade de compra
            if current_price <= self.stop_loss:
                self._close_trade(current_price, 'loss')
                return True
            elif current_price >= self.take_profit:
                self._close_trade(current_price, 'profit')
                return True
        else:
            # Trade de venda
            if current_price >= self.stop_loss:
                self._close_trade(current_price, 'loss')
                return True
            elif current_price <= self.take_profit:
                self._close_trade(current_price, 'profit')
                return True
                
        return False
    
    def _close_trade(self, exit_price: float, reason: str):
        """Fecha o trade com preço e motivo especificados"""
        self.exit_price = exit_price
        self.exit_timestamp = datetime.now()
        self.exit_reason = reason
        self.status = 'closed'
        
        # Calcular P&L
        if self.trade_type == 'buy':
            self.pnl = exit_price - self.entry_price
            self.pnl_percent = (exit_price / self.entry_price - 1) * 100
        else:
            self.pnl = self.entry_price - exit_price
            self.pnl_percent = (self.entry_price / exit_price - 1) * 100
    
    def close_manually(self, exit_price: float):
        """Fecha o trade manualmente"""
        if self.status == 'active':
            self._close_trade(exit_price, 'manual')
    
    def get_current_pnl(self) -> Tuple[float, float]:
        """Retorna P&L atual (absoluto, percentual)"""
        if self.status != 'active':
            return self.pnl, self.pnl_percent
            
        if self.trade_type == 'buy':
            pnl = self.current_price - self.entry_price
            pnl_percent = (self.current_price / self.entry_price - 1) * 100
        else:
            pnl = self.entry_price - self.current_price
            pnl_percent = (self.entry_price / self.current_price - 1) * 100
            
        return pnl, pnl_percent
    
    def to_dict(self) -> Dict:
        """Converter trade para dicionário"""
        current_pnl, current_pnl_percent = self.get_current_pnl()
        
        return {
            'id': self.id,
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'trade_type': self.trade_type,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'timestamp': self.timestamp.isoformat(),
            'signal_confidence': self.signal_confidence,
            'status': self.status,
            'exit_price': self.exit_price,
            'exit_timestamp': self.exit_timestamp.isoformat() if self.exit_timestamp else None,
            'exit_reason': self.exit_reason,
            'pnl': self.pnl if self.status == 'closed' else current_pnl,
            'pnl_percent': self.pnl_percent if self.status == 'closed' else current_pnl_percent,
            'current_price': self.current_price,
            'max_price': self.max_price,
            'min_price': self.min_price
        }

class PaperTradingManager:
    """Gerenciador de trades virtuais (paper trading)"""
    
    def __init__(self, market_data_manager):
        self.market_data = market_data_manager
        self.active_trades = {}  # {trade_id: PaperTrade}
        self.trade_history = []  # Lista de trades fechados
        self.portfolio_balance = 10000.0  # Saldo inicial virtual
        self.initial_balance = 10000.0
        
        # Estatísticas
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        
    def create_trade_from_signal(self, signal) -> str:
        """
        Cria um trade virtual a partir de um sinal
        Retorna o ID do trade criado
        """
        try:
            trade = PaperTrade(
                signal_id=signal.id,
                symbol=signal.symbol,
                trade_type=signal.signal_type,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                timestamp=datetime.now(),
                signal_confidence=signal.confidence
            )
            
            self.active_trades[trade.id] = trade
            self.total_trades += 1
            
            logger.info(f"✅ Paper trade criado: {trade.trade_type} {trade.symbol} @ ${trade.entry_price:.2f}")
            logger.info(f"   SL: ${trade.stop_loss:.2f}, TP: ${trade.take_profit:.2f}")
            logger.info(f"   Confiança do sinal: {trade.signal_confidence:.1%}")
            
            return trade.id
            
        except Exception as e:
            logger.error(f"Erro ao criar paper trade: {e}")
            return None
    
    def update_prices(self):
        """Atualiza preços de todos os trades ativos"""
        closed_trades = []
        
        for trade_id, trade in self.active_trades.items():
            try:
                # Obter preço atual
                current_price = self.market_data.get_current_price(trade.symbol)
                if current_price is None:
                    continue
                
                # Atualizar preço do trade
                was_closed = trade.update_price(current_price)
                
                if was_closed:
                    closed_trades.append(trade_id)
                    self._process_closed_trade(trade)
                    
            except Exception as e:
                logger.error(f"Erro ao atualizar preço do trade {trade_id}: {e}")
        
        # Remover trades fechados da lista ativa
        for trade_id in closed_trades:
            if trade_id in self.active_trades:
                del self.active_trades[trade_id]
    
    def _process_closed_trade(self, trade: PaperTrade):
        """Processa um trade que foi fechado"""
        self.trade_history.append(trade)
          # Atualizar estatísticas
        if trade.pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
            
        self.total_pnl += trade.pnl
        logger.info(f"🔚 Paper trade fechado: {trade.symbol} {trade.trade_type}")
        logger.info(f"   Motivo: {trade.exit_reason}")
        logger.info(f"   P&L: ${trade.pnl:.2f} ({trade.pnl_percent:.2f}%)")
        logger.info(f"   Entry: ${trade.entry_price:.2f} → Exit: ${trade.exit_price:.2f}")
    
    def confirm_signal(self, signal_data, amount=1000):
        """
        Confirma um sinal e cria um trade virtual
        
        Args:
            signal_data (dict): Dados do sinal com keys: signal_type, symbol, entry_price, etc.
            amount (float): Valor do trade (não usado no paper trading, apenas para referência)
              Returns:
            PaperTrade: Objeto do trade criado ou None se erro
        """
        try:
            # Criar objeto de sinal a partir dos dados
            class SignalObj:
                def __init__(self, data):
                    self.id = data.get('id', f"{data['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    self.symbol = data['symbol']
                    self.signal_type = data['signal_type']
                    self.entry_price = data['entry_price']
                    self.confidence = data.get('confidence', 0.5)
                      # Usar os valores de SL e TP que já vêm calculados do signal_generator
                    # Isso preserva os ajustes feitos para timeframes curtos
                    self.stop_loss = data.get('stop_loss')
                    self.take_profit = data.get('take_profit')
                      # Se não tiver os valores, algo está errado - não usar fallbacks fixos
                    if self.stop_loss is None or self.take_profit is None:
                        logger.error(f"❌ ERRO: Stop Loss ou Take Profit não fornecidos no sinal!")
                        logger.error(f"   Dados recebidos: {list(data.keys())}")
                        raise ValueError("Stop Loss e Take Profit devem ser fornecidos no sinal")
                        
                    logger.info(f"🔧 Paper trade usando valores do sinal:")
                    logger.info(f"   Entry: ${self.entry_price:.2f}")
                    logger.info(f"   Stop Loss: ${self.stop_loss:.2f}")
                    logger.info(f"   Take Profit: ${self.take_profit:.2f}")
            
            logger.info(f"🚀 Criando SignalObj com dados:")
            logger.info(f"   SL recebido: {signal_data.get('stop_loss')}")
            logger.info(f"   TP recebido: {signal_data.get('take_profit')}")
            
            signal_obj = SignalObj(signal_data)
            
            logger.info(f"📋 SignalObj criado:")
            logger.info(f"   signal_obj.stop_loss: {signal_obj.stop_loss}")
            logger.info(f"   signal_obj.take_profit: {signal_obj.take_profit}")
            
            trade_id = self.create_trade_from_signal(signal_obj)
            
            if trade_id:
                return self.active_trades[trade_id]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro ao confirmar sinal: {e}")
            return None
    
    def close_trade_manually(self, trade_id: str) -> bool:
        """Fecha um trade manualmente"""
        if trade_id not in self.active_trades:
            return False
            
        trade = self.active_trades[trade_id]
        
        # Obter preço atual para fechamento
        current_price = self.market_data.get_current_price(trade.symbol)
        if current_price is None:
            return False
            
        trade.close_manually(current_price)
        self._process_closed_trade(trade)
        
        del self.active_trades[trade_id]
        return True
    
    def get_portfolio_stats(self) -> Dict:
        """Retorna estatísticas do portfólio"""
        # Calcular P&L total incluindo trades ativos
        total_pnl = self.total_pnl
        for trade in self.active_trades.values():
            current_pnl, _ = trade.get_current_pnl()
            total_pnl += current_pnl
        
        current_balance = self.initial_balance + total_pnl
        total_return = (current_balance / self.initial_balance - 1) * 100
        
        win_rate = (self.winning_trades / max(self.total_trades - len(self.active_trades), 1)) * 100
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': current_balance,
            'total_pnl': total_pnl,
            'total_return_percent': total_return,
            'total_trades': self.total_trades,
            'active_trades': len(self.active_trades),
            'closed_trades': len(self.trade_history),
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate
        }
    
    def get_active_trades(self) -> List[Dict]:
        """Retorna lista de trades ativos"""
        return [trade.to_dict() for trade in self.active_trades.values()]
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de trades"""
        return [trade.to_dict() for trade in self.trade_history[-limit:]]
    
    def get_trade_by_id(self, trade_id: str) -> Optional[Dict]:
        """Retorna trade específico por ID"""
        if trade_id in self.active_trades:
            return self.active_trades[trade_id].to_dict()
        
        for trade in self.trade_history:
            if trade.id == trade_id:
                return trade.to_dict()
                
        return None
