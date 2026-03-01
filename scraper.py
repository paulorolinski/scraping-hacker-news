#Scraping do Hacker News

import re
import time
import requests
import tldextract
from datetime import datetime
from bs4 import BeautifulSoup
from country import get_domain_country
from database import collection


def scrape_hacker_news():
    print("Iniciando scraping de TODOS os posts disponíveis no Hacker News...")

    page = 1
    has_next_page = True

    while has_next_page:
        print(f"\n--- Lendo Página {page} ---")
        soup = _fetch_page(page)
        posts = soup.find_all('tr', class_='athing')

        if not posts:
            break

        for post in posts:
            post_data = _parse_post(post)
            if post_data:
                _save_post(post_data)

        morelink = soup.find('a', class_='morelink')
        if morelink:
            page += 1
            time.sleep(1)
        else:
            has_next_page = False
            print("\nÚltima página alcançada! Scraping concluído.")


def _fetch_page(page):
    """Baixa e parseia o HTML de uma página"""
    url = f"https://news.ycombinator.com/?p={page}"
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def _parse_post(post):
    """Extrai os dados de um post"""
    title_tag = post.find('span', class_='titleline').find('a')
    title = title_tag.text if title_tag else "Sem título"
    link  = title_tag['href'] if title_tag else ""

    full_domain, tld = _extract_domain(link)

    subtext = post.find_next_sibling('tr').find('td', class_='subtext')

    if not subtext.find('span', class_='score'):
        return None

    points   = _parse_points(subtext)
    author   = _parse_author(subtext)
    posted_at = _parse_date(subtext)
    comments = _parse_comments(subtext)
    country  = get_domain_country(tld)

    return {
        "title":    title,
        "postedAt": posted_at,
        "author":   author,
        "points":   points,
        "comments": comments,
        "domain":   full_domain,
        "tld":      tld,
        "country":  country,
    }


def _extract_domain(link):
    """Retorna (full_domain, tld) a partir de um link."""
    if link.startswith('item?id='):
        return "news.ycombinator.com", ".com"

    ext = tldextract.extract(link)
    full_domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
    tld = f".{ext.suffix}" if ext.suffix else ""
    return full_domain, tld


def _parse_points(subtext):
    score_str = subtext.find('span', class_='score').text
    return int(re.search(r'\d+', score_str).group())


def _parse_author(subtext):
    author_tag = subtext.find('a', class_='hnuser')
    return author_tag.text if author_tag else "Desconhecido"


def _parse_date(subtext):
    age_tag = subtext.find('span', class_='age')
    if age_tag and age_tag.get('title'):
        data_limpa = age_tag['title'].split(' ')[0]
        return datetime.fromisoformat(data_limpa.replace('Z', '+00:00')).strftime('%Y-%m-%dT%H:%M:%SZ')
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def _parse_comments(subtext):
    links = subtext.find_all('a')
    if links:
        last = links[-1].text
        if 'comment' in last:
            return int(re.search(r'\d+', last).group())
    return 0


def _save_post(post_data):
    """Faz upsert do post no MongoDB"""
    try:
        collection.update_one(
            {"title": post_data["title"]},
            {"$set": post_data},
            upsert=True
        )
        print(f"Salvo: {post_data['title'][:30]:<30} | Domínio: {post_data['domain']:<20} | País: {post_data['country']}")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
