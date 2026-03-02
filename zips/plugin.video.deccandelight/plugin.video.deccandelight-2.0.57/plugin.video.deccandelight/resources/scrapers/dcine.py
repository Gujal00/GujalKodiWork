'''
movierulz deccandelight plugin
Copyright (C) 2016 gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse
import re


class dcine(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://desicinemas.to/category/'
        self.icon = self.ipath + 'dcine.png'
        self.videos = []
        self.list = {'01Bollywood': self.bu + 'bollywood-movies/',
                     '02Hindi Dubbed': self.bu + 'hindi-dubbed-movies/',
                     '03Punjabi': self.bu + 'punjabi-movies/',
                     '04Gujrati': self.bu + 'gujarati-movies/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Desi Cinemas')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url, headers=self.hdr)
        mlink = SoupStrainer('ul', {'class': re.compile('^MovieList')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'nav-links'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('article', {'class': 'TPost B'})

        for item in items:
            title = item.h2.text
            title = title + ' (' + item.find('span', {'class': 'Date'}).text + ')' if item.find('span', {'class': 'Date'}) else title
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['data-src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        r = Paginator.find('i', {'class': 'fa-arrow-right'})
        if r:
            purl = Paginator.find_all('a')[-1]['href']
            pre = purl.split('/')[-2]
            currpg = int(pre) - 1
            lastpg = Paginator.find_all('a', {'class': 'page-link'})[-1].text
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        def process_item(item):
            vid_link = item.get('href')
            self.resolve_media(vid_link, self.videos)

        html = client.request(url, headers=self.hdr)
        mlink = SoupStrainer('ul', {'class': re.compile('^MovieList')})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        links = videoclass.find_all('a', {'class': 'Button'})
        threads = []
        for link in links:
            threads.append(self.Thread(process_item, link))

        [i.start() for i in threads]
        [i.join() for i in threads]

        return sorted(self.videos)
