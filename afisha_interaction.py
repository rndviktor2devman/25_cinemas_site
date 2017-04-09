import re
import json
import datetime as dt
from bs4 import BeautifulSoup as BS

NO_INFO = 'Информация отсутствует'
STATIC_IMAGE = "static/img/no_poster.png"


def movie_refs(base_page):
    soup = BS(base_page, 'lxml')
    movie_tags = soup.findAll(string=re.compile(r'\w+'), href=re.compile(r'movie/[0-9]+'))
    return ['http:' + tag['href'] for tag in set(movie_tags)]


def json_data(page):
    soup = BS(page, 'lxml')
    return json.loads(soup.find('script', {'type': 'application/ld+json'}).text)


def parse_movie_data(movie_page):
    movie = {}
    soup = BS(movie_page, "lxml")
    movie_page = json.loads(soup.find('script', {'type': 'application/ld+json'}).text)
    movie['director'] = movie_page.get('director', {'name': NO_INFO})['name']
    movie['text'] = movie_page.get('text', NO_INFO)
    movie['description'] = movie_page.get('description', NO_INFO)
    movie['genre'] = movie_page.get('genre')
    movie['name'] = movie_page.get('name', NO_INFO)
    format_duration = movie_page.get('duration', {'name': NO_INFO})['name']
    format_duration = re.sub(r'PT(\d+)H(\d+)M', lambda m: str(int(m.group(1)) * 60 + int(m.group(2))),
                             format_duration)
    if format_duration != NO_INFO:
        format_duration += ' мин.'
    movie['duration'] = format_duration
    release = movie_page.get('datePublished')
    if release is None:
        year = NO_INFO
    else:
        release = release[0:release.find('T')]
        year = dt.datetime.strptime(release, "%Y-%M-%d").date().strftime("%d.%M.%Y")
    movie['release'] = year
    movie['voted'] = movie_page.get('aggregateRating', {'ratingCount': 0})['ratingCount']
    movie['rating'] = movie_page.get('aggregateRating', {'ratingValue': 0})['ratingValue']
    movie['url'] = movie_page.get('url')
    img_url = movie_page.get('image')
    if img_url is None:
        img_url = STATIC_IMAGE
    movie['image'] = img_url

    return movie
