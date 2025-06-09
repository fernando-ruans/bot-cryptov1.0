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
        this.currentTimeframe = '5m';
        this.tradingViewWidget = null;
        this.isConnected = false;
        this.lastPrices = {};
        this.priceUpdateInterval = null;
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
        
        // Sincronizar timeframe com o valor selecionado no HTML
        const timeframeSelector = document.getElementById('timeframeSelector');
        if (timeframeSelector && timeframeSelector.value) {
            this.currentTimeframe = timeframeSelector.value;
            console.log(`📊 Timeframe sincronizado: ${this.currentTimeframe}`);
        }
        
        // Sincronizar ativo com o valor selecionado no HTML
        const assetSelector = document.getElementById('assetSelector');
        if (assetSelector && assetSelector.value) {
            this.currentSymbol = assetSelector.value;
            console.log(`💰 Ativo sincronizado: ${this.currentSymbol}`);
        }
        
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
        
        // Remover event listeners existentes para evitar duplicação
        const generateBtn = document.getElementById('generateSignalBtn');
        const confirmBtn = document.getElementById('confirmSignalBtn');
        const rejectBtn = document.getElementById('rejectSignalBtn');
        
        // Clonar elementos para remover todos os event listeners
        const newGenerateBtn = generateBtn.cloneNode(true);
        const newConfirmBtn = confirmBtn.cloneNode(true);
        const newRejectBtn = rejectBtn.cloneNode(true);
        
        generateBtn.parentNode.replaceChild(newGenerateBtn, generateBtn);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        rejectBtn.parentNode.replaceChild(newRejectBtn, rejectBtn);
        
        // Gerar sinal
        newGenerateBtn.addEventListener('click', () => {
            this.generateSignal();
        });

        // Confirmar sinal
        newConfirmBtn.addEventListener('click', () => {
            this.confirmSignal();
        });

        // Rejeitar sinal
        newRejectBtn.addEventListener('click', () => {
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

        // Seletor de timeframe
        document.getElementById('timeframeSelector').addEventListener('change', (e) => {
            console.log(`🔄 Timeframe selecionado: ${e.target.value}`);
            this.changeTimeframe(e.target.value);
        });
        
        // Iniciar atualização automática de preços
        this.startPriceUpdates();
        
        // Otimizar atualização baseada na visibilidade da página
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Página não visível - reduzir frequência
                this.stopPriceUpdates();
                this.priceUpdateInterval = setInterval(() => {
                    this.updateCurrentPrice();
                }, 5000); // 5 segundos quando não visível
            } else {
                // Página visível - máxima frequência
                this.startPriceUpdates();
            }
        });
    }
    
    startPriceUpdates() {
        // Limpar intervalo anterior se existir
        if (this.priceUpdateInterval) {
            clearInterval(this.priceUpdateInterval);
        }
        
        // Atualizar preço imediatamente
        this.updateCurrentPrice();
        
        // Configurar atualização automática a cada 1 segundo para sincronizar com o gráfico
        this.priceUpdateInterval = setInterval(() => {
            this.updateCurrentPrice();
        }, 1000);
        
        console.log('🔄 Atualização automática de preços iniciada (1s)');
    }
    
    stopPriceUpdates() {
        if (this.priceUpdateInterval) {
            clearInterval(this.priceUpdateInterval);
            this.priceUpdateInterval = null;
            console.log('⏹️ Atualização automática de preços parada');
        }
        
        // Parar também o intervalo de captura do gráfico
        if (this.chartPriceInterval) {
            clearInterval(this.chartPriceInterval);
            this.chartPriceInterval = null;
            console.log('⏹️ Captura de preços do gráfico interrompida');
        }
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
                    symbol: this.currentSymbol,
                    timeframe: this.currentTimeframe
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
                this.showSpecificErrorAlert(data.error, data.error_type);
            }
        } catch (error) {
            console.error('❌ Erro de conexão ao gerar sinal:', error);
            this.showAlert('Erro de conexão ao gerar sinal. Verifique sua internet.', 'danger');
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
        stopLossElement.textContent = signal.stop_loss ? `$${parseFloat(signal.stop_loss).toFixed(2)}` : 'N/A';
        takeProfitElement.textContent = signal.take_profit ? `$${parseFloat(signal.take_profit).toFixed(2)}` : 'N/A';

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
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
                    <p class="text-muted mb-0">Nenhum trade ativo no momento</p>
                    <small class="text-muted">Gere um sinal para começar a negociar</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = activeTrades.map(trade => {
            const currentPrice = parseFloat(trade.current_price || trade.entry_price);
            const entryPrice = parseFloat(trade.entry_price);
            const pnlPercent = ((currentPrice - entryPrice) / entryPrice * 100).toFixed(2);
            const pnlValue = (currentPrice - entryPrice).toFixed(2);
            const isProfit = currentPrice >= entryPrice;
            
            return `
                <div class="card mb-3 shadow-sm border-0">
                    <div class="card-body p-3">
                        <!-- Header com símbolo e tipo -->
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <div class="d-flex align-items-center">
                                <h6 class="mb-0 fw-bold text-primary">${trade.symbol}</h6>
                                <span class="badge ${trade.trade_type === 'BUY' ? 'bg-success' : 'bg-danger'} ms-2">
                                    <i class="fas ${trade.trade_type === 'BUY' ? 'fa-arrow-up' : 'fa-arrow-down'}"></i> ${trade.trade_type}
                                </span>
                            </div>
                            <button class="btn btn-outline-danger btn-sm" onclick="dashboard.closeTrade('${trade.id}')" title="Fechar Trade">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        
                        <!-- Preços principais -->
                        <div class="row g-2 mb-3">
                            <div class="col-6">
                                <div class="bg-light rounded p-2 text-center">
                                    <small class="text-muted d-block mb-1">Preço de Entrada</small>
                                    <strong class="text-dark">$${entryPrice.toFixed(2)}</strong>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="bg-light rounded p-2 text-center">
                                    <small class="text-muted d-block mb-1">Preço Atual</small>
                                    <strong class="${isProfit ? 'text-success' : 'text-danger'}">$${currentPrice.toFixed(2)}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <!-- P&L -->
                        <div class="text-center mb-3">
                            <div class="${isProfit ? 'bg-success' : 'bg-danger'} bg-opacity-10 rounded p-2">
                                <small class="text-muted d-block mb-1">Resultado Atual</small>
                                <div class="${isProfit ? 'text-success' : 'text-danger'} fw-bold">
                                    ${isProfit ? '+' : ''}$${pnlValue} (${isProfit ? '+' : ''}${pnlPercent}%)
                                </div>
                            </div>
                        </div>
                        
                        <!-- Stop Loss e Take Profit -->
                        <div class="row g-2 mb-3">
                            <div class="col-6">
                                <div class="border border-danger border-opacity-25 rounded p-2 text-center">
                                    <small class="text-muted d-block mb-1">Stop Loss</small>
                                    <span class="text-danger fw-bold">
                                        ${trade.stop_loss ? '$' + parseFloat(trade.stop_loss).toFixed(2) : 'N/A'}
                                    </span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="border border-success border-opacity-25 rounded p-2 text-center">
                                    <small class="text-muted d-block mb-1">Take Profit</small>
                                    <span class="text-success fw-bold">
                                        ${trade.take_profit ? '$' + parseFloat(trade.take_profit).toFixed(2) : 'N/A'}
                                    </span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Confiança -->
                        <div class="text-center">
                            <small class="text-muted d-block mb-1">Confiança do Sinal</small>
                            <span class="badge bg-info fs-6">
                                ${trade.signal_confidence ? (trade.signal_confidence * 100).toFixed(1) + '%' : 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
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
            tbody.innerHTML = '<tr><td colspan="11" class="text-center text-muted py-4">Nenhum trade realizado ainda</td></tr>';
            return;
        }
        
        tbody.innerHTML = trades.slice(0, 20).map(trade => `
            <tr>
                <td><strong>${trade.symbol}</strong></td>
                <td><span class="badge ${trade.trade_type === 'BUY' ? 'bg-success' : 'bg-danger'}">${trade.trade_type}</span></td>
                <td>$${parseFloat(trade.entry_price).toFixed(2)}</td>
                <td><span class="text-danger">${trade.stop_loss ? ((Math.abs(trade.stop_loss - trade.entry_price) / trade.entry_price) * 100).toFixed(1) + '%' : 'N/A'}</span></td>
                <td><span class="text-success">${trade.take_profit ? ((Math.abs(trade.take_profit - trade.entry_price) / trade.entry_price) * 100).toFixed(1) + '%' : 'N/A'}</span></td>
                <td>${trade.exit_price ? '$' + parseFloat(trade.exit_price).toFixed(2) : '-'}</td>
                <td>
                    <span class="fw-bold ${trade.pnl >= 0 ? 'text-success' : 'text-danger'}">
                        ${trade.pnl >= 0 ? 'GANHO' : 'PERDA'} (${trade.pnl_percent ? trade.pnl_percent.toFixed(2) + '%' : '0%'})
                    </span>
                </td>
                <td>
                    <span class="badge bg-info">
                        ${trade.signal_confidence ? (trade.signal_confidence * 100).toFixed(1) + '%' : 'N/A'}
                    </span>
                </td>
                <td>
                    <span class="badge ${trade.exit_reason === 'profit' ? 'bg-success' : trade.exit_reason === 'loss' ? 'bg-danger' : 'bg-secondary'}">
                        ${trade.exit_reason ? (trade.exit_reason === 'profit' ? 'Take Profit' : trade.exit_reason === 'loss' ? 'Stop Loss' : trade.exit_reason === 'manual' ? 'Manual' : trade.exit_reason) : '-'}
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

    showSpecificErrorAlert(errorMessage, errorType) {
        let alertType = 'danger';
        let icon = '❌';
        let title = 'Erro';
        
        switch(errorType) {
            case 'cooldown':
                alertType = 'warning';
                icon = '⏰';
                title = 'Aguarde';
                break;
            case 'no_data':
            case 'insufficient_data':
            case 'invalid_data':
                alertType = 'info';
                icon = '📊';
                title = 'Dados Indisponíveis';
                break;
            case 'low_confluence':
                alertType = 'secondary';
                icon = '📈';
                title = 'Condições de Mercado';
                break;
            case 'price_error':
                alertType = 'warning';
                icon = '💰';
                title = 'Erro de Preço';
                break;
            case 'indicators_error':
            case 'technical_error':
            case 'system_error':
                alertType = 'danger';
                icon = '⚠️';
                title = 'Erro Técnico';
                break;
            default:
                alertType = 'danger';
                icon = '❌';
                title = 'Erro';
        }
        
        const message = `<strong>${icon} ${title}:</strong> ${errorMessage}`;
        this.showAlert(message, alertType);
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
        
        // Atualizar o preço no painel lateral (card gerador de sinais)
        const sidebarPriceElement = document.getElementById('sidebarCurrentPrice');
        if (sidebarPriceElement) {
            const lastPrice = this.lastPrices[this.currentSymbol] || price;
            const priceChanged = lastPrice !== price;
            
            sidebarPriceElement.textContent = `$${price.toFixed(2)}`;
            
            // Animação visual quando o preço muda
            if (priceChanged) {
                sidebarPriceElement.style.transition = 'all 0.3s ease';
                sidebarPriceElement.style.transform = 'scale(1.05)';
                sidebarPriceElement.style.color = price > lastPrice ? '#27ae60' : '#e74c3c';
                
                setTimeout(() => {
                    sidebarPriceElement.style.transform = 'scale(1)';
                    sidebarPriceElement.style.color = '';
                }, 300);
            }
            
            // Calcular variação de preço
            const priceChangePercent = ((price - lastPrice) / lastPrice * 100);
            const priceChangeElement = document.getElementById('priceChange');
            
            if (priceChangeElement && priceChanged) {
                const changeText = `${priceChangePercent >= 0 ? '+' : ''}${priceChangePercent.toFixed(2)}%`;
                priceChangeElement.textContent = changeText;
                priceChangeElement.className = `badge ms-2 ${priceChangePercent >= 0 ? 'bg-success' : 'bg-danger'}`;
                
                // Animação no badge de mudança
                priceChangeElement.style.animation = 'pulse 0.5s ease-in-out';
                setTimeout(() => {
                    priceChangeElement.style.animation = '';
                }, 500);
            }
            
            // Armazenar preço anterior
            this.lastPrices[this.currentSymbol] = price;
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
        
        // Reiniciar atualização de preços para o novo ativo
        this.startPriceUpdates();
        
        // Recarregar dados do portfolio para o novo ativo
        this.loadPortfolio();
        this.loadActiveTradesStatus();
        
        this.showAlert(`Ativo alterado para ${newSymbol}`, 'info');
    }

    changeTimeframe(newTimeframe) {
        console.log(`⏰ Mudando timeframe para: ${newTimeframe}`);
        
        this.currentTimeframe = newTimeframe;
        
        // Atualizar gráfico TradingView com novo timeframe
        this.updateTradingViewChart(this.currentSymbol);
        
        this.showAlert(`Timeframe alterado para ${newTimeframe}`, 'info');
    }

    convertTimeframeForTradingView(timeframe) {
        // Converter timeframes para formato TradingView
        const timeframeMapping = {
            '1m': '1',
            '5m': '5',
            '15m': '15',
            '30m': '30',
            '1h': '60',
            '4h': '240',
            '1d': 'D',
            '1w': 'W'
        };
        return timeframeMapping[timeframe] || '5';
    }

    updateTradingViewChart(symbol) {
        const symbolMapping = this.getSymbolMapping();
        const tradingViewSymbol = symbolMapping[symbol] || `BINANCE:${symbol}`;
        const tradingViewTimeframe = this.convertTimeframeForTradingView(this.currentTimeframe);
        
        console.log(`📈 Atualizando gráfico: ${symbol} -> ${tradingViewSymbol}, timeframe: ${this.currentTimeframe} -> ${tradingViewTimeframe}`);
        
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
            "interval": tradingViewTimeframe,
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
            ],
            "onChartReady": () => {
                console.log('📈 TradingView carregado - configurando captura de preços');
                this.setupTradingViewPriceCapture();
            }
        });
        
        console.log(`📈 Gráfico atualizado para: ${tradingViewSymbol}`);
    }

    setupTradingViewPriceCapture() {
        try {
            // Aguardar o widget estar completamente carregado
            setTimeout(() => {
                // Configurar listener para mensagens do TradingView
                this.setupTradingViewMessageListener();
                
                // Configurar intervalo para tentar capturar preço do DOM
                this.setupDOMPriceCapture();
                
                console.log('✅ Captura de preços do TradingView configurada');
            }, 3000);
        } catch (error) {
            console.error('❌ Erro ao configurar captura de preços:', error);
            // Fallback para o método anterior
            this.updateCurrentPrice();
        }
    }
    
    setupTradingViewMessageListener() {
        // Escutar mensagens do iframe do TradingView
        window.addEventListener('message', (event) => {
            try {
                if (event.origin.includes('tradingview.com') && event.data) {
                    const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                    
                    // Procurar por dados de preço nas mensagens
                    if (data.name === 'quote-update' || data.name === 'quote_update') {
                        if (data.data && data.data.lp) {
                            const price = parseFloat(data.data.lp);
                            if (!isNaN(price)) {
                                this.updatePriceDisplay(price);
                            }
                        }
                    }
                }
            } catch (e) {
                // Ignorar erros de parsing silenciosamente
            }
        });
    }
    
    setupDOMPriceCapture() {
        // Configurar intervalo para capturar preço do DOM do TradingView
        this.chartPriceInterval = setInterval(() => {
            this.capturePriceFromDOM();
        }, 1000); // Verificar a cada 1 segundo
    }
    
    capturePriceFromDOM() {
        try {
            // Tentar encontrar elementos de preço no iframe do TradingView
            const chartContainer = document.getElementById('tradingview_chart');
            if (chartContainer) {
                const iframe = chartContainer.querySelector('iframe');
                if (iframe && iframe.contentDocument) {
                    // Procurar por elementos que contenham o preço
                    const priceSelectors = [
                        '[data-name="legend-source-item"]',
                        '.js-symbol-last',
                        '[class*="price"]',
                        '[class*="last"]'
                    ];
                    
                    for (const selector of priceSelectors) {
                        const elements = iframe.contentDocument.querySelectorAll(selector);
                        for (const element of elements) {
                            const text = element.textContent || element.innerText;
                            const priceMatch = text.match(/([0-9,]+\.?[0-9]*)/g);
                            if (priceMatch) {
                                const price = parseFloat(priceMatch[0].replace(/,/g, ''));
                                if (!isNaN(price) && price > 1000) { // Filtro básico para BTC
                                    this.updatePriceDisplay(price);
                                    return;
                                }
                            }
                        }
                    }
                }
            }
        } catch (error) {
            // Fallback silencioso - iframe pode estar bloqueado por CORS
            // Usar API externa como backup
            if (Math.random() < 0.1) { // 10% das vezes para não sobrecarregar
                this.updateCurrentPrice();
            }
        }
    }



    updatePriceDisplay(price) {
        if (price && !isNaN(price)) {
            // Atualizar elementos de preço diretamente
            const priceElements = {
                navPriceElement: document.getElementById('navPriceElement'),
                sidebarCurrentPrice: document.getElementById('sidebarCurrentPrice'),
                currentPriceElements: document.querySelectorAll('.current-price')
            };
            
            const formattedPrice = `$${price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
            
            // Atualizar preço na navegação
            if (priceElements.navPriceElement) {
                const oldPrice = parseFloat(priceElements.navPriceElement.textContent.replace(/[$,]/g, ''));
                priceElements.navPriceElement.textContent = formattedPrice;
                
                // Animação visual
                if (!isNaN(oldPrice) && oldPrice !== price) {
                    priceElements.navPriceElement.style.transform = 'scale(1.05)';
                    priceElements.navPriceElement.style.color = price > oldPrice ? '#28a745' : '#dc3545';
                    setTimeout(() => {
                        priceElements.navPriceElement.style.transform = 'scale(1)';
                        priceElements.navPriceElement.style.color = '';
                    }, 300);
                }
            }
            
            // Atualizar preço no sidebar
            if (priceElements.sidebarCurrentPrice) {
                const oldPrice = parseFloat(priceElements.sidebarCurrentPrice.textContent.replace(/[$,]/g, ''));
                priceElements.sidebarCurrentPrice.textContent = formattedPrice;
                
                // Animação visual
                if (!isNaN(oldPrice) && oldPrice !== price) {
                    priceElements.sidebarCurrentPrice.style.transform = 'scale(1.05)';
                    priceElements.sidebarCurrentPrice.style.color = price > oldPrice ? '#28a745' : '#dc3545';
                    setTimeout(() => {
                        priceElements.sidebarCurrentPrice.style.transform = 'scale(1)';
                        priceElements.sidebarCurrentPrice.style.color = '';
                    }, 300);
                }
            }
            
            // Atualizar outros elementos com classe current-price
            priceElements.currentPriceElements.forEach(element => {
                element.textContent = formattedPrice;
            });
            
            console.log(`💰 Preço atualizado do gráfico: ${formattedPrice}`);
        }
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