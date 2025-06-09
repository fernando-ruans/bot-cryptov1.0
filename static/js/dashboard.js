/**
 * Trading Bot AI - Dashboard Simplificado
 * Sistema Paper Trading com Fluxo Simples:
 * 1. Gerar Sinal → 2. Aprovar/Rejeitar → 3. Contabilizar P&L → 4. Calcular Win Rate
 */

class SimpleTradingDashboard {
    constructor() {
        this.socket = null;
        this.currentSignal = null;
        this.currentSymbol = 'BTCUSDT';
        this.tradingViewWidget = null;
        this.portfolio = {
            total_trades: 0,
            win_rate: 0,
            total_pnl: 0,
            active_trades: 0
        };
        
        this.init();
    }

    init() {
        console.log('🚀 Inicializando Trading Bot AI - Versão Simplificada');
        this.initTradingView();
        this.initEventListeners();
        this.initWebSocket();
        this.loadPortfolio();
        this.loadActiveTradesStatus();
        this.loadTradesHistory();
        
        // Carregar preço inicial
        this.updateCurrentPrice();
        
        // Auto-refresh a cada 30 segundos
        setInterval(() => {
            this.loadPortfolio();
            this.loadActiveTradesStatus();
            this.updateCurrentPrice();
        }, 30000);
        
        // Atualizar preço a cada 10 segundos
        setInterval(() => {
            this.updateCurrentPrice();
        }, 10000);
        
        console.log('✅ Dashboard inicializado com sucesso!');
    }

    initTradingView() {
        console.log('📈 Inicializando TradingView...');
        this.tradingViewWidget = new TradingView.widget({
            "width": "100%",
            "height": "500",
            "symbol": "BINANCE:BTCUSDT",
            "interval": "5",
            "timezone": "America/Sao_Paulo",
            "theme": "light",
            "style": "1",
            "locale": "pt_BR",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_top_toolbar": false,
            "hide_legend": true,
            "save_image": false,
            "container_id": "tradingview_chart",
            "studies": [
                "RSI@tv-basicstudies",
                "MASimple@tv-basicstudies",
                "MACD@tv-basicstudies"
            ]
        });
    }

    initEventListeners() {
        console.log('🎯 Configurando event listeners...');
        
        // Gerar sinal
        document.getElementById('generateSignalBtn').addEventListener('click', () => {
            this.generateSignal();
        });

        // Confirmar sinal
        document.getElementById('confirmSignalBtn').addEventListener('click', () => {
            this.confirmSignal();
        });

        // Rejeitar sinal
        document.getElementById('rejectSignalBtn').addEventListener('click', () => {
            this.rejectSignal();
        });

        // Atualizar histórico
        document.getElementById('refreshHistoryBtn').addEventListener('click', () => {
            this.loadTradesHistory();
        });

        // Seletor de ativos
        document.getElementById('assetSelector').addEventListener('change', (e) => {
            this.changeAsset(e.target.value);
        });
    }

    initWebSocket() {
        console.log('🔗 Conectando WebSocket...');
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('✅ WebSocket conectado');
            this.updateBotStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('❌ WebSocket desconectado');
            this.updateBotStatus(false);
        });

        this.socket.on('price_update', (data) => {
            this.handlePriceUpdate(data);
        });

        this.socket.on('trade_update', (data) => {
            this.handleTradeUpdate(data);
        });
    }

    updateBotStatus(isRunning) {
        const statusElement = document.getElementById('botStatus');
        const statusTextElement = document.getElementById('botStatusText');
        
        if (isRunning) {
            statusElement.className = 'status-indicator status-running';
            statusTextElement.textContent = 'Online';
        } else {
            statusElement.className = 'status-indicator status-stopped';
            statusTextElement.textContent = 'Offline';
        }
    }

    async generateSignal() {
        console.log('🎰 Gerando novo sinal...');
        const btn = document.getElementById('generateSignalBtn');
        const originalText = btn.innerHTML;
        
        try {
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Gerando...';
            btn.disabled = true;

            const response = await fetch('/api/generate_signal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: this.currentSymbol
                })
            });

            const data = await response.json();
            
            if (data.success && data.signal) {
                console.log('✅ Sinal gerado:', data.signal);
                this.currentSignal = data.signal;
                this.displayCurrentSignal(data.signal);
                this.showAlert(`Novo sinal detectado: ${data.signal.signal_type} ${data.signal.symbol}`, 'success');
            } else {
                console.error('❌ Erro ao gerar sinal:', data.error);
                this.showAlert('Erro ao gerar sinal: ' + (data.error || 'Erro desconhecido'), 'danger');
            }
        } catch (error) {
            console.error('❌ Erro de conexão ao gerar sinal:', error);
            this.showAlert('Erro de conexão ao gerar sinal', 'danger');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }

    displayCurrentSignal(signal) {
        console.log('📊 Exibindo sinal:', signal);
        const card = document.getElementById('currentSignalCard');
        const actionElement = document.getElementById('signalAction');
        const priceElement = document.getElementById('signalPrice');
        const symbolElement = document.getElementById('signalSymbol');
        const confidenceElement = document.getElementById('signalConfidence');
        const stopLossElement = document.getElementById('signalStopLoss');
        const takeProfitElement = document.getElementById('signalTakeProfit');

        // Definir cor da ação
        actionElement.className = `badge fs-6 ${signal.signal_type === 'buy' ? 'bg-success' : 'bg-danger'}`;
        actionElement.textContent = signal.signal_type?.toUpperCase() || 'N/A';
        
        priceElement.textContent = `$${parseFloat(signal.entry_price).toFixed(2)}`;
        symbolElement.textContent = signal.symbol;
        
        // Exibir confiança como porcentagem
        const confidence = (signal.confidence * 100).toFixed(1);
        confidenceElement.textContent = `${confidence}%`;
        
        // Exibir stop loss e take profit
        stopLossElement.textContent = `$${parseFloat(signal.stop_loss).toFixed(2)}`;
        takeProfitElement.textContent = `$${parseFloat(signal.take_profit).toFixed(2)}`;

        // Aplicar classe CSS baseada na ação
        card.className = `card signal-card signal-alert mb-4 ${signal.signal_type?.toLowerCase() || 'neutral'}`;
        card.style.display = 'block';
    }

    async confirmSignal() {
        if (!this.currentSignal) {
            this.showAlert('Nenhum sinal para confirmar', 'warning');
            return;
        }

        console.log('✅ Confirmando sinal:', this.currentSignal);

        try {
            const response = await fetch('/api/paper_trading/confirm_signal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    signal: this.currentSignal,
                    amount: 1000 // Valor padrão fictício
                })
            });

            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Trade confirmado com sucesso!');
                this.showAlert('✅ Trade confirmado com sucesso!', 'success');
                this.hideCurrentSignal();
                this.loadPortfolio();
                this.loadActiveTradesStatus();
                this.loadTradesHistory();
            } else {
                console.error('❌ Erro ao confirmar trade:', data.error);
                this.showAlert('Erro ao confirmar trade: ' + (data.error || 'Erro desconhecido'), 'danger');
            }
        } catch (error) {
            console.error('❌ Erro de conexão ao confirmar trade:', error);
            this.showAlert('Erro de conexão ao confirmar trade', 'danger');
        }
    }

    rejectSignal() {
        console.log('❌ Sinal rejeitado pelo usuário');
        this.showAlert('Sinal rejeitado', 'info');
        this.hideCurrentSignal();
    }

    hideCurrentSignal() {
        const card = document.getElementById('currentSignalCard');
        card.style.display = 'none';
        this.currentSignal = null;
    }

    async loadPortfolio() {
        try {
            const response = await fetch('/api/paper_trading/portfolio');
            const data = await response.json();
            
            if (data.success) {
                this.portfolio = data.portfolio;
                this.updateStatsDisplay();
                console.log('📊 Portfolio atualizado:', this.portfolio);
            }
        } catch (error) {
            console.error('❌ Erro ao carregar portfolio:', error);
        }
    }

    updateStatsDisplay() {
        document.getElementById('totalTrades').textContent = this.portfolio.total_trades;
        
        const winRateElement = document.getElementById('winRate');
        const winRate = this.portfolio.win_rate;
        winRateElement.textContent = `${winRate.toFixed(1)}%`;
        
        // Aplicar cores baseadas na taxa de acerto
        winRateElement.className = '';
        if (winRate >= 60) {
            winRateElement.classList.add('win-rate-good');
        } else if (winRate >= 40) {
            winRateElement.classList.add('win-rate-neutral');
        } else {
            winRateElement.classList.add('win-rate-bad');
        }
        
        const pnlElement = document.getElementById('totalPnL');
        const pnl = this.portfolio.total_pnl;
        pnlElement.textContent = `R$ ${pnl.toFixed(2)}`;
        pnlElement.className = pnl >= 0 ? 'text-success fw-bold' : 'text-danger fw-bold';
        
        document.getElementById('activeTrades').textContent = this.portfolio.active_trades;
    }

    async loadActiveTradesStatus() {
        try {
            const response = await fetch('/api/paper_trading/portfolio');
            const data = await response.json();
            
            if (data.success && data.active_trades) {
                this.displayActiveTrades(data.active_trades);
            }
        } catch (error) {
            console.error('❌ Erro ao carregar trades ativos:', error);
        }
    }

    displayActiveTrades(activeTrades) {
        const container = document.getElementById('activeTradesList');
        
        if (activeTrades.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">Nenhum trade ativo</p>';
            return;
        }
        
        container.innerHTML = activeTrades.map(trade => `
            <div class="border rounded p-3 mb-2 bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${trade.symbol}</strong><br>
                        <small class="text-muted">${trade.action} @ $${parseFloat(trade.entry_price).toFixed(2)}</small>
                    </div>
                    <div class="text-end">
                        <span class="badge ${trade.current_pnl >= 0 ? 'badge-profit' : 'badge-loss'} mb-1">
                            ${trade.current_pnl >= 0 ? '+' : ''}$${trade.current_pnl.toFixed(2)}
                        </span><br>
                        <button class="btn btn-warning-custom btn-sm" onclick="dashboard.closeTrade('${trade.id}')" title="Fechar Trade">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async closeTrade(tradeId) {
        console.log('🔒 Fechando trade:', tradeId);
        
        try {
            const response = await fetch('/api/paper_trading/close_trade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    trade_id: tradeId
                })
            });

            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Trade fechado com sucesso!');
                this.showAlert('Trade fechado com sucesso!', 'success');
                this.loadPortfolio();
                this.loadActiveTradesStatus();
                this.loadTradesHistory();
            } else {
                console.error('❌ Erro ao fechar trade:', data.error);
                this.showAlert('Erro ao fechar trade: ' + (data.error || 'Erro desconhecido'), 'danger');
            }
        } catch (error) {
            console.error('❌ Erro de conexão ao fechar trade:', error);
            this.showAlert('Erro de conexão ao fechar trade', 'danger');
        }
    }

    async loadTradesHistory() {
        console.log('📜 Carregando histórico de trades...');
        
        try {
            const response = await fetch('/api/paper_trading/history');
            const data = await response.json();
            
            if (data.success) {
                this.displayTradesHistory(data.trades);
                console.log(`📊 Histórico carregado: ${data.trades.length} trades`);
            }
        } catch (error) {
            console.error('❌ Erro ao carregar histórico:', error);
        }
    }

    displayTradesHistory(trades) {
        const tbody = document.querySelector('#tradesHistoryTable tbody');
        
        if (trades.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Nenhum trade realizado ainda</td></tr>';
            return;
        }
        
        tbody.innerHTML = trades.slice(0, 20).map(trade => `
            <tr>
                <td><strong>${trade.symbol}</strong></td>
                <td><span class="badge ${trade.action === 'BUY' ? 'bg-success' : 'bg-danger'}">${trade.action}</span></td>
                <td>$${parseFloat(trade.entry_price).toFixed(2)}</td>
                <td>${trade.exit_price ? '$' + parseFloat(trade.exit_price).toFixed(2) : '-'}</td>
                <td>
                    <span class="fw-bold ${trade.pnl >= 0 ? 'text-success' : 'text-danger'}">
                        ${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}
                    </span>
                </td>
                <td><small>${new Date(trade.timestamp).toLocaleString('pt-BR')}</small></td>
                <td>
                    <span class="badge ${trade.status === 'open' ? 'bg-warning' : trade.pnl >= 0 ? 'bg-success' : 'bg-danger'}">
                        ${trade.status === 'open' ? 'Aberto' : (trade.pnl >= 0 ? 'Lucro' : 'Perda')}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    handlePriceUpdate(data) {
        // Atualizar preços em tempo real se necessário
        console.log('💰 Atualização de preço:', data);
        // Pode implementar atualizações visuais aqui se necessário
    }

    handleTradeUpdate(data) {
        // Atualizar trades em tempo real
        console.log('📈 Atualização de trade:', data);
        this.loadPortfolio();
        this.loadActiveTradesStatus();
    }

    showAlert(message, type = 'info') {
        // Criar elemento de alerta com melhor styling
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed shadow-lg`;
        alert.style.cssText = 'top: 100px; right: 20px; z-index: 1050; min-width: 350px; border-radius: 10px;';
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas ${this.getAlertIcon(type)} me-2"></i>
                <div>${message}</div>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(alert);
        
        // Remover automaticamente após 5 segundos
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    getAlertIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'danger': 'fa-exclamation-triangle',
            'warning': 'fa-exclamation-circle',
            'info': 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    async updateCurrentPrice() {
        try {
            const response = await fetch(`/api/price/${this.currentSymbol}`);
            const data = await response.json();
            
            if (data.success) {
                this.displayCurrentPrice(data.price);
            } else {
                console.warn(`⚠️ Não foi possível obter preço para ${this.currentSymbol}`);
            }
        } catch (error) {
            console.error('❌ Erro ao atualizar preço:', error);
        }
    }

    displayCurrentPrice(price) {
        // Atualizar o indicador de preço na navbar
        const navPriceElement = document.getElementById('currentPrice');
        if (navPriceElement) {
            navPriceElement.textContent = `$${price.toFixed(6)}`;
        }
        
        // Atualizar o preço no painel lateral
        const sidebarPriceElement = document.getElementById('sidebarCurrentPrice');
        if (sidebarPriceElement) {
            sidebarPriceElement.textContent = `$${price.toFixed(2)}`;
        }
        
        // Atualizar qualquer outro elemento de preço na interface
        const symbolPriceElements = document.querySelectorAll('.current-price');
        symbolPriceElements.forEach(element => {
            element.textContent = `$${price.toFixed(6)}`;
        });
        
        console.log(`💰 Preço atualizado: ${this.currentSymbol} = $${price.toFixed(2)}`);
    }

    // Mapeamento de símbolos para TradingView
    getSymbolMapping() {
        return {
            // Crypto Major
            'BTCUSDT': 'BINANCE:BTCUSDT',
            'ETHUSDT': 'BINANCE:ETHUSDT',
            'ADAUSDT': 'BINANCE:ADAUSDT',
            'BNBUSDT': 'BINANCE:BNBUSDT',
            'SOLUSDT': 'BINANCE:SOLUSDT',
            'XRPUSDT': 'BINANCE:XRPUSDT',
            'DOTUSDT': 'BINANCE:DOTUSDT',
            'LINKUSDT': 'BINANCE:LINKUSDT',
            
            // Crypto Alt
            'MATICUSDT': 'BINANCE:MATICUSDT',
            'AVAXUSDT': 'BINANCE:AVAXUSDT',
            'LTCUSDT': 'BINANCE:LTCUSDT',
            'UNIUSDT': 'BINANCE:UNIUSDT',
            'ATOMUSDT': 'BINANCE:ATOMUSDT',
            'ALGOUSDT': 'BINANCE:ALGOUSDT',
            
            // Forex
            'EURUSD': 'FX:EURUSD',
            'GBPUSD': 'FX:GBPUSD',
            'USDJPY': 'FX:USDJPY',
            'AUDUSD': 'FX:AUDUSD',
            'USDCAD': 'FX:USDCAD',
            
            // Índices
            'SPX': 'SP:SPX',
            'NDX': 'NASDAQ:NDX',
            'DJI': 'DJ:DJI'
        };
    }

    changeAsset(newSymbol) {
        console.log(`🔄 Mudando ativo para: ${newSymbol}`);
        
        this.currentSymbol = newSymbol;
        
        // Atualizar interface
        document.getElementById('currentSymbol').textContent = newSymbol;
        document.getElementById('navCurrentAsset').textContent = newSymbol;
        document.getElementById('selectedAssetBadge').textContent = newSymbol;
        
        // Atualizar gráfico TradingView
        this.updateTradingViewChart(newSymbol);
        
        // Limpar sinal atual se existir
        this.clearCurrentSignal();
        
        // Atualizar preço atual imediatamente
        this.updateCurrentPrice();
        
        // Recarregar dados do portfolio para o novo ativo
        this.loadPortfolio();
        this.loadActiveTradesStatus();
        
        this.showAlert(`Ativo alterado para ${newSymbol}`, 'info');
    }

    updateTradingViewChart(symbol) {
        const symbolMapping = this.getSymbolMapping();
        const tradingViewSymbol = symbolMapping[symbol] || `BINANCE:${symbol}`;
        
        // Remover widget existente
        if (this.tradingViewWidget) {
            const container = document.getElementById('tradingview_chart');
            container.innerHTML = '';
        }
        
        // Criar novo widget
        this.tradingViewWidget = new TradingView.widget({
            "width": "100%",
            "height": "500",
            "symbol": tradingViewSymbol,
            "interval": "5",
            "timezone": "America/Sao_Paulo",
            "theme": "light",
            "style": "1",
            "locale": "pt_BR",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "allow_symbol_change": false,
            "container_id": "tradingview_chart",
            "studies": [
                "RSI@tv-basicstudies",
                "MACD@tv-basicstudies"
            ]
        });
        
        console.log(`📈 Gráfico atualizado para: ${tradingViewSymbol}`);
    }

    clearCurrentSignal() {
        this.currentSignal = null;
        document.getElementById('signalContent').style.display = 'none';
        document.getElementById('signalActions').style.display = 'none';
        document.getElementById('generateSignalBtn').style.display = 'block';
    }
}

// Função global para fechar trades (chamada pelo onclick nos botões)
window.closeTrade = function(tradeId) {
    if (window.dashboard) {
        window.dashboard.closeTrade(tradeId);
    }
};

// Inicializar dashboard quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 DOM carregado, inicializando dashboard...');
    window.dashboard = new SimpleTradingDashboard();
});

// Exportar para uso global
window.SimpleTradingDashboard = SimpleTradingDashboard;