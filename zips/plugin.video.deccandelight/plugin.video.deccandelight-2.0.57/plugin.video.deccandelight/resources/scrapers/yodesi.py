'''
DeccanDelight scraper plugin
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
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class yodesi(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.yodesi.net/'
        self.icon = self.ipath + 'yodesi.png'
        self.videos = []
        self.list = {'01Star Plus': self.bu + 'star-plus/',
                     '02Colors': self.bu + 'colors/',
                     '03Zee TV': self.bu + 'zee-tv/',
                     '04Sony TV': self.bu + 'sony-tv/',
                     '05SAB TV': self.bu + 'sab-tv/',
                     '07Star Bharat': self.bu + 'star-bharat/',
                     '08& TV': self.bu + 'tv-and-tv/',
                     '09Star Jalsha': self.bu + 'star-jalsha/',
                     '10Star Pravah': self.bu + 'star-pravah/',
                     '11Star Vijay': self.bu + 'star-vijay/',
                     '12MTV': self.bu + 'mtv-india/',
                     '14Colors Marathi': self.bu + 'colors-marathi/',
                     '15Colors Bangla': self.bu + 'colors-bangla/',
                     '16Zee Yuva': self.bu + 'zee-yuva/',
                     '17Zee Marathi': self.bu + 'zee-marathi/',
                     '18Zee Bangla': self.bu + 'zee-bangla/',
                     '31Amazon': self.bu + 'amazon/',
                     '32Eros Now Web Series': self.bu + 'eros-now-web-series/',
                     '33Voot': self.bu + 'voot/',
                     '34ALTBalaji': self.bu + 'alt-balaji/',
                     '35Zee5': self.bu + 'zee5/',
                     '36Netflix': self.bu + 'netflix/',
                     '37Hotstar': self.bu + 'hotstar/',
                     '38MX Web Series': self.bu + 'mx-web-series/',
                     '39Vikram Bhatt Web Series': self.bu + 'vikram-bhatt-web-series/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu + '?s=MMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = client.request(iurl)
        mlink = SoupStrainer('div', {'id': 'content_box'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('div', {'class': re.compile('^one_')})
        for item in items:
            title = self.unescape(item.find('p').text)
            url = item.find('a')['href']
            try:
                icon = item.find('img')['src']
            except:
                icon = self.icon

            shows.append((title, icon, url))

        return (shows, 7)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Yo Desi!')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text
        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'main-container'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('nav', {'class': re.compile('pagination$')})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'latestPost-content'})

        for item in items:
            title = self.unescape(item.h2.text)
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextli = Paginator.find('a', {'class': 'next'})
            purl = nextli.get('href')
            currpg = Paginator.find('span', {'class': re.compile('current')}).text
            pages = Paginator.find_all('a', {'class': 'page-numbers'})
            lastpg = pages[-2].text
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        def process_item(item):
            vidurl = item.get('href')
            vidtxt = self.unescape(item.text)
            vidtxt = re.search(r'(\d.*)', vidtxt)
            vidtxt = vidtxt.group(1) if vidtxt else ''
            self.resolve_media(vidurl, self.videos, vidtxt)

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': re.compile('entry-content')})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        links = videoclass.find_all('iframe')
        for link in links:
            vidurl = link.get('src')
            self.resolve_media(vidurl, self.videos)

        links = videoclass.find_all('a', {'target': '_blank'})
        threads = []
        for link in links:
            threads.append(self.Thread(process_item, link))
        [i.start() for i in threads]
        [i.join() for i in threads]

        return sorted(self.videos)
