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


class torm(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://tormalayalam.cam/'
        self.icon = self.ipath + 'torm.png'
        self.list = {'01Movies': self.bu}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []

        html = client.request(url)
        mlink = SoupStrainer('div', {'id': 'content'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('nav', {'role': 'navigation'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('article')

        for item in items:
            title = self.unescape(item.h2.text).rstrip('Malym ')
            title = title.encode('utf8') if self.PY2 else title
            url = item.find('a')['href']
            thumb = item.find('img')['src']
            movies.append((title, thumb, url))

        try:
            pgtxt = Paginator.find('li', {'class': 'page_info'}).text
            parts = pgtxt.split(' ')
            if int(parts[1]) < int(parts[3]):
                purl = self.bu + 'page/{0}/'.format(int(parts[1]) + 1)
                title = 'Next Page.. (Currently in %s)' % pgtxt
                movies.append((title, self.nicon, purl))
        except:
            pass

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = client.request(url)
        try:
            links = re.findall(r'href="([^"]+)[^>]+>Watch<', html)
            for link in links:
                self.resolve_media(link, videos)
        except:
            pass

        mlink = SoupStrainer('div', {'class': 'video_player'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                vidurl = link.get('data-url')
                self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
