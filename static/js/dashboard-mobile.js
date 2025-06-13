// 📱 CryptoNinja Mobile - Dashboard JavaScript
// Otimizado para dispositivos móveis com performance e UX aprimorados

class MobileDashboard {
    constructor() {
        this.socket = null;
        this.isOnline = false;
        this.lastUpdate = null;
        this.refreshInterval = null;
        this.touchStartY = 0;
        this.pullToRefreshThreshold = 60;
        this.isRefreshing = false;
        this.toastCount = 0;
        this.maxToasts = 3;
        
        this.init();
    }

    init() {
        console.log('🚀 Inicializando CryptoNinja Mobile Dashboard');
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Conectar WebSocket
        this.connectWebSocket();
        
        // Carregar dados iniciais
        this.loadInitialData();
        
        // Configurar refresh automático
        this.setupAutoRefresh();
        
        // Configurar PWA
        this.setupPWA();
        
        // Configurar pull-to-refresh
        this.setupPullToRefresh();
    }

    setupEventListeners() {
        // Botão de refresh
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Botão de gerar sinais
        const generateSignalsBtn = document.getElementById('generate-signals-btn');
        if (generateSignalsBtn) {
            generateSignalsBtn.addEventListener('click', () => this.generateSignals());
        }

        // Monitorar visibilidade da página
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });

        // Detectar orientação
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.handleOrientationChange(), 100);
        });

        // Eventos de touch para melhor responsividade
        document.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
    }

    connectWebSocket() {
        try {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('✅ WebSocket conectado');
                this.updateConnectionStatus(true);
                this.isOnline = true;
            });

            this.socket.on('disconnect', () => {
                console.log('❌ WebSocket desconectado');
                this.updateConnectionStatus(false);
                this.isOnline = false;
            });

            this.socket.on('price_update', (data) => {
                this.updatePrices(data);
            });

            this.socket.on('signal_update', (data) => {
                this.updateSignals(data);
            });

            this.socket.on('stats_update', (data) => {
                this.updateStats(data);
            });

            this.socket.on('trade_update', (data) => {
                this.updateTrades(data);
            });

        } catch (error) {
            console.error('❌ Erro ao conectar WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    async loadInitialData() {
        this.showLoading(true);
        
        try {
            // Carregar dados em paralelo para melhor performance
            const [statsResponse, pricesResponse, signalsResponse, tradesResponse] = await Promise.all([
                fetch('/api/stats'),
                fetch('/api/prices'),
                fetch('/api/signals'),
                fetch('/api/trades')
            ]);

            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                this.updateStats(stats);
            }

            if (pricesResponse.ok) {
                const prices = await pricesResponse.json();
                this.updatePrices(prices);
            }

            if (signalsResponse.ok) {
                const signals = await signalsResponse.json();
                this.updateSignals(signals);
            }

            if (tradesResponse.ok) {
                const trades = await tradesResponse.json();
                this.updateTrades(trades);
            }

            this.lastUpdate = new Date();
            this.updateLastUpdateTime();

        } catch (error) {
            console.error('❌ Erro ao carregar dados:', error);
            this.showToast('Erro ao carregar dados', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    updateStats(stats) {
        const elements = {
            'stat-balance': this.formatCurrency(stats.balance || 0),
            'stat-daily-pnl': this.formatCurrency(stats.daily_pnl || 0),
            'stat-win-rate': `${(stats.win_rate || 0).toFixed(1)}%`,
            'stat-total-trades': stats.total_trades || 0,
            'stat-active-trades': stats.active_trades || 0
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                
                // Adicionar classes de cor para P&L
                if (id === 'stat-daily-pnl') {
                    element.className = stats.daily_pnl >= 0 ? 'stat-positive' : 'stat-negative';
                }
            }
        });
    }

    updatePrices(prices) {
        const priceGrid = document.getElementById('price-grid');
        if (!priceGrid || !prices) return;

        const priceCards = prices.map(price => {
            const changeClass = price.change >= 0 ? 'text-success' : 'text-danger';
            const changeIcon = price.change >= 0 ? '↗' : '↘';
            
            return `
                <div class="price-card animate-slide-up">
                    <div class="price-symbol">${price.symbol}</div>
                    <div class="price-value">$${this.formatNumber(price.price)}</div>
                    <div class="price-change ${changeClass}">
                        ${changeIcon} ${price.change.toFixed(2)}%
                    </div>
                </div>
            `;
        }).join('');

        priceGrid.innerHTML = priceCards;
        this.updateLastUpdateTime();
    }

    updateSignals(signals) {
        const container = document.getElementById('signals-container');
        if (!container || !signals || !Array.isArray(signals)) return;

        if (signals.length === 0) {
            container.innerHTML = `
                <div class="signal-card text-center">
                    <i class="fas fa-search fa-2x mb-2 text-muted"></i>
                    <h6>Nenhum sinal disponível</h6>
                    <p class="mb-0 text-muted">Clique em "Gerar" para análise IA</p>
                </div>
            `;
            return;
        }

        const signalCards = signals.slice(0, 3).map(signal => {
            const signalClass = signal.action.toLowerCase();
            const signalIcon = this.getSignalIcon(signal.action);
            
            return `
                <div class="signal-card ${signalClass} animate-slide-right">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="mb-0">${signal.symbol}</h6>
                        <span class="badge bg-${this.getSignalColor(signal.action)}">
                            ${signalIcon} ${signal.action}
                        </span>
                    </div>
                    <p class="mb-1"><strong>Preço:</strong> $${this.formatNumber(signal.price)}</p>
                    <p class="mb-1"><strong>Confiança:</strong> ${signal.confidence}%</p>
                    <p class="mb-0 text-muted small">${signal.reason}</p>
                </div>
            `;
        }).join('');

        container.innerHTML = signalCards;
    }

    updateTrades(trades) {
        this.updateActiveTrades(trades.active || []);
        this.updateTradeHistory(trades.history || []);
    }

    updateActiveTrades(activeTrades) {
        const table = document.getElementById('active-trades-table');
        const count = document.getElementById('active-trades-count');
        
        if (count) count.textContent = activeTrades.length;
        
        if (!table) return;

        if (activeTrades.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-3">
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <br>Nenhum trade ativo
                    </td>
                </tr>
            `;
            return;
        }

        const rows = activeTrades.map(trade => {
            const pnlClass = trade.pnl >= 0 ? 'text-success' : 'text-danger';
            
            return `
                <tr>
                    <td><strong>${trade.symbol}</strong></td>
                    <td>
                        <span class="badge bg-${trade.side === 'BUY' ? 'success' : 'danger'}">
                            ${trade.side}
                        </span>
                    </td>
                    <td class="d-none d-sm-table-cell">$${this.formatNumber(trade.entry_price)}</td>
                    <td>$${this.formatNumber(trade.current_price)}</td>
                    <td class="${pnlClass}">$${this.formatNumber(trade.pnl)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger" onclick="mobileDashboard.closeTrade('${trade.id}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        table.innerHTML = rows;
    }

    updateTradeHistory(history) {
        const table = document.getElementById('trade-history-table');
        if (!table) return;

        if (history.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted py-3">
                        <i class="fas fa-history fa-2x mb-2"></i>
                        <br>Nenhum histórico disponível
                    </td>
                </tr>
            `;
            return;
        }

        const rows = history.slice(0, 10).map(trade => {
            const statusClass = trade.status === 'PROFIT' ? 'success' : 'danger';
            const pnlClass = trade.pnl >= 0 ? 'text-success' : 'text-danger';
            
            return `
                <tr>
                    <td><strong>${trade.symbol}</strong></td>
                    <td>
                        <span class="badge bg-${trade.side === 'BUY' ? 'success' : 'danger'}">
                            ${trade.side}
                        </span>
                    </td>
                    <td class="d-none d-sm-table-cell ${pnlClass}">$${this.formatNumber(trade.pnl)}</td>
                    <td>
                        <span class="badge bg-${statusClass}">
                            ${trade.status}
                        </span>
                    </td>
                </tr>
            `;
        }).join('');

        table.innerHTML = rows;
    }

    async generateSignals() {
        const btn = document.getElementById('generate-signals-btn');
        if (!btn) return;

        const originalContent = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        btn.disabled = true;

        try {
            const response = await fetch('/api/generate-signals', {
                method: 'POST'
            });

            if (response.ok) {
                const signals = await response.json();
                this.updateSignals(signals);
                this.showToast('Sinais gerados com sucesso!', 'success');
            } else {
                throw new Error('Falha ao gerar sinais');
            }
        } catch (error) {
            console.error('❌ Erro ao gerar sinais:', error);
            this.showToast('Erro ao gerar sinais', 'error');
        } finally {
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    }

    async closeTrade(tradeId) {
        try {
            const response = await fetch(`/api/close-trade/${tradeId}`, {
                method: 'POST'
            });

            if (response.ok) {
                this.showToast('Trade fechado com sucesso!', 'success');
                this.refreshData();
            } else {
                throw new Error('Falha ao fechar trade');
            }
        } catch (error) {
            console.error('❌ Erro ao fechar trade:', error);
            this.showToast('Erro ao fechar trade', 'error');
        }
    }

    refreshData() {
        if (this.isRefreshing) return;
        
        this.isRefreshing = true;
        const refreshBtn = document.getElementById('refresh-btn');
        
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }

        this.loadInitialData().finally(() => {
            this.isRefreshing = false;
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
            }
        });
    }

    setupAutoRefresh() {
        // Refresh automático a cada 30 segundos
        this.refreshInterval = setInterval(() => {
            if (this.isOnline && !document.hidden) {
                this.loadInitialData();
            }
        }, 30000);
    }

    setupPWA() {
        // Registrar Service Worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('✅ Service Worker registrado');
                })
                .catch(error => {
                    console.error('❌ Falha ao registrar Service Worker:', error);
                });
        }

        // Prompt de instalação PWA
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Mostrar botão de instalação após 30 segundos
            setTimeout(() => {
                this.showInstallPrompt(deferredPrompt);
            }, 30000);
        });
    }

    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let pullDistance = 0;
        let isPulling = false;

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!isPulling) return;
            
            currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;
            
            if (pullDistance > 0 && pullDistance < this.pullToRefreshThreshold * 2) {
                e.preventDefault();
                
                // Visual feedback do pull-to-refresh
                const progress = Math.min(pullDistance / this.pullToRefreshThreshold, 1);
                document.body.style.transform = `translateY(${pullDistance * 0.5}px)`;
                document.body.style.opacity = 1 - (progress * 0.1);
            }
        }, { passive: false });

        document.addEventListener('touchend', () => {
            if (isPulling && pullDistance > this.pullToRefreshThreshold) {
                this.refreshData();
            }
            
            // Reset visual
            document.body.style.transform = '';
            document.body.style.opacity = '';
            
            isPulling = false;
            pullDistance = 0;
        }, { passive: true });
    }

    handleTouchStart(e) {
        this.touchStartY = e.touches[0].clientY;
    }

    handleTouchMove(e) {
        // Implementar gestos personalizados se necessário
    }

    handleTouchEnd(e) {
        // Implementar gestos personalizados se necessário
    }

    handleOrientationChange() {
        // Reagir a mudanças de orientação
        console.log('📱 Orientação alterada');
        
        // Recalcular layouts se necessário
        setTimeout(() => {
            this.refreshData();
        }, 300);
    }

    updateConnectionStatus(isOnline) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            if (isOnline) {
                statusElement.className = 'fas fa-circle text-success';
            } else {
                statusElement.className = 'fas fa-circle text-danger';
            }
        }
    }

    updateLastUpdateTime() {
        const timeElement = document.getElementById('price-update-time');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = `Atualizado: ${now.toLocaleTimeString()}`;
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('d-none');
            } else {
                overlay.classList.add('d-none');
            }
        }
    }

    showToast(message, type = 'info') {
        if (this.toastCount >= this.maxToasts) {
            return; // Não mostrar mais toasts se já tiver muitos
        }

        const container = document.getElementById('toast-container');
        if (!container) return;

        const toastId = 'toast-' + Date.now();
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${iconMap[type]} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 3000
        });
        
        this.toastCount++;
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
            this.toastCount--;
        });
        
        bsToast.show();
    }

    showInstallPrompt(deferredPrompt) {
        if (!deferredPrompt) return;

        const message = 'Instalar CryptoNinja como app?';
        if (confirm(message)) {
            deferredPrompt.prompt();
            
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('✅ PWA instalado');
                }
                deferredPrompt = null;
            });
        }
    }

    pauseUpdates() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }

    resumeUpdates() {
        this.setupAutoRefresh();
        this.loadInitialData();
    }

    // Utility Methods
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'USD'
        }).format(value);
    }

    formatNumber(value) {
        if (value >= 1000) {
            return new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(value);
        }
        return value.toFixed(4);
    }

    getSignalIcon(action) {
        const icons = {
            'BUY': '↗',
            'SELL': '↘',
            'HOLD': '→'
        };
        return icons[action] || '?';
    }

    getSignalColor(action) {
        const colors = {
            'BUY': 'success',
            'SELL': 'danger',
            'HOLD': 'warning'
        };
        return colors[action] || 'secondary';
    }
}

// Utility Functions
function toggleHistory() {
    const section = document.getElementById('history-section');
    const icon = document.getElementById('history-toggle-icon');
    
    if (section && icon) {
        section.classList.toggle('show');
        
        if (section.classList.contains('show')) {
            icon.className = 'fas fa-eye-slash';
        } else {
            icon.className = 'fas fa-eye';
        }
    }
}

function quickAction(action) {
    mobileDashboard.showToast(`Ação ${action.toUpperCase()} executada!`, 'info');
}

// Inicializar Dashboard quando DOM estiver pronto
let mobileDashboard;

document.addEventListener('DOMContentLoaded', () => {
    mobileDashboard = new MobileDashboard();
});

// Exportar para uso global
window.mobileDashboard = mobileDashboard;