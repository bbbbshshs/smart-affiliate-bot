import os
import time
import random
import requests
import xml.etree.ElementTree as ET

# Pega as variáveis de ambiente configuradas no GitHub
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SHOPEE_AFFILIATE_ID = "18352440043"  # Seu ID de Afiliado da Shopee

def enviar_mensagem_telegram(texto, imagem_url=None):
    """Envia uma mensagem de texto (e opcionalmente uma foto) para o Telegram."""
    if imagem_url:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHAT_ID,
            "photo": imagem_url,
            "caption": texto,
            "parse_mode": "HTML"
        }
    else:
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
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

def gerar_link_afiliado_shopee(url_produto):
    """Adiciona seu ID de afiliado a um link da Shopee."""
    if url_produto and "shopee.com.br" in url_produto:
        separador = "&" if "?" in url_produto else "?"
        return f"{url_produto}{separador}af_id={SHOPEE_AFFILIATE_ID}"
    return url_produto

def buscar_ofertas_rss():
    """Busca ofertas no feed RSS do Promobit."""
    # Feed RSS de ofertas do Promobit
    url_rss = "https://www.promobit.com.br/feed/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"📡 Buscando ofertas em: {url_rss}")
        response = requests.get(url_rss, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Faz o parse do XML do RSS
        root = ET.fromstring(response.content)
        
        # Procura por todos os itens do feed
        ofertas = []
        for item in root.findall('.//item')[:10]:  # Pega os 10 primeiros
            try:
                titulo = item.find('title').text if item.find('title') is not None else "Oferta"
                link = item.find('link').text if item.find('link') is not None else None
                descricao = item.find('description').text if item.find('description') is not None else ""
                
                if not link:
                    continue
                
                # Se for um link da Shopee, gera o link de afiliado
                link_final = gerar_link_afiliado_shopee(link)
                
                ofertas.append({
                    "titulo": titulo,
                    "link": link_final,
                    "descricao": descricao[:100] + "..." if len(descricao) > 100 else descricao
                })
            except Exception as e:
                print(f"Erro ao processar um item: {e}")
                continue
        
        print(f"✅ Encontradas {len(ofertas)} ofertas no feed.")
        return ofertas
        
    except Exception as e:
        print(f"❌ Erro ao buscar o RSS: {e}")
        return []

def main():
    print("=" * 50)
    print("🚀 Iniciando busca automática de ofertas...")
    print("=" * 50)
    
    ofertas = buscar_ofertas_rss()
    
    if not ofertas:
        print("❌ Nenhuma oferta encontrada. Nada será postado.")
        return

    # Pega uma oferta aleatória
    oferta = random.choice(ofertas)
    print(f"🎯 Oferta escolhida: {oferta['titulo']}")
    
    mensagem = (
        f"🔥 <b>ACHADINHO ENCONTRADO!</b> 🔥\n\n"
        f"📦 {oferta['titulo']}\n\n"
        f"🛒 <a href='{oferta['link']}'>Clique aqui para ver a oferta</a>"
    )
    
    enviar_mensagem_telegram(mensagem)
    print("=" * 50)

if __name__ == "__main__":
    main()
