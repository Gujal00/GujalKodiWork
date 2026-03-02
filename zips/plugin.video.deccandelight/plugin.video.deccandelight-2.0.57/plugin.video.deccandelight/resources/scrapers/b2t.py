'''
DeccanDelight scraper plugin
Copyright (C) 2019 gujal

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
import re

import six
from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class b2t(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.bolly2tolly.gold/category/' if self.mirror else 'https://www.bolly2tolly.net/category/'
        self.icon = self.ipath + 'b2t.png'
        self.list = {'01Tamil Movies': self.bu + 'tamil-movies',
                     '02Telugu Movies': self.bu + 'telugu-movies',
                     '03Malayalam Movies': self.bu + 'malayalam-movies',
                     '04Kannada Movies': self.bu + 'kannada-movies',
                     '11Hindi Movies': self.bu + 'hindi-movies',
                     '21English Movies': self.bu + 'english-movies',
                     '34Bengali Movies': self.bu + 'bengali-movies',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Bolly2Tolly')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        mlink = SoupStrainer('article')
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        for item in items:
            title = self.unescape(item.h3.text)
            title = self.clean_title(title)
            url = item.a.get('href')
            try:
                thumb = item.find('img')['src'].replace('-185x275', '')
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'Next' in str(Paginator):
            purl = Paginator.find('a', {'class': 'next'}).get('href')
            currpg = Paginator.find('span').text
            lastpg = Paginator.find_all('a', {'class': 'page-numbers'})[-2].text
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'TPlayer'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('div', {'class': re.compile('^TPlayerTb')})
            for link in links:
                content = self.unescape(link.contents[0])
                if isinstance(content, six.text_type):
                    link = BeautifulSoup(content, "html.parser")
                vidurl = link.find('iframe')['src']
                if 'about:' in vidurl:
                    vidurl = link.find('iframe')['data-phast-src']
                self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
