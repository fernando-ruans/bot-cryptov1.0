#!/usr/bin/env python3
"""
Teste para verificar se a conversão de HOLD está funcionando no main.py
"""

import requests
import json
import time

def test_no_hold_api():
    """Testar API para verificar se retorna apenas BUY/SELL"""
    print("🧪 Testando API para eliminação de sinais HOLD...")
    
    # URL do endpoint
    base_url = "http://localhost:5000"
    endpoint = "/api/generate_signal"
    
    # Lista de símbolos para testar
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
    
    signals_generated = []
    
    print(f"🔍 Testando endpoint: {base_url}{endpoint}")
    
    # Testar múltiplos símbolos
    for i, symbol in enumerate(test_symbols):
        try:
            print(f"\nTeste {i+1}: {symbol}")
            
            # Fazer requisição
            response = requests.post(
                f"{base_url}{endpoint}",
                json={
                    'symbol': symbol,
                    'timeframe': '1h'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('signal'):
                    signal = data['signal']
                    signal_type = signal.get('signal_type', 'unknown')
                    confidence = signal.get('confidence', 0)
                    reasons = signal.get('reasons', [])
                    
                    signals_generated.append(signal_type)
                    
                    # Verificar se foi convertido de HOLD
                    converted = 'original_was_hold' in reasons
                    status = "CONVERTIDO" if converted else "NORMAL"
                    
                    print(f"  ✅ {signal_type.upper()} (conf: {confidence:.3f}) [{status}]")
                    
                    if converted:
                        print(f"      🔄 Original era HOLD - conversão bem-sucedida!")
                    
                else:
                    print(f"  ❌ Erro na resposta: {data.get('message', 'Unknown')}")
                    signals_generated.append('ERROR')
            
            elif response.status_code == 429:
                print(f"  ⏳ Cooldown ativo - aguardando...")
                signals_generated.append('COOLDOWN')
            
            else:
                print(f"  ❌ Erro HTTP {response.status_code}: {response.text}")
                signals_generated.append('ERROR')
                
            # Pequena pausa entre requisições
            time.sleep(2)
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Erro de conexão: {e}")
            signals_generated.append('CONNECTION_ERROR')
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            signals_generated.append('ERROR')
    
    # Análise dos resultados
    print(f"\n{'='*50}")
    print("📊 RESULTADOS:")
    
    buy_count = signals_generated.count('buy')
    sell_count = signals_generated.count('sell')
    hold_count = signals_generated.count('hold')
    error_count = len([s for s in signals_generated if s in ['ERROR', 'CONNECTION_ERROR']])
    cooldown_count = signals_generated.count('COOLDOWN')
    
    total_valid = len([s for s in signals_generated if s in ['buy', 'sell', 'hold']])
    
    if total_valid > 0:
        print(f"BUY:      {buy_count:2d} ({buy_count/total_valid*100:.1f}%)")
        print(f"SELL:     {sell_count:2d} ({sell_count/total_valid*100:.1f}%)")
        print(f"HOLD:     {hold_count:2d} ({hold_count/total_valid*100:.1f}%)")
    
    print(f"ERROS:    {error_count:2d}")
    print(f"COOLDOWN: {cooldown_count:2d}")
    
    # Verificar se objetivo foi alcançado
    if total_valid > 0:
        success = hold_count == 0
        
        if success:
            print("\n✅ SUCESSO: API não retorna mais sinais HOLD!")
            print("🎯 Sistema agora gera apenas BUY/SELL para decisões de trading!")
        else:
            print(f"\n❌ FALHA: Ainda há {hold_count} sinais HOLD retornados!")
        
        return success
    else:
        print("\n⚠️ Nenhum sinal válido foi gerado para análise.")
        print("   Verifique se o servidor está rodando e acessível.")
        return False

def test_all_pairs_endpoint():
    """Testar endpoint de todos os pares"""
    print("\n🧪 Testando endpoint de todos os pares...")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/generate_signals_all_pairs",
            json={'timeframe': '1h'},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('signals'):
                signals = data['signals']
                print(f"📊 Gerados {len(signals)} sinais:")
                
                hold_found = False
                converted_count = 0
                
                for signal in signals:
                    signal_type = signal.get('signal_type', 'unknown')
                    reasons = signal.get('reasons', [])
                    converted = 'original_was_hold' in reasons
                    
                    if signal_type == 'hold':
                        hold_found = True
                    
                    if converted:
                        converted_count += 1
                    
                    status = "CONVERTIDO" if converted else "NORMAL"
                    print(f"  {signal.get('symbol', 'UNKNOWN'):8s}: {signal_type.upper():4s} [{status}]")
                
                print(f"\n📈 Convertidos de HOLD: {converted_count}")
                
                if hold_found:
                    print("❌ Ainda há sinais HOLD sendo retornados!")
                    return False
                else:
                    print("✅ Nenhum sinal HOLD encontrado!")
                    return True
            else:
                print(f"❌ Erro na resposta: {data.get('message', 'Unknown')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Teste de API - Eliminação de sinais HOLD")
    print("⚠️  Certifique-se de que o servidor está rodando (python main.py)")
    print()
    
    # Testar endpoint individual
    success1 = test_no_hold_api()
    
    # Testar endpoint de todos os pares
    success2 = test_all_pairs_endpoint()
    
    print(f"\n{'='*60}")
    if success1 and success2:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema eliminado com sucesso os sinais HOLD!")
    else:
        print("❌ Alguns testes falharam.")
        print("   Verifique os logs para mais detalhes.")
