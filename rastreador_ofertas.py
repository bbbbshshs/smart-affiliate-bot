import os
import random
import requests
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SHOPEE_AFFILIATE_ID = "18352440043"

# Lista de feeds RSS confiáveis (em ordem de prioridade)
FEEDS_RSS = [
    "https://www.hardmob.com.br/forums/407-Promo%C3%A7%C3%B5es.rss",
    "https://www.pelando.com.br/rss/feed.xml",
    "https://www.promobit.com.br/rss/",
]

def enviar_mensagem_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, data=payload, timeout=20)
        response.raise_for_status()
        print("✅ Mensagem enviada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

def gerar_link_afiliado_shopee(url_produto):
    """Adiciona seu ID de afiliado a um link da Shopee."""
    if url_produto and "shopee.com.br" in url_produto:
        separador = "&" if "?" in url_produto else "?"
        return f"{url_produto}{separador}af_id={SHOPEE_AFFILIATE_ID}"
    return None

def buscar_ofertas_feed(url_rss):
    """Busca ofertas em um feed RSS específico."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"📡 Tentando: {url_rss}")
        response = requests.get(url_rss, headers=headers, timeout=20)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ofertas = []
        
        for item in root.findall('.//item'):
            try:
                titulo = item.find('title').text if item.find('title') is not None else None
                link = item.find('link').text if item.find('link') is not None else None
                
                if not titulo or not link:
                    continue
                
                # Verifica se o link é da Shopee
                link_afiliado = gerar_link_afiliado_shopee(link)
                
                # Se não for Shopee, pula
                if not link_afiliado:
                    continue
                
                ofertas.append({
                    "titulo": titulo.strip(),
                    "link": link_afiliado
                })
            except Exception:
                continue
        
        print(f"   → {len(ofertas)} ofertas da Shopee encontradas neste feed.")
        return ofertas
        
    except Exception as e:
        print(f"   ❌ Erro neste feed: {e}")
        return []

def main():
    print("=" * 50)
    print("🚀 Iniciando busca automática de ofertas...")
    print("=" * 50)
    
    todas_ofertas = []
    
    for url_feed in FEEDS_RSS:
        ofertas = buscar_ofertas_feed(url_feed)
        todas_ofertas.extend(ofertas)
        
        # Se já encontrou 5 ou mais ofertas, para de buscar
        if len(todas_ofertas) >= 5:
            break
    
    if not todas_ofertas:
        print("❌ Nenhuma oferta da Shopee encontrada. Nada será postado.")
        return
    
    # Pega uma oferta aleatória
    oferta = random.choice(todas_ofertas)
    print(f"🎯 Oferta escolhida: {oferta['titulo'][:80]}")
    
    mensagem = (
        f"🔥 <b>ACHADINHO ENCONTRADO!</b> 🔥\n\n"
        f"📦 {oferta['titulo']}\n\n"
        f"🛒 <a href='{oferta['link']}'>Clique aqui para ver a oferta</a>"
    )
    
    enviar_mensagem_telegram(mensagem)
    print("=" * 50)

if __name__ == "__main__":
    main()
