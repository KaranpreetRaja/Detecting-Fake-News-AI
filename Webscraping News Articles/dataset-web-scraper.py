import requests
from bs4 import BeautifulSoup
import csv
import re

def get_onion_article_links(url, page):
    response = requests.get(url, params={'startIndex': (page - 1) * 20})
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')
    article_links = [article.find('a')['href'] for article in articles]
    return article_links

def get_onion_article_links2(url):
    rss_url = 'https://www.theonion.com/rss'
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')
    article_links = [item.find('link').text for item in items]
    return article_links

count = 0


from urllib.parse import urljoin

def get_onion_article_links_news_in_brief(url, page, count=0):
    response = requests.get(url, params={'startIndex': (page - 1) * 20})
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')
    article_links = [article.find('a', class_='sc-1out364-0 dPMosf js_link')['href'] for article in articles if article.find('a', class_='sc-1out364-0 dPMosf js_link')]

    # Check if there's a 'Next' button to see if more pages are available.
    next_button = soup.find('a', rel='next')
    count += 1
    if next_button and count < 900:
        print("found next button " + str(count))
        next_url = urljoin(url, next_button['href'])
        return article_links + get_onion_article_links_news_in_brief(next_url, 1, count)
    else:
        return article_links


def get_bbc_article_links(url, page):
    response = requests.get(f'{url}?page={page}')
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('a', class_='gs-c-promo-heading')
    article_links = ['https://www.bbc.com' + article['href'] if article['href'].startswith('/') else article['href'] for article in articles]
    return article_links

def get_onion_article_text(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.find('div', class_='js_post-content')
    if article:
        return article.get_text().strip()
    else:
        return None

def get_bbc_article_text(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, 'lxml')
    article = soup.find('article')
    if article:
        def match_class(class_name):
            if class_name:
                return re.match(r'ssrcss-.*-Paragraph .*', class_name)
            return False

        paragraphs = article.find_all('p', class_=match_class)
        cleaned_paragraphs = [p.get_text().strip() for p in paragraphs]
        print(len(cleaned_paragraphs))
        return ' '.join(cleaned_paragraphs)
    else:
        return None

def save_to_csv(articles_list, file_name='news_articles.csv'):
    with open(file_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['text', 'label'])
        for article in articles_list:
            writer.writerow(article)


def main():
    onion_url = 'https://www.theonion.com/'
    onion_news_in_brief_url = 'https://www.theonion.com/breaking-news/news-in-brief'
    bbc_url = 'https://www.bbc.com/news'
    bbc_url2 = 'https://www.bbc.com/'
    bbc_world_url = 'https://www.bbc.com/news/world'

    articles = []

    # Fetch all Onion "News in Brief" articles
    onion_article_links_news_in_brief = get_onion_article_links_news_in_brief(onion_news_in_brief_url, 1)
    print(onion_article_links_news_in_brief)

    onion_article_links = get_onion_article_links(onion_url, 1) + get_onion_article_links2(onion_url)
    bbc_article_links = get_bbc_article_links(bbc_url, 1) + get_bbc_article_links(bbc_url2, 1) + get_bbc_article_links(bbc_world_url, 1)

    # Add Onion "News in Brief" articles for the first page
    onion_article_links += onion_article_links_news_in_brief

    for link in onion_article_links:
        print("processing: " + link)
        article_text = get_onion_article_text(link)
        if article_text:
            articles.append((article_text, 1))

    for link in bbc_article_links:
        print("processing: " + link)
        article_text = get_bbc_article_text(link)
        if article_text:
            articles.append((article_text, 0))

    save_to_csv(articles)

if __name__ == '__main__':
    main()
