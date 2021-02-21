import random
import requests
from bs4 import BeautifulSoup

# FIXME: This class not used - remove when possible


class RandomProxy:
    __PROXY_URL_SITE = 'https://free-proxy-list.net/'  # FIXME: don't work with twitter

    def __init__(self):
        self.__all: list[dict[str, any]] = self.__get_proxy_list()

    @property
    def all(self) -> list[dict[str, any]]:
        return self.__all

    @property
    def http(self) -> list[dict[str, any]]:
        return [_elem for _elem in self.__all if not _elem['https']]

    @property
    def https(self) -> list[dict[str, any]]:
        return [_elem for _elem in self.__all if _elem['https']]

    @property
    def random_http(self) -> dict[str, any]:
        return random.choice(self.http)

    @property
    def random_https(self) -> dict[str, any]:
        return random.choice(self.https)

    def __get_proxy_list(self) -> list[dict[str, any]]:
        _response = requests.get(self.__PROXY_URL_SITE)
        _soup = BeautifulSoup(_response.text, 'lxml')
        _table = _soup.find('table', id='proxylisttable')
        _td_items = [_elem.find_all('td') for _elem in _table.find_all('tr')]
        return [self.__get_proxy_elem(_elem) for _elem in _td_items if _elem]

    @staticmethod
    def __get_proxy_elem(items: list) -> dict[str, any]:
        return {
            'ip': items[0].text,
            'port': items[1].text,
            'code': items[2].text,
            'country': items[3].text,
            'https': bool(items[6].text == 'yes'),
        }
