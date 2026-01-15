import feedparser
import google.generativeai as genai
import os
import json
from datetime import datetime

# 1. Configuração da IA
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # Modelo rápido e barato

# 2. Fontes de Notícias (RSS da YGOrganization e Konami)
feeds = [
    "https://ygorganization.com/feed/",
    "https://www.yugioh-card.com/en/feed/"
]

def get_news():
    raw_articles = []
    
    # Coleta os últimos 5 artigos de cada feed
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]: 
            raw_articles.append(f"Title: {entry.title}\nLink: {entry.link}\nSummary: {entry.description[:200]}")

    # Se não tiver notícias, para
    if not raw_articles:
        return []

    # Junta tudo num texto para a IA ler
    content_to_analyze = "\n\n".join(raw_articles)

    # 3. O Prompt para a IA (A Mágica)
    prompt = f"""
    Atue como um especialista em Yu-Gi-Oh. Analise as notícias abaixo (em inglês) e selecione as 3 mais importantes para jogadores competitivos ou colecionadores.
    
    Para cada notícia selecionada:
    1. Traduza o título para Português do Brasil (PT-BR) de forma chamativa.
    2. Faça um resumo curto de 1 linha em PT-BR.
    3. Mantenha o link original.

    Saída OBRIGATÓRIA em formato JSON puro (sem markdown), array de objetos com chaves: 'titulo', 'resumo', 'link', 'data'. A data deve ser a de hoje ({datetime.now().strftime("%Y-%m-%d")}).

    Notícias para analisar:
    {content_to_analyze}
    """

    try:
        response = model.generate_content(prompt)
        # Limpa o texto caso a IA coloque crases ```json ... ```
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Erro na IA: {e}")
        return []

# 4. Execução e Salvamento
news_data = get_news()

if news_data:
    # Salva no arquivo news.json
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print("Notícias atualizadas com sucesso!")
else:
    print("Nenhuma notícia relevante ou erro na execução.")
