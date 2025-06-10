/**
 * Enhanced Trading Dashboard Features
 * Funcionalidades avançadas para melhorar a experiência do usuário
 */

class EnhancedFeatures {
    constructor() {
        this.initAnimations();
        this.initInteractiveElements();
        this.initPerformanceMonitoring();
        this.initAccessibility();
    }

    /**
     * Inicializar animações avançadas
     */
    initAnimations() {
        // Animação de entrada escalonada para cards
        this.staggerCardAnimations();
        
        // Animação de contador para estatísticas
        this.initCounterAnimations();
        
        // Animações de hover aprimoradas
        this.initHoverEffects();
        
        // Animações de carregamento
        this.initLoadingAnimations();
    }

    /**
     * Animação escalonada para cards
     */
    staggerCardAnimations() {
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    /**
     * Animação de contador para números
     */
    initCounterAnimations() {
        const counters = document.querySelectorAll('.stat-card h4');
        
        const animateCounter = (element, target) => {
            const isPercent = target.includes('%');
            const isCurrency = target.includes('R$');
            const numericValue = parseFloat(target.replace(/[^\d.-]/g, ''));
            
            if (isNaN(numericValue)) return;
            
            let current = 0;
            const increment = numericValue / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= numericValue) {
                    current = numericValue;
                    clearInterval(timer);
                }
                
                let displayValue = current.toFixed(isPercent || isCurrency ? 1 : 0);
                if (isPercent) displayValue += '%';
                if (isCurrency) displayValue = 'R$ ' + displayValue;
                
                element.textContent = displayValue;
            }, 20);
        };

        // Observar quando os elementos entram na viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.animated) {
                    const target = entry.target.textContent;
                    entry.target.dataset.animated = 'true';
                    animateCounter(entry.target, target);
                }
            });
        });

        counters.forEach(counter => observer.observe(counter));
    }

    /**
     * Efeitos de hover aprimorados
     */
    initHoverEffects() {
        // Efeito de brilho nos botões
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            btn.addEventListener('mouseenter', function() {
                this.classList.add('btn-enhanced');
            });
        });

        // Efeito de levitação nos cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
                this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.2)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
            });
        });
    }

    /**
     * Animações de carregamento
     */
    initLoadingAnimations() {
        // Skeleton loading para tabelas
        this.addSkeletonLoading();
        
        // Loading spinner customizado
        this.createCustomSpinner();
    }

    /**
     * Adicionar skeleton loading
     */
    addSkeletonLoading() {
        const tableBody = document.querySelector('#tradesHistoryTable tbody');
        if (tableBody) {
            const originalContent = tableBody.innerHTML;
            
            window.showTableLoading = () => {
                tableBody.innerHTML = Array(5).fill().map(() => `
                    <tr>
                        <td><div class="shimmer" style="height: 20px; border-radius: 4px;"></div></td>
                        <td><div class="shimmer" style="height: 20px; border-radius: 4px;"></div></td>
                        <td><div class="shimmer" style="height: 20px; border-radius: 4px;"></div></td>
                        <td><div class="shimmer" style="height: 20px; border-radius: 4px;"></div></td>
                        <td><div class="shimmer" style="height: 20px; border-radius: 4px;"></div></td>
                        <td><div class="shimmer" style="height: 20px; border-radius: 4px;"></div></td>
                    </tr>
                `).join('');
            };
            
            window.hideTableLoading = () => {
                tableBody.innerHTML = originalContent;
            };
        }
    }

    /**
     * Criar spinner customizado
     */
    createCustomSpinner() {
        const style = document.createElement('style');
        style.textContent = `
            .custom-spinner {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 3px solid rgba(79, 70, 229, 0.3);
                border-radius: 50%;
                border-top-color: #4f46e5;
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Elementos interativos
     */
    initInteractiveElements() {
        // Tooltip aprimorado
        this.initTooltips();
        
        // Confirmações elegantes
        this.initConfirmations();
        
        // Feedback tátil
        this.initHapticFeedback();
    }

    /**
     * Tooltips aprimorados
     */
    initTooltips() {
        const createTooltip = (element, text) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = text;
            tooltip.style.cssText = `
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 14px;
                pointer-events: none;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.3s ease;
                backdrop-filter: blur(10px);
            `;
            document.body.appendChild(tooltip);
            
            element.addEventListener('mouseenter', (e) => {
                const rect = element.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
                tooltip.style.opacity = '1';
            });
            
            element.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
            });
        };

        // Adicionar tooltips aos botões importantes
        const tooltipElements = [
            { selector: '#generateSignalBtn', text: 'Gera um novo sinal baseado em IA' },
            { selector: '#confirmSignalBtn', text: 'Executa o trade com o sinal atual' },
            { selector: '#rejectSignalBtn', text: 'Rejeita o sinal atual' },
            { selector: '#refreshHistoryBtn', text: 'Atualiza o histórico de trades' }
        ];

        tooltipElements.forEach(({ selector, text }) => {
            const element = document.querySelector(selector);
            if (element) createTooltip(element, text);
        });
    }

    /**
     * Confirmações elegantes
     */
    initConfirmations() {
        const createConfirmModal = (title, message, onConfirm) => {
            const modal = document.createElement('div');
            modal.className = 'custom-confirm-modal';
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 2000;
                opacity: 0;
                transition: opacity 0.3s ease;
                backdrop-filter: blur(5px);
            `;
            
            modal.innerHTML = `
                <div class="modal-content" style="
                    background: white;
                    padding: 2rem;
                    border-radius: 20px;
                    max-width: 400px;
                    text-align: center;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                    transform: scale(0.8);
                    transition: transform 0.3s ease;
                ">
                    <h5 style="margin-bottom: 1rem; color: #1e293b;">${title}</h5>
                    <p style="margin-bottom: 2rem; color: #64748b;">${message}</p>
                    <div style="display: flex; gap: 1rem;">
                        <button class="btn btn-secondary flex-fill cancel-btn">Cancelar</button>
                        <button class="btn btn-primary flex-fill confirm-btn">Confirmar</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            setTimeout(() => {
                modal.style.opacity = '1';
                modal.querySelector('.modal-content').style.transform = 'scale(1)';
            }, 10);
            
            modal.querySelector('.cancel-btn').onclick = () => {
                modal.style.opacity = '0';
                setTimeout(() => modal.remove(), 300);
            };
            
            modal.querySelector('.confirm-btn').onclick = () => {
                onConfirm();
                modal.style.opacity = '0';
                setTimeout(() => modal.remove(), 300);
            };
            
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.style.opacity = '0';
                    setTimeout(() => modal.remove(), 300);
                }
            };
        };

        // Adicionar confirmação aos botões críticos
        const criticalButtons = document.querySelectorAll('[onclick*="closeTrade"]');
        criticalButtons.forEach(btn => {
            const originalOnclick = btn.onclick;
            btn.onclick = null;
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                createConfirmModal(
                    'Confirmar Fechamento',
                    'Tem certeza que deseja fechar este trade?',
                    originalOnclick
                );
            });
        });
    }

    /**
     * Feedback tátil
     */
    initHapticFeedback() {
        const vibrate = (pattern) => {
            if ('vibrate' in navigator) {
                navigator.vibrate(pattern);
            }
        };

        // Vibração suave nos cliques
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', () => vibrate(50));
        });

        // Vibração de sucesso/erro
        window.vibrateSuccess = () => vibrate([100, 50, 100]);
        window.vibrateError = () => vibrate([200, 100, 200]);
    }

    /**
     * Monitoramento de performance
     */
    initPerformanceMonitoring() {
        // Monitor de FPS
        this.initFPSMonitor();
        
        // Monitor de memória
        this.initMemoryMonitor();
        
        // Otimizações automáticas
        this.initAutoOptimizations();
    }

    /**
     * Monitor de FPS
     */
    initFPSMonitor() {
        let lastTime = performance.now();
        let frameCount = 0;
        let fps = 0;

        const measureFPS = (currentTime) => {
            frameCount++;
            if (currentTime - lastTime >= 1000) {
                fps = Math.round(frameCount * 1000 / (currentTime - lastTime));
                frameCount = 0;
                lastTime = currentTime;
                
                // Otimizar se FPS baixo
                if (fps < 30) {
                    this.reducedMotion();
                }
            }
            requestAnimationFrame(measureFPS);
        };

        requestAnimationFrame(measureFPS);
    }

    /**
     * Monitor de memória
     */
    initMemoryMonitor() {
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                const usage = memory.usedJSHeapSize / memory.jsHeapSizeLimit;
                
                if (usage > 0.8) {
                    this.optimizeMemory();
                }
            }, 10000);
        }
    }

    /**
     * Otimizações automáticas
     */
    initAutoOptimizations() {
        // Lazy loading para imagens
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));

        // Debounce para eventos de scroll/resize
        this.debounceEvents();
    }

    /**
     * Reduzir animações para melhor performance
     */
    reducedMotion() {
        document.documentElement.style.setProperty('--animation-duration', '0.1s');
        console.log('Performance otimizada: animações reduzidas');
    }

    /**
     * Otimizar uso de memória
     */
    optimizeMemory() {
        // Limpar listeners não utilizados
        const unusedElements = document.querySelectorAll('.unused');
        unusedElements.forEach(el => el.remove());
        
        // Forçar garbage collection se disponível
        if ('gc' in window) {
            window.gc();
        }
        
        console.log('Memória otimizada');
    }

    /**
     * Debounce para eventos
     */
    debounceEvents() {
        const debounce = (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        };

        // Debounce para resize
        window.addEventListener('resize', debounce(() => {
            // Reajustar layout se necessário
            console.log('Layout reajustado');
        }, 250));
    }

    /**
     * Recursos de acessibilidade
     */
    initAccessibility() {
        // Navegação por teclado
        this.initKeyboardNavigation();
        
        // Alto contraste
        this.initHighContrast();
        
        // Leitor de tela
        this.initScreenReader();
    }

    /**
     * Navegação por teclado
     */
    initKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Esc para fechar modais
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.custom-confirm-modal');
                modals.forEach(modal => modal.click());
            }
            
            // Enter/Space para ativar botões focados
            if ((e.key === 'Enter' || e.key === ' ') && e.target.classList.contains('btn')) {
                e.target.click();
            }
        });

        // Indicadores de foco visíveis
        const style = document.createElement('style');
        style.textContent = `
            .btn:focus {
                outline: 2px solid #4f46e5;
                outline-offset: 2px;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Modo alto contraste
     */
    initHighContrast() {
        const toggleHighContrast = () => {
            document.body.classList.toggle('high-contrast');
        };

        // Detectar preferência do sistema
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            toggleHighContrast();
        }

        // Adicionar CSS para alto contraste
        const style = document.createElement('style');
        style.textContent = `
            .high-contrast {
                filter: contrast(150%);
            }
            .high-contrast .card {
                border: 2px solid #000;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Suporte para leitores de tela
     */
    initScreenReader() {
        // Adicionar labels ARIA onde necessário
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            if (!btn.getAttribute('aria-label') && !btn.textContent.trim()) {
                const icon = btn.querySelector('i');
                if (icon) {
                    const iconClass = icon.className;
                    let label = 'Botão';
                    if (iconClass.includes('fa-magic')) label = 'Gerar sinal';
                    if (iconClass.includes('fa-check')) label = 'Confirmar';
                    if (iconClass.includes('fa-times')) label = 'Rejeitar';
                    btn.setAttribute('aria-label', label);
                }
            }
        });

        // Anunciar mudanças importantes
        window.announceToScreenReader = (message) => {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            document.body.appendChild(announcement);
            
            setTimeout(() => announcement.remove(), 3000);
        };
    }
}

// Inicializar recursos avançados quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎨 Inicializando recursos avançados...');
    window.enhancedFeatures = new EnhancedFeatures();
});

// Exportar para uso global
window.EnhancedFeatures = EnhancedFeatures;
