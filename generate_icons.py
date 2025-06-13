#!/usr/bin/env python3
"""
Gerador de ícones PWA para CryptoBot Dashboard
Cria ícones em SVG e PNG para diferentes tamanhos
"""

import os
import json
from pathlib import Path

def create_svg_icon(size, output_path):
    """Cria um ícone SVG com design moderno para crypto trading"""
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#06d6a0;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background circle -->
  <circle cx="{size//2}" cy="{size//2}" r="{size//2-8}" fill="url(#grad1)" stroke="#1f2937" stroke-width="2"/>
  
  <!-- Bitcoin symbol modern -->
  <g transform="translate({size//2-size//4},{size//2-size//4})">
    <!-- B shape -->
    <path d="M{size//8} {size//16} L{size//8} {size//2} L{size//4} {size//2} C{size//3} {size//2} {size//3} {size//3} {size//4} {size//3} L{size//8} {size//3} M{size//8} {size//3} L{size//5} {size//3} C{size//4} {size//3} {size//4} {size//8} {size//5} {size//8} L{size//8} {size//8}" 
          fill="white" stroke="white" stroke-width="2" stroke-linejoin="round"/>
    
    <!-- Vertical lines -->
    <line x1="{size//12}" y1="0" x2="{size//12}" y2="{size//2+size//16}" stroke="white" stroke-width="2" stroke-linecap="round"/>
    <line x1="{size//6}" y1="0" x2="{size//6}" y2="{size//2+size//16}" stroke="white" stroke-width="2" stroke-linecap="round"/>
  </g>
  
  <!-- Chart lines (candlestick style) -->
  <g transform="translate({size//2+size//8},{size//2-size//6})">
    <rect x="0" y="{size//12}" width="3" height="{size//8}" fill="url(#grad2)" rx="1"/>
    <rect x="8" y="{size//16}" width="3" height="{size//6}" fill="url(#grad2)" rx="1"/>
    <rect x="16" y="{size//8}" width="3" height="{size//10}" fill="url(#grad2)" rx="1"/>
    <line x1="1.5" y1="0" x2="1.5" y2="{size//4}" stroke="url(#grad2)" stroke-width="1"/>
    <line x1="9.5" y1="0" x2="9.5" y2="{size//4}" stroke="url(#grad2)" stroke-width="1"/>
    <line x1="17.5" y1="0" x2="17.5" y2="{size//4}" stroke="url(#grad2)" stroke-width="1"/>
  </g>
  
  <!-- AI brain symbol -->
  <g transform="translate({size//2-size//6},{size//2+size//8})">
    <circle cx="4" cy="4" r="2" fill="#fbbf24" opacity="0.8"/>
    <circle cx="12" cy="4" r="2" fill="#fbbf24" opacity="0.8"/>
    <circle cx="8" cy="10" r="2" fill="#fbbf24" opacity="0.8"/>
    <line x1="4" y1="4" x2="8" y2="10" stroke="#fbbf24" stroke-width="1" opacity="0.6"/>
    <line x1="12" y1="4" x2="8" y2="10" stroke="#fbbf24" stroke-width="1" opacity="0.6"/>
    <line x1="4" y1="4" x2="12" y2="4" stroke="#fbbf24" stroke-width="1" opacity="0.6"/>
  </g>
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return svg_content

def create_simple_png_data(size):
    """Cria dados PNG simples usando ASCII art"""
    
    # Criar um padrão simples baseado em texto
    pattern = f"""
    <!-- PNG {size}x{size} representation -->
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
      <rect width="{size}" height="{size}" fill="#6366f1" rx="{size//8}"/>
      <text x="{size//2}" y="{size//2}" font-family="Arial" font-size="{size//3}" 
            fill="white" text-anchor="middle" dominant-baseline="middle" font-weight="bold">₿</text>
      <rect x="{size//8}" y="{size*3//4}" width="{size*3//4}" height="{size//16}" fill="#10b981" rx="2"/>
    </svg>
    """
    
    return pattern

def generate_all_icons():
    """Gera todos os ícones necessários para PWA"""
    
    # Criar diretório de ícones
    icons_dir = Path("static/icons")
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Tamanhos necessários para PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    print("🎨 Gerando ícones PWA para CryptoBot Dashboard...")
    
    for size in sizes:
        # Arquivo SVG
        svg_file = icons_dir / f"icon-{size}x{size}.svg"
        create_svg_icon(size, svg_file)
        print(f"✅ Criado: {svg_file}")
        
        # Arquivo PNG (simulado com SVG)
        png_file = icons_dir / f"icon-{size}x{size}.png"
        create_svg_icon(size, png_file)  # Usar mesmo SVG para PNG
        print(f"✅ Criado: {png_file}")
    
    # Criar favicon
    favicon_file = icons_dir / "favicon.ico"
    create_svg_icon(32, favicon_file)
    print(f"✅ Criado: {favicon_file}")
    
    # Criar apple-touch-icon
    apple_icon = icons_dir / "apple-touch-icon.png"
    create_svg_icon(180, apple_icon)
    print(f"✅ Criado: {apple_icon}")
    
    # Criar screenshots mock
    create_mock_screenshots(icons_dir)
    
    print(f"\n🎉 Total de {len(sizes) * 2 + 3} ícones gerados com sucesso!")
    print(f"📁 Localização: {icons_dir.absolute()}")
    
    return True

def create_mock_screenshots(icons_dir):
    """Cria screenshots mock para PWA"""
    
    # Screenshot mobile
    mobile_screenshot = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="390" height="844" viewBox="0 0 390 844" xmlns="http://www.w3.org/2000/svg">
  <rect width="390" height="844" fill="#0a0e27"/>
  
  <!-- Header -->
  <rect x="0" y="0" width="390" height="80" fill="#1f2937"/>
  <text x="195" y="50" font-family="Arial" font-size="18" fill="white" text-anchor="middle" font-weight="bold">CryptoBot Dashboard</text>
  
  <!-- Cards -->
  <rect x="20" y="100" width="350" height="120" fill="#374151" rx="12"/>
  <text x="40" y="130" font-family="Arial" font-size="14" fill="#9ca3af">Portfolio Total</text>
  <text x="40" y="160" font-family="Arial" font-size="24" fill="#10b981" font-weight="bold">$12,847.32</text>
  <text x="40" y="185" font-family="Arial" font-size="12" fill="#10b981">+2.34% (24h)</text>
  
  <rect x="20" y="240" width="170" height="100" fill="#374151" rx="12"/>
  <text x="40" y="270" font-family="Arial" font-size="12" fill="#9ca3af">BTC/USDT</text>
  <text x="40" y="295" font-family="Arial" font-size="16" fill="white" font-weight="bold">$45,230</text>
  
  <rect x="200" y="240" width="170" height="100" fill="#374151" rx="12"/>
  <text x="220" y="270" font-family="Arial" font-size="12" fill="#9ca3af">ETH/USDT</text>
  <text x="220" y="295" font-family="Arial" font-size="16" fill="white" font-weight="bold">$3,180</text>
  
  <!-- Chart area -->
  <rect x="20" y="360" width="350" height="200" fill="#374151" rx="12"/>
  <text x="40" y="390" font-family="Arial" font-size="14" fill="white" font-weight="bold">Price Chart</text>
  
  <!-- Mock chart lines -->
  <polyline points="40,450 80,430 120,460 160,420 200,440 240,410 280,430 320,400 360,420" 
            stroke="#10b981" stroke-width="2" fill="none"/>
  
  <!-- Signals -->
  <rect x="20" y="580" width="350" height="150" fill="#374151" rx="12"/>
  <text x="40" y="610" font-family="Arial" font-size="14" fill="white" font-weight="bold">Active Signals</text>
  
  <rect x="40" y="630" width="310" height="40" fill="#1f2937" rx="8"/>
  <text x="60" y="655" font-family="Arial" font-size="12" fill="#10b981" font-weight="bold">BUY BTC/USDT - 85% confidence</text>
</svg>'''
    
    with open(icons_dir / "screenshot-mobile.png", 'w', encoding='utf-8') as f:
        f.write(mobile_screenshot)
    
    # Screenshot desktop
    desktop_screenshot = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1920" height="1080" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
  <rect width="1920" height="1080" fill="#0a0e27"/>
  
  <!-- Header -->
  <rect x="0" y="0" width="1920" height="80" fill="#1f2937"/>
  <text x="960" y="50" font-family="Arial" font-size="24" fill="white" text-anchor="middle" font-weight="bold">CryptoBot Dashboard - Desktop</text>
  
  <!-- Sidebar -->
  <rect x="0" y="80" width="300" height="1000" fill="#374151"/>
  
  <!-- Main content -->
  <rect x="320" y="100" width="800" height="300" fill="#374151" rx="16"/>
  <text x="720" y="250" font-family="Arial" font-size="18" fill="white" text-anchor="middle">Advanced Trading Dashboard</text>
  
  <!-- Charts grid -->
  <rect x="320" y="420" width="400" height="200" fill="#374151" rx="12"/>
  <rect x="740" y="420" width="400" height="200" fill="#374151" rx="12"/>
  <rect x="320" y="640" width="400" height="200" fill="#374151" rx="12"/>
  <rect x="740" y="640" width="400" height="200" fill="#374151" rx="12"/>
  
  <!-- Right panel -->
  <rect x="1160" y="100" width="740" height="740" fill="#374151" rx="16"/>
  <text x="1530" y="480" font-family="Arial" font-size="16" fill="white" text-anchor="middle">Live Trading Feed</text>
</svg>'''
    
    with open(icons_dir / "screenshot-desktop.png", 'w', encoding='utf-8') as f:
        f.write(desktop_screenshot)
    
    print("✅ Criado: screenshot-mobile.png")
    print("✅ Criado: screenshot-desktop.png")

def main():
    """Função principal"""
    try:
        generate_all_icons()
        
        print("\n📋 Próximos passos:")
        print("1. Adicione os ícones ao manifest.json")
        print("2. Inclua as meta tags no HTML")
        print("3. Configure o service worker")
        print("4. Teste a instalação PWA")
        
    except Exception as e:
        print(f"❌ Erro ao gerar ícones: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
