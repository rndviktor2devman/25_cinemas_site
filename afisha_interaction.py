import requests
from bs4 import BeautifulSoup as BS


def fetch_afisha_page():
    url = "http://www.afisha.ru/msk/schedule_cinema/"
    return requests.get(url).content


def parse_afisha_data(raw_data):
    soup = BS(raw_data, "lxml")
    movies = []
    for item in soup.find_all('div',
                              "object s-votes-hover-area collapsed"):
        movie = {}
        a = item.find('h3', "usetags")
        ref = a.find('a', href=True)
        movie["title"] = a.text
        movie["afishaUrl"] = "http:{}".format(ref['href'])
        table = item.find('table')
        movie["cinemas"] = len(table.find_all('tr'))
        movies.append(movie)

    return movies
