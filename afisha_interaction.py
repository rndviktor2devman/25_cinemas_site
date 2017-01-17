import requests
import re
import json
from bs4 import BeautifulSoup as BS

NO_INFO = 'Информация отсутствует'


def fetch_afisha_page():
    url = "http://www.afisha.ru/msk/schedule_cinema/"
    return requests.get(url).content


def movie_refs(base_page):
    soup = BS(base_page, 'lxml')
    movie_tags = soup.findAll(string=re.compile(r'\w+'), href=re.compile(r'movie/[0-9]+'))
    return ['http:' + tag['href'] for tag in movie_tags]


def parse_movie_data(raw_data):
    movie = {}
    soup = BS(raw_data, "lxml")
    raw_data = json.loads(soup.find('script', {'type': 'application/ld+json'}).text)
    movie['director'] = raw_data.get('director', {'name': NO_INFO})['name']
    movie['text'] = raw_data.get('text', NO_INFO)
    movie['description'] = raw_data.get('description', NO_INFO)
    movie['genre'] = raw_data.get('genre')
    format_duration = raw_data.get('duration', {'name': NO_INFO})['name']
    movie['duration'] = re.sub(r'PT(\d+)H(\d+M)',
                               lambda t: str(int(t.group(1)) * 60 +
                                             int(t.group(2))), format_duration)
    movie['release'] = re.sub(r'(\d{4}).*', r'\1', raw_data['datePublished'])
    movie['voted'] = raw_data.get('aggregateRating', {'ratingCount': 0})['ratingCount']
    movie['rating'] = raw_data.get('aggregateRating', {'ratingValue': 0})['ratingValue']
    movie['url'] = raw_data.get('url')
    movie['image'] = raw_data.get('image')
    return movie
