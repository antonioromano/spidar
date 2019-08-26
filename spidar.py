
import os
import json
import requests
import validators
from bs4 import BeautifulSoup
from bs4.element import Comment
from reppy.robots import Robots
from urllib.parse import urljoin
from urllib.parse import urlparse


class Spidar:

    def __init__(self, url, limit_pages_counter=1, storage=False, meta={}, debug=False, user_agent='Spidar/1.1',
                 allow_external_link_crawling=False):
        self.__start_url = url
        parse_location = urlparse(url)
        self.__initial_domain_name = parse_location.netloc
        self.__pages = []
        self.__url_to_discover = set()
        self.__url_discovered = set()
        self.__max_counter_pages = limit_pages_counter
        self.__storage = storage
        self.__PATH_STORAGE = '__storage/'
        self.__PATH_SOURCE = self.__PATH_STORAGE + 'sources/'
        self.__PATH_INFO = self.__PATH_STORAGE + 'infos/'
        self.__meta = meta
        self.__debug = debug
        self.__user_agent = user_agent
        self.__allow_external_link_crawling = allow_external_link_crawling

        self.__rp = Robots.fetch(Robots.robots_url(self.__start_url))

        if self.__storage:
            self.__set_up_folders(self.__initial_domain_name)

    def __print_debug(self, *argv):
        if self.__debug:
            print(*argv)

    def __set_up_folders(self, domain_name):
        if not os.path.exists(self.__PATH_SOURCE + domain_name):
            os.makedirs(self.__PATH_SOURCE + domain_name)

        if not os.path.exists(self.__PATH_INFO + domain_name):
            os.makedirs(self.__PATH_INFO + domain_name)

    def crawl(self):
        self.__url_to_discover.add(self.__start_url)

        # iterate over pages in list
        while len(self.__url_to_discover) > 0:
            url = self.__url_to_discover.pop()
            self.__url_discovered.add(url)
            try:
                self.__extract_info(url)
            except Exception as e:
                self.__print_debug('EXCEPTION [a]', e)

            self.__print_debug(self.__initial_domain_name, ', to discover', len(self.__url_to_discover), 'discovered:',
                               len(self.__url_discovered), 'pages:', len(self.__pages))
            if len(self.__pages) >= self.__max_counter_pages >= 0:
                self.__print_debug('ending crawling with ', len(self.__pages), 'pages crawled')
                break

        return self.__pages

    def __add_url(self, link):
        if validators.url(link) and link not in self.__url_discovered:
            self.__url_to_discover.add(link)

    def __extract_info(self, url):

        self.__print_debug('crawling page', url)

        parsed_url = urlparse(url)
        if parsed_url.netloc == self.__initial_domain_name:
            if not self.__rp.allowed(url, self.__user_agent):
                self.__print_debug('disallowed by user agent')
                return None
        else:
            current_robot = Robots.fetch(Robots.robots_url(url))
            if not current_robot.allowed(url, self.__user_agent):
                self.__print_debug('disallowed by user agent')
                return None

        r = requests.get(url, stream=True, headers={'User-Agent': self.__user_agent})

        if 'Content-Type' not in r.headers or 'text' not in r.headers['Content-Type']:
            self.__print_debug('page does not contains text')
            r.close()
            return None
        else:
            content = b''
            is_html = 'html' in r.headers['Content-Type']
            language = None
            if 'Content-language' in r.headers:
                language = r.headers['Content-language']
            for line in r.iter_lines():
                if line:
                    content += line
            r.close()

            if r.status_code >= 300:
                return None

            path = urlparse(url).path.replace('/', '_')
            if path is None or path == '':
                path = '__index__'

            if self.__storage:
                self.__set_up_folders(parsed_url.netloc)
                fsource = open(self.__PATH_SOURCE + parsed_url.netloc + '/' + path + '.html', 'wb')
                fsource.write(content)
                fsource.close()

            if not is_html:
                self.__pages.append({'content': content, 'language': language, 'url': url, 'html': content})
                return content
            soup = BeautifulSoup(content, 'html.parser')

            for link in soup.find_all('a'):
                href = link.get('href')
                if href is None or '#' in href:
                    continue
                if href.startswith('http'):
                    self.__add_url(href)
                    continue

                if href.startswith('mailto'):
                    continue

                new_url = str(urljoin(url, href))
                self.__add_url(new_url)
            texts = soup.findAll(text=True)
            visible_texts = filter(self.__tag_visible, texts)

            visible_texts = ' '.join(t.strip() for t in visible_texts if t.strip() != '')

            if self.__storage:
                fout = open(self.__PATH_INFO + parsed_url.netloc + '/' + path + '.json', 'w')
                fout.write(json.dumps({'url': url,
                                       'domain_name': parsed_url.netloc,
                                       'html': content.decode('utf-8'),
                                       'language': language,
                                       'content': visible_texts,
                                       'meta': self.__meta, }))
                fout.close()

            self.__pages.append({'content': visible_texts,
                                 'language': language,
                                 'url': url,
                                 'html': content})

    @staticmethod
    def __tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True


def test(limit_pages=5, storage=True):
    s = Spidar('https://www.wikipedia.org', limit_pages_counter=limit_pages, storage=storage, debug=False, allow_external_link_crawling=True)
    res = s.crawl()
    print(res)


if __name__ == '__main__':

    test()
