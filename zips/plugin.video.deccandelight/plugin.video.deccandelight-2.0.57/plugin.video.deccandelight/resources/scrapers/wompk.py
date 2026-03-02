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

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class wompk(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.watch-movies.com.pk/category/'
        self.icon = self.ipath + 'wompk.png'
        self.list = {'01Hindi Movies': 'indian movies',
                     '02Hindi Dubbed Movies': 'hindi dubbed movies',
                     '03English Movies': 'english',
                     '04Movies By Actor': 'movies by actors',
                     '05Movies By Actress': 'movies by actress',
                     '06Movies By Type': 'by type',
                     '07Punjabi': self.bu + 'watch-punjabi-movies-online/MMMM7',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s=MMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of categories.
        """
        cats = []
        page = client.request(self.bu[:-9])
        mlink = SoupStrainer('div', {'class': re.compile('^menu-shahbaz')})
        mdiv = BeautifulSoup(page, "html.parser", parse_only=mlink)

        submenus = mdiv.find_all('li', {'class': re.compile('^menu-item')})
        for submenu in submenus:
            if iurl in submenu.find('a').text.lower():
                break

        items = submenu.find_all('li')
        for item in items:
            title = item.text
            url = item.find('a')['href']
            cats.append((title, self.icon, url))

        return (cats, 7)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Movies Watch')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': re.compile('^postbox')})
        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        movies = []
        for item in items:
            title = item.h2.text
            title = title.encode('utf8') if self.PY2 else title
            if ')' in title:
                title = title.split(')')[0] + ')'
            thumb = item.img.get('data-wpfc-original-src') or item.img.get('src')
            url = item.a.get('href')
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextpg = Paginator.find('a', {'class': 'nextpostslink'})
            purl = nextpg.get('href')
            pgtxt = Paginator.find('span', {'class': 'pages'}).text
            title = 'Next Page.. (Currently in {0})'.format(pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        html = client.request(url)

        try:
            links = re.findall(r'<a\s*target="_blank"\s*href="([^"]+).+?(\d{3,4}p)', html, re.IGNORECASE)
            for link, qual in links:
                self.resolve_media(link, videos, qual)
        except:
            pass

        try:
            links = re.findall(r'<iframe.+?\ssrc="([^"]+)', html, re.IGNORECASE)
            for link in links:
                link = link if link.startswith('http') else 'https:' + link
                self.resolve_media(link, videos)
        except:
            pass

        return videos
