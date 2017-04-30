import re
import json
import datetime as dt
from bs4 import BeautifulSoup as BS


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
    director = movie_page.get('director')
    if director is not None:
        director = director.get('name')
    movie['director'] = director
    movie['text'] = movie_page.get('text')
    movie['description'] = movie_page.get('description')
    movie['genre'] = movie_page.get('genre')
    movie['name'] = movie_page.get('name')
    duration = movie_page.get('duration')
    if duration is not None:
        duration = duration.get('name')
        duration = re.sub(r'PT(\d+)H(\d+)M', lambda m: str(int(m.group(1)) * 60 + int(m.group(2))),
                                 duration)
    movie['duration'] = duration
    release = movie_page.get('datePublished')
    year = None
    if release is not None:
        release = release[0:release.find('T')]
        year = dt.datetime.strptime(release, "%Y-%M-%d").date().strftime("%d.%M.%Y")
    movie['release'] = year
    movie['voted'] = movie_page.get('aggregateRating', {'ratingCount': 0})['ratingCount']
    movie['rating'] = movie_page.get('aggregateRating', {'ratingValue': 0})['ratingValue']
    movie['url'] = movie_page.get('url')
    movie['image'] = movie_page.get('image')

    return movie
