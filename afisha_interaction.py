import requests
from bs4 import BeautifulSoup as BS


def fetch_afisha_page():
    url = "http://www.afisha.ru/msk/schedule_cinema/"
    return requests.get(url).content