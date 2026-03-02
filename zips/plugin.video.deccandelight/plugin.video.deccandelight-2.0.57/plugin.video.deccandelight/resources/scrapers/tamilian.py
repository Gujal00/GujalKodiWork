'''
DeccanDelight scraper plugin
Copyright (C) 2021 gujal

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

import json
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class tamilian(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://tamilian.io/'
        self.icon = self.ipath + 'tamilian.png'
        self.list = {'01Latest Movies': self.bu + 'movies/',
                     '02Top IMDB': self.bu + 'top-imdb/',
                     '03Genres': 'menu-item-11$MMMM5',
                     '04Movies By Years': 'menu-item-65$MMMM5',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_second(self, iurl):
        """
        Get the list of categories.
        """
        cats = []
        page = client.request(self.bu)
        mlink = SoupStrainer('li', {'class': re.compile(iurl)})
        mdiv = BeautifulSoup(page, "html.parser", parse_only=mlink)
        items = mdiv.find('ul').find_all('a')
        for item in items:
            title = item.text
            url = item.get('href')
            cats.append((title, self.icon, url))

        return (cats, 7)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Tamilian')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        mdiv = BeautifulSoup(html, "html.parser")
        plink = SoupStrainer('ul', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'ml-item'})

        for item in items:
            title = self.unescape(item.find('h2').text)
            url = item.find('a').get('href')
            thumb = item.find('img').get('src')
            movies.append((title, thumb, url))

        try:
            pages = Paginator.find_all('li')
            last_pg = int(pages[-1].find('a').get('href').split('/')[-2])
            curr_pg = int(Paginator.find('li', {'class': 'active'}).text)
            if curr_pg < last_pg:
                ndiv = Paginator.find('li', {'class': 'active'}).next_sibling
                purl = ndiv.find('a').get('href')
                title = 'Next Page.. (Currently in Page {0} of {1})'.format(curr_pg, last_pg)
                movies.append((title, self.nicon, purl))
        except:
            pass

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        if 'watch.html' in url:
            wurl = urllib_parse.parse_qs(urllib_parse.urlparse(url).fragment).get('urls')
            if wurl:
                urls = json.loads(self.b64decode(wurl[0]))
                for vidhost in urls.keys():
                    vidurl = urls[vidhost]
                    if '/authenticator/' in vidurl:
                        vidurl = client.request(vidurl)
                    videos.append((vidhost, vidurl))

        html = client.request(url)
        try:
            r = re.search(r'#urls=([^&]+)', html)
            if r:
                r = json.loads(self.b64decode(r.group(1)))
                for key in r.keys():
                    vidurl = r[key]
                    if 'authenticator' in vidurl:
                        vidurl = client.request(vidurl)
                    videos.append((key, vidurl + '|User-Agent=iPad'))
        except:
            pass

        try:
            r = re.search(r'<iframe.+?src="([^"]+)', html)
            if r:
                self.resolve_media(r.group(1), videos)
        except:
            pass

        return videos
