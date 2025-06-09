#!/usr/bin/env python3
"""
Gerenciador de risco para trading
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class Position:
    """Classe para representar uma posição de trading"""
    
    def __init__(self, symbol: str, side: str, size: float, entry_price: float,
                 stop_loss: float, take_profit: float, timestamp: datetime):
        self.symbol = symbol
        self.side = side  # 'long' or 'short'
        self.size = size
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.timestamp = timestamp
        self.current_price = entry_price
        self.unrealized_pnl = 0.0
        self.status = 'open'
        self.id = f"{symbol}_{side}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def update_price(self, current_price: float):
        """Atualizar preço atual e PnL"""
        self.current_price = current_price
        
        if self.side == 'long':
            self.unrealized_pnl = (current_price - self.entry_price) * self.size
        else:  # short
            self.unrealized_pnl = (self.entry_price - current_price) * self.size
    
    def get_return_pct(self) -> float:
        """Calcular retorno percentual"""
        if self.side == 'long':
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.current_price) / self.entry_price) * 100
    
    def should_close(self) -> Tuple[bool, str]:
        """Verificar se posição deve ser fechada"""
        if self.side == 'long':
            if self.current_price <= self.stop_loss:
                return True, 'stop_loss'
            elif self.current_price >= self.take_profit:
                return True, 'take_profit'
        else:  # short
            if self.current_price >= self.stop_loss:
                return True, 'stop_loss'
            elif self.current_price <= self.take_profit:
                return True, 'take_profit'
        
        return False, ''
    
    def to_dict(self) -> Dict:
        """Converter posição para dicionário"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'unrealized_pnl': self.unrealized_pnl,
            'return_pct': self.get_return_pct(),
            'timestamp': self.timestamp.isoformat(),
            'status': self.status
        }

class RiskManager:
    """Gerenciador de risco principal"""
    
    def __init__(self, config):
        self.config = config
        self.positions = {}
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_equity = 0.0
        self.trade_history = []
        self.daily_reset_time = None
        
    def validate_signal(self, signal_data: Dict, account_balance: float) -> Dict:
        """Validar sinal antes de executar trade"""
        try:
            validation_result = {
                'valid': True,
                'reasons': [],
                'suggested_size': 0.0,
                'risk_level': 'low'
            }
            
            symbol = signal_data.get('symbol')
            signal_type = signal_data.get('signal_type')
            confidence = signal_data.get('confidence', 0)
            entry_price = signal_data.get('entry_price', 0)
            
            # Verificar se já existe posição para o símbolo
            existing_position = self._get_position_by_symbol(symbol)
            if existing_position:
                validation_result['valid'] = False
                validation_result['reasons'].append(f"Posição já existe para {symbol}")
                return validation_result
            
            # Verificar número máximo de posições
            if len(self.positions) >= self.config.RISK_MANAGEMENT['max_open_positions']:
                validation_result['valid'] = False
                validation_result['reasons'].append("Número máximo de posições atingido")
                return validation_result
            
            # Verificar perda diária máxima
            max_daily_loss = self.config.RISK_MANAGEMENT['max_daily_loss']
            if self.daily_pnl < -(account_balance * max_daily_loss):
                validation_result['valid'] = False
                validation_result['reasons'].append("Perda diária máxima atingida")
                return validation_result
            
            # Calcular tamanho da posição
            position_size = self._calculate_position_size(
                account_balance, entry_price, signal_data.get('stop_loss', entry_price), confidence
            )
            
            if position_size <= 0:
                validation_result['valid'] = False
                validation_result['reasons'].append("Tamanho de posição inválido")
                return validation_result
            
            validation_result['suggested_size'] = position_size
            
            # Avaliar nível de risco
            risk_level = self._assess_risk_level(signal_data, account_balance, position_size)
            validation_result['risk_level'] = risk_level
            
            # Verificações adicionais baseadas no nível de risco
            if risk_level == 'high':
                if confidence < 0.8:
                    validation_result['valid'] = False
                    validation_result['reasons'].append("Confiança insuficiente para trade de alto risco")
                    return validation_result
            
            validation_result['reasons'].append(f"Trade validado - Risco: {risk_level}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Erro na validação do sinal: {e}")
            return {'valid': False, 'reasons': [f"Erro na validação: {e}"], 'suggested_size': 0.0}
    
    def _calculate_position_size(self, account_balance: float, entry_price: float, 
                                stop_loss: float, confidence: float) -> float:
        """Calcular tamanho da posição baseado no risco"""
        try:
            # Risco máximo por trade
            max_risk_per_trade = self.config.RISK_MANAGEMENT['max_risk_per_trade']
            
            # Calcular risco em dólares
            risk_amount = account_balance * max_risk_per_trade
            
            # Calcular distância do stop loss
            stop_distance = abs(entry_price - stop_loss)
            
            if stop_distance == 0:
                return 0.0
            
            # Calcular tamanho base da posição
            base_size = risk_amount / stop_distance
            
            # Ajustar baseado na confiança
            confidence_multiplier = min(confidence * 1.5, 1.0)
            adjusted_size = base_size * confidence_multiplier
            
            # Limitar a um percentual máximo do saldo
            max_position_value = account_balance * 0.2  # Máximo 20% do saldo por posição
            max_size = max_position_value / entry_price
            
            return min(adjusted_size, max_size)
            
        except Exception as e:
            logger.error(f"Erro ao calcular tamanho da posição: {e}")
            return 0.0
    
    def _assess_risk_level(self, signal_data: Dict, account_balance: float, position_size: float) -> str:
        """Avaliar nível de risco do trade"""
        try:
            risk_factors = 0
            
            # Fator 1: Tamanho da posição
            position_value = position_size * signal_data.get('entry_price', 0)
            position_pct = position_value / account_balance
            
            if position_pct > 0.15:
                risk_factors += 2
            elif position_pct > 0.1:
                risk_factors += 1
            
            # Fator 2: Confiança do sinal
            confidence = signal_data.get('confidence', 0)
            if confidence < 0.6:
                risk_factors += 2
            elif confidence < 0.75:
                risk_factors += 1
            
            # Fator 3: Volatilidade do ativo
            # (Seria calculado com dados históricos)
            
            # Fator 4: Correlação com posições existentes
            correlation_risk = self._calculate_correlation_risk(signal_data.get('symbol'))
            risk_factors += correlation_risk
            
            # Fator 5: Condições de mercado
            # (Seria baseado em indicadores de mercado)
            
            if risk_factors >= 4:
                return 'high'
            elif risk_factors >= 2:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Erro ao avaliar risco: {e}")
            return 'medium'
    
    def _calculate_correlation_risk(self, symbol: str) -> int:
        """Calcular risco de correlação com posições existentes"""
        try:
            # Verificar se há posições correlacionadas
            correlated_positions = 0
            
            for position in self.positions.values():
                if position.symbol != symbol:
                    # Verificar correlação (simplificado)
                    if self._are_correlated(symbol, position.symbol):
                        correlated_positions += 1
            
            if correlated_positions >= 3:
                return 2
            elif correlated_positions >= 1:
                return 1
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Erro ao calcular risco de correlação: {e}")
            return 0
    
    def _are_correlated(self, symbol1: str, symbol2: str) -> bool:
        """Verificar se dois símbolos são correlacionados"""
        # Correlações conhecidas (simplificado)
        crypto_pairs = self.config.CRYPTO_PAIRS
        forex_pairs = self.config.FOREX_PAIRS
        
        # Criptomoedas são geralmente correlacionadas
        if symbol1 in crypto_pairs and symbol2 in crypto_pairs:
            return True
        
        # Pares de forex com moedas comuns
        if symbol1 in forex_pairs and symbol2 in forex_pairs:
            if symbol1[:3] == symbol2[:3] or symbol1[3:] == symbol2[3:]:
                return True
            if symbol1[:3] == symbol2[3:] or symbol1[3:] == symbol2[:3]:
                return True
        
        return False
    
    def open_position(self, signal_data: Dict, position_size: float) -> Optional[Position]:
        """Abrir nova posição"""
        try:
            symbol = signal_data['symbol']
            signal_type = signal_data['signal_type']
            entry_price = signal_data['entry_price']
            stop_loss = signal_data['stop_loss']
            take_profit = signal_data['take_profit']
            
            # Converter tipo de sinal para lado da posição
            side = 'long' if signal_type == 'buy' else 'short'
            
            # Criar posição
            position = Position(
                symbol=symbol,
                side=side,
                size=position_size,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timestamp=datetime.now()
            )
            
            # Adicionar às posições ativas
            self.positions[position.id] = position
            
            logger.info(f"Posição aberta: {position.id} - {side} {symbol} @ {entry_price}")
            
            return position
            
        except Exception as e:
            logger.error(f"Erro ao abrir posição: {e}")
            return None
    
    def close_position(self, position_id: str, close_price: float, reason: str = 'manual') -> Dict:
        """Fechar posição"""
        try:
            if position_id not in self.positions:
                return {'success': False, 'error': 'Posição não encontrada'}
            
            position = self.positions[position_id]
            
            # Calcular PnL realizado
            if position.side == 'long':
                realized_pnl = (close_price - position.entry_price) * position.size
            else:
                realized_pnl = (position.entry_price - close_price) * position.size
            
            # Atualizar estatísticas
            self.daily_pnl += realized_pnl
            self.total_pnl += realized_pnl
            
            # Registrar trade no histórico
            trade_record = {
                'position_id': position_id,
                'symbol': position.symbol,
                'side': position.side,
                'size': position.size,
                'entry_price': position.entry_price,
                'close_price': close_price,
                'realized_pnl': realized_pnl,
                'return_pct': (realized_pnl / (position.entry_price * position.size)) * 100,
                'open_time': position.timestamp,
                'close_time': datetime.now(),
                'close_reason': reason
            }
            
            self.trade_history.append(trade_record)
            
            # Remover posição
            position.status = 'closed'
            del self.positions[position_id]
            
            logger.info(f"Posição fechada: {position_id} - PnL: {realized_pnl:.2f}")
            
            return {
                'success': True,
                'realized_pnl': realized_pnl,
                'trade_record': trade_record
            }
            
        except Exception as e:
            logger.error(f"Erro ao fechar posição: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_positions(self, market_prices: Dict[str, float]):
        """Atualizar todas as posições com preços atuais"""
        try:
            positions_to_close = []
            
            for position_id, position in self.positions.items():
                if position.symbol in market_prices:
                    current_price = market_prices[position.symbol]
                    position.update_price(current_price)
                    
                    # Verificar se deve fechar
                    should_close, reason = position.should_close()
                    if should_close:
                        positions_to_close.append((position_id, current_price, reason))
            
            # Fechar posições que atingiram stop loss ou take profit
            for position_id, close_price, reason in positions_to_close:
                self.close_position(position_id, close_price, reason)
            
            # Atualizar drawdown
            self._update_drawdown()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar posições: {e}")
    
    def _update_drawdown(self):
        """Atualizar máximo drawdown"""
        try:
            current_equity = self.total_pnl + sum(pos.unrealized_pnl for pos in self.positions.values())
            
            if current_equity > self.peak_equity:
                self.peak_equity = current_equity
            
            current_drawdown = (self.peak_equity - current_equity) / max(self.peak_equity, 1) * 100
            
            if current_drawdown > self.max_drawdown:
                self.max_drawdown = current_drawdown
                
        except Exception as e:
            logger.error(f"Erro ao atualizar drawdown: {e}")
    
    def _get_position_by_symbol(self, symbol: str) -> Optional[Position]:
        """Obter posição por símbolo"""
        for position in self.positions.values():
            if position.symbol == symbol:
                return position
        return None
    
    def get_portfolio_summary(self) -> Dict:
        """Obter resumo do portfólio"""
        try:
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            
            # Estatísticas de trades
            if self.trade_history:
                winning_trades = [t for t in self.trade_history if t['realized_pnl'] > 0]
                losing_trades = [t for t in self.trade_history if t['realized_pnl'] < 0]
                
                win_rate = len(winning_trades) / len(self.trade_history) * 100
                avg_win = np.mean([t['realized_pnl'] for t in winning_trades]) if winning_trades else 0
                avg_loss = np.mean([t['realized_pnl'] for t in losing_trades]) if losing_trades else 0
                profit_factor = abs(sum(t['realized_pnl'] for t in winning_trades) / 
                                  sum(t['realized_pnl'] for t in losing_trades)) if losing_trades else float('inf')
            else:
                win_rate = 0
                avg_win = 0
                avg_loss = 0
                profit_factor = 0
            
            return {
                'open_positions': len(self.positions),
                'total_realized_pnl': self.total_pnl,
                'total_unrealized_pnl': total_unrealized_pnl,
                'daily_pnl': self.daily_pnl,
                'max_drawdown': self.max_drawdown,
                'total_trades': len(self.trade_history),
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'positions': [pos.to_dict() for pos in self.positions.values()]
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo do portfólio: {e}")
            return {}
    
    def reset_daily_stats(self):
        """Resetar estatísticas diárias"""
        try:
            current_time = datetime.now()
            
            # Resetar apenas uma vez por dia
            if (self.daily_reset_time is None or 
                current_time.date() > self.daily_reset_time.date()):
                
                self.daily_pnl = 0.0
                self.daily_reset_time = current_time
                
                logger.info("Estatísticas diárias resetadas")
                
        except Exception as e:
            logger.error(f"Erro ao resetar estatísticas diárias: {e}")
    
    def get_risk_metrics(self) -> Dict:
        """Obter métricas de risco"""
        try:
            if not self.trade_history:
                return {}
            
            returns = [t['return_pct'] for t in self.trade_history]
            
            # Sharpe Ratio (simplificado)
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
            
            # Sortino Ratio
            negative_returns = [r for r in returns if r < 0]
            downside_std = np.std(negative_returns) if negative_returns else 0
            sortino_ratio = avg_return / downside_std if downside_std > 0 else 0
            
            # Maximum Consecutive Losses
            consecutive_losses = 0
            max_consecutive_losses = 0
            
            for trade in self.trade_history:
                if trade['realized_pnl'] < 0:
                    consecutive_losses += 1
                    max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
                else:
                    consecutive_losses = 0
            
            return {
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_consecutive_losses': max_consecutive_losses,
                'avg_return': avg_return,
                'volatility': std_return,
                'max_drawdown': self.max_drawdown
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de risco: {e}")
            return {}
    
    def should_stop_trading(self) -> Tuple[bool, str]:
        """Verificar se deve parar de fazer trades"""
        try:
            # Verificar perda diária máxima
            max_daily_loss_pct = self.config.RISK_MANAGEMENT['max_daily_loss']
            if hasattr(self, 'account_balance'):
                max_daily_loss = self.account_balance * max_daily_loss_pct
                if self.daily_pnl <= -max_daily_loss:
                    return True, "Perda diária máxima atingida"
            
            # Verificar drawdown máximo
            if self.max_drawdown > 20:  # 20% drawdown
                return True, "Drawdown máximo atingido"
            
            # Verificar perdas consecutivas
            risk_metrics = self.get_risk_metrics()
            if risk_metrics.get('max_consecutive_losses', 0) >= 5:
                return True, "Muitas perdas consecutivas"
            
            return False, ""
            
        except Exception as e:
            logger.error(f"Erro ao verificar se deve parar trading: {e}")
            return False, ""