import feedparser
import google.generativeai as genai
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup # Importante para achar a imagem

# Configurações
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

feeds = [
    "https://ygorganization.com/feed/",
    "https://www.yugioh-card.com/en/feed/"
]

# Imagem padrão caso a notícia não tenha nenhuma (coloque um link de uma logo do seu app ou carta genérica)
DEFAULT_IMG = "https://upload.wikimedia.org/wikipedia/en/2/2b/Yugioh_Card_Back.jpg"

def get_news():
    raw_articles = []
    
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:6]: # Analisa as 6 últimas
            
            # Tenta achar imagem no HTML da descrição
            img_url = DEFAULT_IMG
            if 'description' in entry:
                soup = BeautifulSoup(entry.description, 'html.parser')
                img_tag = soup.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
            
            # Formata para a IA ler
            raw_articles.append(f"Title: {entry.title}\nLink: {entry.link}\nImageURL: {img_url}\nContent: {entry.description[:300]}")

    if not raw_articles:
        return []

    content_to_analyze = "\n---\n".join(raw_articles)

    prompt = f"""
    Atue como expert em Yu-Gi-Oh. Das notícias abaixo, escolha as 3 mais impactantes (Meta, Banlist, Novos Arquétipos).
    
    Para cada uma:
    1. Traduza o título para PT-BR (seja breve e chamativo).
    2. Resuma em 1 linha PT-BR.
    3. Mantenha o Link original e a ImageURL exata fornecida.
    4. Data deve ser: {datetime.now().strftime("%d/%m/%Y")}.

    SAÍDA JSON OBRIGATÓRIA (Array de objetos):
    [
      {{
        "titulo": "...",
        "resumo": "...",
        "imagem": "...", 
        "link": "...",
        "data": "..."
      }}
    ]

    Notícias:
    {content_to_analyze}
    """

    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Erro: {e}")
        return []

news_data = get_news()

if news_data:
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
