#!/usr/bin/env python3

# Teste simples da lógica corrigida
buy_signals = [0.4, 0.5]  # RSI + MACD (exemplo do debug anterior)
sell_signals = [0.4, 0.5]  # EMA + ADX (exemplo do debug anterior)

buy_strength = sum(buy_signals)  # 0.9
sell_strength = sum(sell_signals)  # 0.9

print(f"Buy strength: {buy_strength}")
print(f"Sell strength: {sell_strength}")

# Lógica corrigida
min_strength = 0.4
min_diff = 0.2

if buy_strength >= min_strength and buy_strength > sell_strength + min_diff:
    signal_type = 'buy'
    confidence = min(buy_strength / 2.0, 1.0)
    print(f"Resultado: BUY (confiança: {confidence:.2f}) - Diferença suficiente")
elif sell_strength >= min_strength and sell_strength > buy_strength + min_diff:
    signal_type = 'sell'
    confidence = min(sell_strength / 2.0, 1.0)
    print(f"Resultado: SELL (confiança: {confidence:.2f}) - Diferença suficiente")
elif buy_strength >= min_strength and buy_strength > sell_strength:
    signal_type = 'buy'
    confidence = min(buy_strength / 3.0, 0.6)
    print(f"Resultado: BUY (confiança: {confidence:.2f}) - Buy maior, diferença pequena")
elif sell_strength >= min_strength and sell_strength > buy_strength:
    signal_type = 'sell'
    confidence = min(sell_strength / 3.0, 0.6)
    print(f"Resultado: SELL (confiança: {confidence:.2f}) - Sell maior, diferença pequena")
elif buy_strength >= min_strength and buy_strength == sell_strength:
    # Empate - escolher baseado no primeiro sinal mais forte
    max_buy = max(buy_signals) if buy_signals else 0
    max_sell = max(sell_signals) if sell_signals else 0
    if max_buy >= max_sell:
        signal_type = 'buy'
        confidence = min(buy_strength / 2.2, 0.6)
        print(f"Resultado: BUY (confiança: {confidence:.2f}) - Empate, max buy signal prevalece")
    else:
        signal_type = 'sell'
        confidence = min(sell_strength / 2.2, 0.6)
        print(f"Resultado: SELL (confiança: {confidence:.2f}) - Empate, max sell signal prevalece")
else:
    signal_type = 'hold'
    confidence = 0.0
    print(f"Resultado: HOLD (confiança: {confidence:.2f}) - Força insuficiente")

print(f"\nComparando com min_confidence: 0.4")
print(f"Sinal passaria? {confidence >= 0.4}")
