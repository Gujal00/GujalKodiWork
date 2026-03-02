"""
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
"""

import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class todaypk(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.todaypk.com.pk/category/'
        self.icon = self.ipath + 'todaypk.png'
        self.list = {'01Tamil Movies': self.bu + 'tamil-movies',
                     '02Telugu Movies': self.bu + 'telugu-movies',
                     '04Bollywood Movies': self.bu + 'bollywood-movies',
                     '05Hollywood Movies': self.bu + 'english-movies',
                     '06South Indian Hindi Dubbed Movies': self.bu + 'south-indian-hindi-dubbed',
                     '07Hollywood Hindi Dubbed Movies': self.bu + 'english-hindi-dubbed',
                     '08Punjabi Movies': self.bu + 'punjabi-movies',
                     '10Urdu Movies': self.bu + 'pakistani-movies',
                     '11TV Shows': self.bu + 'tv-shows',
                     '12Web Series': self.bu + 'web-series',
                     '13WWE Shows': self.bu + 'wwe-tv-shows',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + 'search_movies?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Today PK')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text
        mlink = SoupStrainer('div', {'id': 'content'})
        html = client.request(url)
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'id': re.compile('^post-')})
        for item in items:
            title = item.find('h2').a.text
            if ')' in title:
                title = title.split(')')[0] + ')'
            title = self.clean_title(title)
            url = urllib_parse.urljoin(self.bu, item.find('a')['href'])
            try:
                thumb = urllib_parse.urljoin(self.bu, item.find('img')['src'])
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'Last' in str(Paginator):
            currpg = Paginator.find('li', {'class': 'active'})
            purl = urllib_parse.urljoin(self.bu, currpg.find_next_sibling().a.get('href'))
            lurl = Paginator.find_all('li')[-1].a.get('href')
            lstpg = lurl.split('/')[-1]
            pgtxt = '{0} of {1}'.format(currpg.text, lstpg)
            title = 'Next Page... (Currently in Page {0})'.format(pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = client.request(url)
        mlink = SoupStrainer('center')
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('button', {'class': 'btn'})
            for link in links:
                a = link.find('a')
                vidurl = a.get('href')
                if '/waaw/' in vidurl:
                    vidurl = 'https://hqq.ac/e/' + vidurl.split('=')[-1]
                q = re.search(r'(\d+p)', a.text)
                vidtxt = q.group(1) if q else ''
                self.resolve_media(vidurl, videos, vidtxt)
        except:
            pass

        return videos
