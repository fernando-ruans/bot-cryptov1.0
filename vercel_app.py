#!/usr/bin/env python3
"""
CryptoNinja Trading Bot - Vercel Compatible App
Otimizado para deploy serverless em Vercel
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Configurar logging minimalista para produção
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cryptoninja-vercel-prod-2025')

# Configuração de banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///trading_bot.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

# Importar módulos essenciais de forma lazy
def get_ai_engine():
    """Lazy loading da AI Engine para reduzir cold start"""
    try:
        from src.ai_engine import AITradingEngine
        return AITradingEngine()
    except Exception as e:
        logger.error(f"Erro ao carregar AI Engine: {e}")
        return None

def get_market_data():
    """Lazy loading do Market Data Manager"""
    try:
        from src.market_data import MarketDataManager
        return MarketDataManager()
    except Exception as e:
        logger.error(f"Erro ao carregar Market Data: {e}")
        return None

# Cache de instâncias
ai_engine = None
market_data = None

@app.route('/')
def index():
    """Página principal"""
    return render_template('dashboard.html')

@app.route('/api/symbols')
def get_symbols():
    """Obter lista de símbolos disponíveis"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT']
    return jsonify(symbols)

@app.route('/api/price/<symbol>')
def get_price(symbol):
    """Obter preço atual de um símbolo"""
    global market_data
    
    try:
        if not market_data:
            market_data = get_market_data()
        
        if market_data:
            price_data = market_data.get_current_price(symbol)
            if price_data:
                return jsonify({
                    'symbol': symbol,
                    'price': price_data.get('price', 0),
                    'change_24h': price_data.get('change_24h', 0),
                    'volume_24h': price_data.get('volume_24h', 0),
                    'timestamp': datetime.now().isoformat()
                })
    except Exception as e:
        logger.error(f"Erro ao obter preço {symbol}: {e}")
    
    # Fallback com dados simulados
    return jsonify({
        'symbol': symbol,
        'price': 50000 if symbol == 'BTCUSDT' else 3000,
        'change_24h': 2.5,
        'volume_24h': 1000000,
        'timestamp': datetime.now().isoformat(),
        'simulated': True
    })

@app.route('/api/signal/<symbol>')
def generate_signal(symbol):
    """Gerar sinal de trading para um símbolo"""
    global ai_engine, market_data
    
    try:
        if not ai_engine:
            ai_engine = get_ai_engine()
        if not market_data:
            market_data = get_market_data()
        
        if ai_engine and market_data:
            # Obter dados do mercado
            market_data_obj = market_data.get_market_data(symbol)
            
            if market_data_obj:
                # Gerar sinal
                signal = ai_engine.generate_signal(symbol, market_data_obj)
                
                return jsonify({
                    'symbol': symbol,
                    'signal': signal.get('signal', 'HOLD'),
                    'confidence': signal.get('confidence', 0.5),
                    'price': signal.get('price', 0),
                    'timestamp': datetime.now().isoformat(),
                    'features': signal.get('features', {}),
                    'technical_indicators': signal.get('technical_indicators', {})
                })
    except Exception as e:
        logger.error(f"Erro ao gerar sinal {symbol}: {e}")
    
    # Fallback com sinal simulado
    import random
    return jsonify({
        'symbol': symbol,
        'signal': random.choice(['BUY', 'SELL', 'HOLD']),
        'confidence': round(random.uniform(0.3, 0.9), 2),
        'price': 50000 if symbol == 'BTCUSDT' else 3000,
        'timestamp': datetime.now().isoformat(),
        'simulated': True
    })

@app.route('/api/trades')
def get_trades():
    """Obter trades ativos simulados"""
    trades = [
        {
            'id': 1,
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'entry_price': 48500.0,
            'current_price': 49200.0,
            'quantity': 0.1,
            'pnl': 70.0,
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': 2,
            'symbol': 'ETHUSDT',
            'side': 'SELL',
            'entry_price': 3100.0,
            'current_price': 3050.0,
            'quantity': 1.0,
            'pnl': 50.0,
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    return jsonify(trades)

@app.route('/api/stats')
def get_stats():
    """Obter estatísticas de trading"""
    stats = {
        'total_trades': 125,
        'winning_trades': 78,
        'losing_trades': 47,
        'win_rate': 62.4,
        'total_pnl': 2850.75,
        'daily_pnl': 125.50,
        'best_trade': 450.00,
        'worst_trade': -85.25,
        'active_trades': 2,
        'balance': 12850.75
    }
    
    return jsonify(stats)

@app.route('/api/health')
def health_check():
    """Health check para monitoramento"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Configuração para Vercel
def handler(request):
    """Handler principal para Vercel"""
    return app(request.environ, lambda status, headers: None)

# Para desenvolvimento local
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )

# Export para Vercel
app = app
