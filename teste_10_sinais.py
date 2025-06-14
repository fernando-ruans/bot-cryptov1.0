#!/usr/bin/env python3
"""
Teste robusto com 10 sinais para verificar se o viés BUY foi corrigido
"""

import requests
import json
import time
from datetime import datetime
from collections import Counter

def test_10_signals():
    """Testa 10 sinais para verificar distribuição BUY/SELL"""
    
    print("🎯 TESTE ROBUSTO - 10 SINAIS PARA VERIFICAR VIÉS")
    print("=" * 60)
    
    resultados = []
    contador_sinais = Counter()
    
    # Lista de ativos diferentes para variar as condições
    ativos = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", 
              "SOLUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "AVAXUSDT"]
    
    # Timeframes diferentes para variar análise
    timeframes = ["5m", "15m", "1h", "4h"]
    
    for i in range(10):
        # Usar ativo e timeframe diferentes a cada iteração
        ativo = ativos[i % len(ativos)]
        timeframe = timeframes[i % len(timeframes)]
        
        print(f"\n[{i+1}/10] 🔍 Testando {ativo} {timeframe}...")
        
        try:
            # Fazer requisição
            response = requests.post(
                "http://localhost:5000/api/generate_signal",
                json={
                    "symbol": ativo,
                    "timeframe": timeframe
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair signal_type
                signal_info = data.get('signal', {})
                signal_type = signal_info.get('signal_type')
                confidence = signal_info.get('confidence', 0)
                
                if signal_type:
                    contador_sinais[signal_type.upper()] += 1
                    
                    resultado = {
                        "teste": i + 1,
                        "ativo": ativo,
                        "timeframe": timeframe,
                        "signal_type": signal_type.upper(),
                        "confidence": confidence,
                        "timestamp": datetime.now().isoformat(),
                        "sucesso": True
                    }
                    
                    print(f"    ✅ {signal_type.upper()} (confiança: {confidence:.3f})")
                    
                else:
                    resultado = {
                        "teste": i + 1,
                        "ativo": ativo,
                        "timeframe": timeframe,
                        "signal_type": "NULL",
                        "confidence": 0,
                        "timestamp": datetime.now().isoformat(),
                        "sucesso": False,
                        "erro": "Signal_type não encontrado"
                    }
                    contador_sinais["NULL"] += 1
                    print(f"    ❌ NULL - Signal type não encontrado")
                
                resultados.append(resultado)
                
            else:
                print(f"    ❌ Erro API: {response.status_code}")
                resultado = {
                    "teste": i + 1,
                    "ativo": ativo,
                    "timeframe": timeframe,
                    "signal_type": "ERROR",
                    "confidence": 0,
                    "timestamp": datetime.now().isoformat(),
                    "sucesso": False,
                    "erro": f"HTTP {response.status_code}"
                }
                resultados.append(resultado)
                contador_sinais["ERROR"] += 1
            
            # Pausa entre requisições para não sobrecarregar
            time.sleep(2)
            
        except Exception as e:
            print(f"    ❌ Exceção: {str(e)}")
            resultado = {
                "teste": i + 1,
                "ativo": ativo,
                "timeframe": timeframe,
                "signal_type": "EXCEPTION",
                "confidence": 0,
                "timestamp": datetime.now().isoformat(),
                "sucesso": False,
                "erro": str(e)
            }
            resultados.append(resultado)
            contador_sinais["EXCEPTION"] += 1
    
    # Análise dos resultados
    print("\n" + "="*60)
    print("📊 ANÁLISE DOS RESULTADOS - 10 SINAIS")
    print("="*60)
    
    total_testes = len(resultados)
    total_sucessos = sum(1 for r in resultados if r['sucesso'])
    
    print(f"📈 ESTATÍSTICAS GERAIS:")
    print(f"  Total de testes: {total_testes}")
    print(f"  Sucessos: {total_sucessos}")
    print(f"  Falhas: {total_testes - total_sucessos}")
    print(f"  Taxa de sucesso: {(total_sucessos/total_testes)*100:.1f}%")
    
    print(f"\n🎯 DISTRIBUIÇÃO DE SINAIS:")
    for signal_type, count in contador_sinais.most_common():
        percentage = (count / total_testes) * 100
        print(f"  {signal_type}: {count} ({percentage:.1f}%)")
    
    # Análise de viés
    buy_count = contador_sinais.get("BUY", 0)
    sell_count = contador_sinais.get("SELL", 0)
    hold_count = contador_sinais.get("HOLD", 0)
    
    valid_signals = buy_count + sell_count + hold_count
    
    if valid_signals > 0:
        print(f"\n📋 SINAIS VÁLIDOS: {valid_signals}")
        print(f"  BUY: {buy_count} ({(buy_count/valid_signals)*100:.1f}%)")
        print(f"  SELL: {sell_count} ({(sell_count/valid_signals)*100:.1f}%)")
        print(f"  HOLD: {hold_count} ({(hold_count/valid_signals)*100:.1f}%)")
        
        print(f"\n🔍 ANÁLISE DE VIÉS:")
        
        if sell_count == 0 and buy_count > 0:
            print(f"  🚨 VIÉS CRÍTICO: 100% BUY - NENHUM SELL!")
            print(f"      ❌ BUG AINDA NÃO FOI CORRIGIDO")
            
        elif buy_count == 0 and sell_count > 0:
            print(f"  🚨 VIÉS CRÍTICO: 100% SELL - NENHUM BUY!")
            print(f"      ❌ BUG INVERTIDO")
            
        elif abs(buy_count - sell_count) <= 2:  # Diferença de até 2 sinais é aceitável em 10 testes
            print(f"  ✅ DISTRIBUIÇÃO EQUILIBRADA!")
            print(f"      ✅ BUG APARENTA ESTAR CORRIGIDO")
            
        elif buy_count > sell_count:
            bias_percentage = ((buy_count - sell_count) / valid_signals) * 100
            if bias_percentage > 60:
                print(f"  ⚠️  VIÉS MODERADO PARA BUY ({bias_percentage:.1f}% diferença)")
                print(f"      🔧 MELHORIA NECESSÁRIA")
            else:
                print(f"  ⚖️  LEVE TENDÊNCIA PARA BUY ({bias_percentage:.1f}% diferença)")
                print(f"      ✅ DENTRO DO ACEITÁVEL")
                
        else:
            bias_percentage = ((sell_count - buy_count) / valid_signals) * 100
            if bias_percentage > 60:
                print(f"  ⚠️  VIÉS MODERADO PARA SELL ({bias_percentage:.1f}% diferença)")
                print(f"      🔧 MELHORIA NECESSÁRIA")
            else:
                print(f"  ⚖️  LEVE TENDÊNCIA PARA SELL ({bias_percentage:.1f}% diferença)")
                print(f"      ✅ DENTRO DO ACEITÁVEL")
        
        # Estatísticas detalhadas
        print(f"\n📊 DETALHES DOS TESTES:")
        for i, resultado in enumerate(resultados, 1):
            if resultado['sucesso']:
                print(f"  [{i}] {resultado['ativo']} {resultado['timeframe']}: {resultado['signal_type']} (conf: {resultado['confidence']:.3f})")
            else:
                print(f"  [{i}] {resultado['ativo']} {resultado['timeframe']}: ❌ {resultado.get('erro', 'Erro desconhecido')}")
    
    else:
        print(f"❌ NENHUM SINAL VÁLIDO ENCONTRADO!")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"teste_10_sinais_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_testes": total_testes,
            "sucessos": total_sucessos,
            "distribuicao": dict(contador_sinais),
            "resultados_detalhados": resultados
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {filename}")
    print(f"\n✅ Teste de 10 sinais concluído!")

if __name__ == "__main__":
    test_10_signals()
