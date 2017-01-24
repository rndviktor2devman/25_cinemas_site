import requests
import re
import json
import datetime as dt
from bs4 import BeautifulSoup as BS

NO_INFO = 'Информация отсутствует'


def fetch_afisha_page():
    url = "http://www.afisha.ru/msk/schedule_cinema/"
    return requests.get(url).content


def movie_refs(base_page):
    soup = BS(base_page, 'lxml')
    movie_tags = soup.findAll(string=re.compile(r'\w+'), href=re.compile(r'movie/[0-9]+'))
    return ['http:' + tag['href'] for tag in set(movie_tags)]


def parse_movie_data(raw_data):
    movie = {}
    soup = BS(raw_data, "lxml")
    raw_data = json.loads(soup.find('script', {'type': 'application/ld+json'}).text)
    movie['director'] = raw_data.get('director', {'name': NO_INFO})['name']
    movie['text'] = raw_data.get('text', NO_INFO)
    movie['description'] = raw_data.get('description', NO_INFO)
    movie['genre'] = raw_data.get('genre')
    format_duration = raw_data.get('duration', {'name': NO_INFO})['name']
    format_duration = re.sub(r'PT(\d+)H(\d+)M', lambda m: str(int(m.group(1)) * 60 + int(m.group(2))),
                             format_duration)
    if format_duration != NO_INFO:
        format_duration += ' мин.'
    movie['duration'] = format_duration
    release = raw_data.get('datePublished')
    if release is None:
        year = NO_INFO
    else:
        release = release[0:release.find('T')]
        year = dt.datetime.strptime(release, "%Y-%M-%d").date()
    movie['release'] = year
    movie['voted'] = raw_data.get('aggregateRating', {'ratingCount': 0})['ratingCount']
    movie['rating'] = raw_data.get('aggregateRating', {'ratingValue': 0})['ratingValue']
    movie['url'] = raw_data.get('url')
    movie['image'] = raw_data.get('image')
    return movie
