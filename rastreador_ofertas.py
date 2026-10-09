import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Pega as variáveis de ambiente configuradas no GitHub
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AFFILIATE_LINK = os.getenv("AFFILIATE_LINK")
CHAT_ID = os.getenv("CHAT_ID")

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

def buscar_ofertas():
    # Configuração do Chrome para rodar no Linux (GitHub Actions)
    chrome_options = Options()
    chrome_options.add_argument('--headless') # Roda sem interface gráfica
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # Inicializa o navegador
    driver = webdriver.Chrome(options=chrome_options)
    
    ofertas_encontradas = []

    try:
        # Aqui você coloca o site que deseja raspar. 
        # Exemplo genérico: buscando em uma página de promoções.
        # Substitua pela URL real da loja que você quer monitorar.
        url_alvo = "https://www.shopee.com.br/" # Exemplo
        driver.get(url_alvo)
        time.sleep(5) # Espera a página carregar

        # Exemplo de extração (isso depende da estrutura do site alvo)
        # Neste exemplo, apenas simulamos que encontramos um produto.
        # Você precisaria inspecionar o site alvo para pegar as classes CSS corretas.
        
        # Simulação de oferta encontrada para testar o fluxo:
        ofertas_encontradas.append({
            "titulo": "Sérum Facial Anti-Idade",
            "preco_original": "R$ 89,90",
            "preco_desconto": "R$ 29,90",
            "link": AFFILIATE_LINK # Usa o link de afiliado configurado
        })

    except Exception as e:
        print(f"Erro durante a busca: {e}")
    finally:
        driver.quit()

    return ofertas_encontradas

def main():
    print("Iniciando busca de ofertas...")
    ofertas = buscar_ofertas()
    
    if not ofertas:
        print("Nenhuma oferta encontrada nesta execução.")
        return

    for oferta in ofertas:
        mensagem = (
            f"🔥 <b>ACHADINHO ENCONTRADO!</b> 🔥\n\n"
            f"📦 {oferta['titulo']}\n"
            f"❌ De: {oferta['preco_original']}\n"
            f"✅ Por: <b>{oferta['preco_desconto']}</b>\n\n"
            f"🛒 <a href='{oferta['link']}'>Clique aqui para comprar</a>"
        )
        enviar_mensagem_telegram(mensagem)
        time.sleep(2) # Pequena pausa entre mensagens

if __name__ == "__main__":
    main()
