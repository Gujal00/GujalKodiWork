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
import json
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class moviehax(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://moviehax.vip/genre/'
        self.icon = self.ipath + 'moviehax.png'
        self.list = {'01Hindi': self.bu + 'bollywood-movies/',
                     '02Netflix': self.bu + 'netflix/',
                     '03South Hindi Dubbed Movies': self.bu + 'latest-south-hindi-dubbed-movies/',
                     '04Hindi Dubbed Movies': self.bu + 'hindi-dubbed-movies/',
                     '05English': self.bu + 'hollywood/',
                     '07Punjabi': self.bu + 'new-punjabi-movie/',
                     '08Urdu': self.bu + 'pakistani-movies/',
                     '94[COLOR cyan]Adult Alt Balaji[/COLOR]': self.bu + 'altbalaji/',
                     '95[COLOR cyan]Adult Ullu[/COLOR]': self.bu + 'ullu/',
                     '96[COLOR cyan]Adult Hindi 18+[/COLOR]': self.bu + 'bollywood-18/',
                     '97[COLOR cyan]Adult English 18+[/COLOR]': self.bu + 'hollywood-18/',
                     '97[COLOR cyan]Adult Korean 18+[/COLOR]': self.bu + 'korean-18/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-6] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, iurl):
        movies = []
        if iurl[-3:] == '?s=':
            search_text = self.get_SearchQuery('Moviehax')
            search_text = urllib_parse.quote_plus(search_text)
            iurl += search_text

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'items normal'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('article', {'id': re.compile('^post')})
        for item in items:
            title = item.find('h3').text
            qual = item.find('span', {'class': 'quality'})
            if qual:
                if qual.text not in title:
                    title += ' ({0})'.format(qual.text)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon

            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            purl = Paginator.find_all('a')[-1].get('href')
            pgtxt = Paginator.find('span').text
            title = 'Next Page.. (Currently in {0})'.format(pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'content right'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        galeria = videoclass.find('div', {'class': 'galeria'})
        if galeria:
            galeria.decompose()
        mlink1 = SoupStrainer('ul', {'id': 'playeroptionsul'})
        videoclass1 = BeautifulSoup(html, "html.parser", parse_only=mlink1)

        try:
            vtabs = videoclass1.find_all('li')
            for vtab in vtabs:
                eurl = urllib_parse.urljoin(self.bu, '/wp-admin/admin-ajax.php')
                data = {
                    'action': 'doo_player_ajax',
                    'post': vtab.get('data-post'),
                    'nume': vtab.get('data-nume'),
                    'type': vtab.get('data-type')
                }
                html1 = client.request(eurl, XHR=True, referer=url, post=data)
                embed_url = json.loads(html1).get('embed_url')
                self.resolve_media(embed_url, videos, vidtxt=vtab.text)
        except:
            pass

        try:
            dclass = videoclass.find('div', {'class': 'sbox'})
            vtabs = re.findall(r'>\s*(\d+p)\s.+?href="([^"]+)', str(dclass))
            for qual, videourl in vtabs:
                self.resolve_media(videourl, videos, vidtxt=qual)
        except:
            pass

        return videos
