#!/usr/bin/env python3
"""
Gerador de dados mock para APIs do CryptoBot Dashboard
Cria dados realistas para desenvolvimento e testes
"""

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

class MockDataGenerator:
    def __init__(self):
        self.crypto_pairs = [
            'BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT',
            'SOL/USDT', 'MATIC/USDT', 'AVAX/USDT', 'LUNA/USDT', 'ATOM/USDT'
        ]
        
        self.base_prices = {
            'BTC/USDT': 45000,
            'ETH/USDT': 3200,
            'ADA/USDT': 0.85,
            'DOT/USDT': 12.5,
            'LINK/USDT': 18.3,
            'SOL/USDT': 95.7,
            'MATIC/USDT': 1.25,
            'AVAX/USDT': 78.4,
            'LUNA/USDT': 85.2,
            'ATOM/USDT': 28.6
        }
    
    def generate_price_data(self):
        """Gera dados de preços em tempo real"""
        prices = {}
        
        for pair in self.crypto_pairs:
            base_price = self.base_prices[pair]
            
            # Variação aleatória (-5% a +5%)
            change_percent = random.uniform(-5, 5)
            current_price = base_price * (1 + change_percent / 100)
            
            # Volume 24h
            volume_24h = random.uniform(1000000, 50000000)
            
            # High/Low 24h
            high_24h = current_price * random.uniform(1.01, 1.08)
            low_24h = current_price * random.uniform(0.92, 0.99)
            
            prices[pair] = {
                'symbol': pair,
                'price': round(current_price, 6),
                'change_24h': round(change_percent, 2),
                'volume_24h': round(volume_24h, 2),
                'high_24h': round(high_24h, 6),
                'low_24h': round(low_24h, 6),
                'last_update': datetime.now().isoformat(),
                'trend': 'up' if change_percent > 0 else 'down',
                'market_cap': round(current_price * random.uniform(1000000, 100000000), 2)
            }
        
        return prices
    
    def generate_signals(self, count=10):
        """Gera sinais de trading"""
        signals = []
        signal_types = ['BUY', 'SELL', 'HOLD']
        
        for i in range(count):
            pair = random.choice(self.crypto_pairs)
            signal_type = random.choice(signal_types)
            
            # Confidence baseada no tipo
            if signal_type == 'HOLD':
                confidence = random.uniform(60, 80)
            else:
                confidence = random.uniform(70, 95)
            
            # Timestamp variado
            timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
            
            # Preço de entrada/saída
            base_price = self.base_prices[pair]
            entry_price = base_price * random.uniform(0.98, 1.02)
            
            if signal_type == 'BUY':
                target_price = entry_price * random.uniform(1.02, 1.08)
                stop_loss = entry_price * random.uniform(0.95, 0.98)
            elif signal_type == 'SELL':
                target_price = entry_price * random.uniform(0.92, 0.98)
                stop_loss = entry_price * random.uniform(1.02, 1.05)
            else:  # HOLD
                target_price = entry_price
                stop_loss = entry_price
            
            signal = {
                'id': i + 1,
                'pair': pair,
                'type': signal_type,
                'confidence': round(confidence, 1),
                'entry_price': round(entry_price, 6),
                'target_price': round(target_price, 6),
                'stop_loss': round(stop_loss, 6),
                'timestamp': timestamp.isoformat(),
                'status': random.choice(['active', 'completed', 'cancelled']),
                'ai_reasoning': self._generate_ai_reasoning(signal_type, pair),
                'risk_level': random.choice(['low', 'medium', 'high']),
                'timeframe': random.choice(['1h', '4h', '1d', '1w'])
            }
            
            signals.append(signal)
        
        # Ordenar por timestamp (mais recente primeiro)
        signals.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return signals
    
    def generate_trades(self, count=20):
        """Gera histórico de trades"""
        trades = []
        
        for i in range(count):
            pair = random.choice(self.crypto_pairs)
            trade_type = random.choice(['BUY', 'SELL'])
            
            # Quantidade baseada no par
            if 'BTC' in pair:
                amount = round(random.uniform(0.001, 0.1), 6)
            elif 'ETH' in pair:
                amount = round(random.uniform(0.01, 1.0), 4)
            else:
                amount = round(random.uniform(1, 1000), 2)
            
            # Preço baseado no par
            base_price = self.base_prices[pair]
            price = base_price * random.uniform(0.95, 1.05)
            
            # Resultado do trade
            is_profit = random.choice([True, True, True, False])  # 75% profit
            if is_profit:
                pnl_percent = random.uniform(0.5, 8.0)
                status = 'completed_profit'
            else:
                pnl_percent = random.uniform(-5.0, -0.5)
                status = 'completed_loss'
            
            pnl_amount = amount * price * (pnl_percent / 100)
            
            # Timestamp
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 168))
            
            trade = {
                'id': i + 1,
                'pair': pair,
                'type': trade_type,
                'amount': amount,
                'price': round(price, 6),
                'total': round(amount * price, 2),
                'fee': round(amount * price * 0.001, 6),  # 0.1% fee
                'pnl_percent': round(pnl_percent, 2),
                'pnl_amount': round(pnl_amount, 6),
                'status': status,
                'timestamp': timestamp.isoformat(),
                'signal_id': random.randint(1, 10) if random.choice([True, False]) else None,
                'exchange': random.choice(['Binance', 'Coinbase', 'Kraken', 'KuCoin'])
            }
            
            trades.append(trade)
        
        # Ordenar por timestamp (mais recente primeiro)
        trades.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return trades
    
    def generate_portfolio_stats(self):
        """Gera estatísticas do portfolio"""
        
        # Calcular estatísticas baseadas nos trades
        total_trades = random.randint(100, 500)
        winning_trades = int(total_trades * random.uniform(0.65, 0.85))
        losing_trades = total_trades - winning_trades
        
        win_rate = (winning_trades / total_trades) * 100
        
        # Portfolio value
        initial_balance = 10000
        current_balance = initial_balance * random.uniform(1.05, 1.8)
        total_pnl = current_balance - initial_balance
        total_pnl_percent = (total_pnl / initial_balance) * 100
        
        # Risk metrics
        max_drawdown = random.uniform(-15, -5)
        sharpe_ratio = random.uniform(1.2, 2.8)
        
        # Active positions
        active_positions = random.randint(3, 8)
        
        stats = {
            'portfolio': {
                'total_value': round(current_balance, 2),
                'initial_value': initial_balance,
                'total_pnl': round(total_pnl, 2),
                'total_pnl_percent': round(total_pnl_percent, 2),
                'available_balance': round(current_balance * 0.3, 2),
                'invested_balance': round(current_balance * 0.7, 2),
                'last_update': datetime.now().isoformat()
            },
            'trading': {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 1),
                'active_positions': active_positions,
                'avg_profit': round(random.uniform(2, 8), 2),
                'avg_loss': round(random.uniform(-3, -1), 2),
                'best_trade': round(random.uniform(15, 50), 2),
                'worst_trade': round(random.uniform(-20, -8), 2)
            },
            'risk': {
                'max_drawdown': round(max_drawdown, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'risk_score': random.randint(3, 7),
                'var_95': round(random.uniform(-5, -2), 2),
                'exposure': round(random.uniform(60, 85), 1)
            },
            'ai_metrics': {
                'signal_accuracy': round(random.uniform(75, 92), 1),
                'model_confidence': round(random.uniform(80, 95), 1),
                'prediction_horizon': '4h',
                'last_model_update': (datetime.now() - timedelta(hours=6)).isoformat(),
                'features_used': random.randint(25, 45)
            }
        }
        
        return stats
    
    def generate_candlestick_data(self, pair='BTC/USDT', timeframe='1h', periods=100):
        """Gera dados de candlestick"""
        
        base_price = self.base_prices[pair]
        candlesticks = []
        
        current_time = datetime.now()
        current_price = base_price
        
        for i in range(periods):
            # Timestamp
            if timeframe == '1m':
                timestamp = current_time - timedelta(minutes=i)
            elif timeframe == '5m':
                timestamp = current_time - timedelta(minutes=i*5)
            elif timeframe == '1h':
                timestamp = current_time - timedelta(hours=i)
            elif timeframe == '4h':
                timestamp = current_time - timedelta(hours=i*4)
            elif timeframe == '1d':
                timestamp = current_time - timedelta(days=i)
            
            # OHLCV data
            open_price = current_price
            
            # Variação do período
            change = random.uniform(-0.03, 0.03)  # -3% a +3%
            close_price = open_price * (1 + change)
            
            # High e Low
            high_price = max(open_price, close_price) * random.uniform(1.001, 1.02)
            low_price = min(open_price, close_price) * random.uniform(0.98, 0.999)
            
            # Volume
            volume = random.uniform(100, 10000)
            
            candlestick = {
                'timestamp': timestamp.isoformat(),
                'open': round(open_price, 6),
                'high': round(high_price, 6),
                'low': round(low_price, 6),
                'close': round(close_price, 6),
                'volume': round(volume, 2)
            }
            
            candlesticks.append(candlestick)
            current_price = close_price
        
        # Reverter para ordem cronológica
        candlesticks.reverse()
        
        return {
            'pair': pair,
            'timeframe': timeframe,
            'data': candlesticks
        }
    
    def _generate_ai_reasoning(self, signal_type, pair):
        """Gera reasoning de IA para sinais"""
        
        reasons = {
            'BUY': [
                f"Strong bullish momentum detected in {pair}",
                f"RSI oversold condition with volume spike in {pair}",
                f"Breaking resistance level with high confidence in {pair}",
                f"Positive correlation with market leaders suggests uptrend in {pair}",
                f"Machine learning model shows 85%+ probability of price increase in {pair}"
            ],
            'SELL': [
                f"Bearish divergence detected in {pair}",
                f"RSI overbought with decreasing volume in {pair}",
                f"Technical resistance level reached in {pair}",
                f"Market sentiment turning negative for {pair}",
                f"Risk management suggests position closure in {pair}"
            ],
            'HOLD': [
                f"Consolidation phase detected in {pair}",
                f"Mixed signals, recommend holding position in {pair}",
                f"Waiting for clearer market direction in {pair}",
                f"Current risk/reward ratio not favorable for {pair}",
                f"Market volatility too high for confident prediction in {pair}"
            ]
        }
        
        return random.choice(reasons[signal_type])
    
    def save_all_data(self):
        """Salva todos os dados mock em arquivos JSON"""
        
        print("🤖 Gerando dados mock para CryptoBot Dashboard...")
        
        # Criar diretório de dados
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Gerar e salvar todos os tipos de dados
        data_files = {
            'mock_prices.json': self.generate_price_data(),
            'mock_signals.json': self.generate_signals(15),
            'mock_trades.json': self.generate_trades(30),
            'mock_stats.json': self.generate_portfolio_stats(),
            'mock_btc_candlesticks.json': self.generate_candlestick_data('BTC/USDT', '1h', 168),
            'mock_eth_candlesticks.json': self.generate_candlestick_data('ETH/USDT', '4h', 72)
        }
        
        for filename, data in data_files.items():
            filepath = data_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Criado: {filepath}")
        
        print(f"\n🎉 {len(data_files)} arquivos de dados mock gerados!")
        print(f"📁 Localização: {data_dir.absolute()}")
        
        return True

def main():
    """Função principal"""
    try:
        generator = MockDataGenerator()
        generator.save_all_data()
        
        print("\n📋 Como usar os dados mock:")
        print("1. Use os arquivos JSON para desenvolvimento")
        print("2. Configure APIs mock no backend")
        print("3. Teste o dashboard com dados realistas")
        print("4. Substitua por APIs reais em produção")
        
    except Exception as e:
        print(f"❌ Erro ao gerar dados mock: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
