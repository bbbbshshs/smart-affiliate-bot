import os
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Pega as variáveis de ambiente configuradas no GitHub
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SHOPEE_AFFILIATE_ID = "18352440043"  # Seu ID de Afiliado da Shopee

def enviar_mensagem_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def buscar_ofertas_promobit():
    """Busca ofertas no site Promobit."""
    url = "https://www.promobit.com.br/" 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ofertas = []
        # O seletor CSS abaixo deve ser ajustado de acordo com a estrutura do site.
        # Este é um exemplo genérico para pegar cards de ofertas.
        for card in soup.select('.card-offer, .offer-card, .promo-card')[:5]:
            try:
                titulo = card.select_one('.title, .offer-title, h2').get_text(strip=True)
                link_tag = card.select_one('a')
                link_produto = link_tag['href'] if link_tag else None
                
                if not link_produto:
                    continue

                # Tenta extrair o preço
                preco_tag = card.select_one('.price, .offer-price, .sale-price')
                preco = preco_tag.get_text(strip=True) if preco_tag else "Ver preço"
                
                # Gera o link de afiliado da Shopee
                link_afiliado = gerar_link_afiliado_shopee(link_produto)
                
                if link_afiliado:
                    ofertas.append({
                        "titulo": titulo,
                        "preco": preco,
                        "link": link_afiliado
                    })
            except Exception as e:
                print(f"Erro ao processar um card de oferta: {e}")
                continue
        
        return ofertas
    except Exception as e:
        print(f"Erro ao buscar ofertas no Promobit: {e}")
        return []

def gerar_link_afiliado_shopee(url_produto):
    """
    Gera um link de afiliado da Shopee a partir de uma URL de produto.
    Este método simula a conversão que o portal de afiliados faz.
    """
    # Formato de link de afiliado da Shopee (simplificado)
    # Exemplo: https://shopee.com.br/product/123456/78910?af_id=18352440043
    if "shopee.com.br" in url_produto:
        separador = "&" if "?" in url_produto else "?"
        return f"{url_produto}{separador}af_id={SHOPEE_AFFILIATE_ID}"
    return None

def main():
    print("Iniciando garimpo de ofertas no Promobit...")
    ofertas = buscar_ofertas_promobit()
    
    if not ofertas:
        print("Nenhuma oferta encontrada nesta execução.")
        return

    # Pega uma oferta aleatória
    oferta = random.choice(ofertas)
    
    mensagem = (
        f"🔥 <b>ACHADINHO ENCONTRADO!</b> 🔥\n\n"
        f"📦 {oferta['titulo']}\n"
        f"💰 Por: <b>{oferta['preco']}</b>\n\n"
        f"🛒 <a href='{oferta['link']}'>Clique aqui para comprar</a>"
    )
    
    enviar_mensagem_telegram(mensagem)

if __name__ == "__main__":
    main()
