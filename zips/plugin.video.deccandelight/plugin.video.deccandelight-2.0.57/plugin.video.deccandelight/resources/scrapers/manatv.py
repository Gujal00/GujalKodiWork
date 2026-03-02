'''
DeccanDelight scraper plugin
Copyright (C) 2018 gujal

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
import base64
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper


class manatv(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://manatelugu.com/'
        self.icon = self.ipath + 'manatv.png'
        self.list = {'01MAA TV Serials': 'MAA Serials',
                     '02Gemini TV Serials': 'Gemini Serials',
                     '03Zee Telugu Serials': 'ZEE Serials',
                     '04ETV Serials': 'ETV Serials',
                     '08TV Shows': self.bu + 'category/tv-shows/MMMM6'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        categories = []
        html = client.request(self.bu)
        mlink = SoupStrainer('li', {'class': re.compile('menu-item-460356$')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        submenus = mdiv.find_all('div', {'class': 'vc_column-inner'})

        for submenu in submenus:
            if iurl in submenu.find('a'):
                items = submenu.find_all('li')
                for item in items:
                    title = item.a.text
                    url = item.a.get('href')
                    categories.append((title, self.icon, url))
                break

        return (categories, 7)

    def get_third(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'td-main-content-wrap'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': re.compile('^page-nav')})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'td-block-span6'})
        for item in items:
            idiv = item.find('div', {'class': 'td-module-thumb'})
            title = idiv.find('a').get('title')
            title = self.unescape(title)
            title = title.encode('utf8') if self.PY2 else title
            url = idiv.find('a').get('href')
            thumb = idiv.find('img').get('src')
            shows.append((title, thumb, url))

        if 'td-icon-menu-right' in str(Paginator).lower():
            pdiv = Paginator.find_all('a')[-1]
            purl = pdiv.get('href')
            pgtxt = Paginator.find('span', {'class': 'pages'}).text.strip()
            shows.append(('Next Page.. (Currently in {0})'.format(pgtxt), self.nicon, purl))

        return (shows, 7)

    def get_items(self, url):
        movies = []
        html = client.request(url)
        html = html.replace('<br />', '</p><p>')
        mlink = SoupStrainer('div', {'class': re.compile('^td-post-content')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': re.compile('^page-nav')})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        ilink = SoupStrainer('div', {'class': 'td-post-featured-image'})
        idiv = BeautifulSoup(html, "html.parser", parse_only=ilink)

        try:
            thumb = idiv.find('img')['src']
        except:
            thumb = self.icon

        items = mdiv.find_all('p')
        for item in items:
            if 'href' in str(item):
                itxt = (item.text).replace('Click ', 'Click').replace('Here ', 'Here').replace(' OR', '')
                itxt = self.unescape(itxt)
                itxt = itxt.encode('utf8') if self.PY2 else itxt
                itxt = re.search(r'(E\d+)?.+?\s(\d.*)', itxt)
                if itxt:
                    ep = '[COLOR lime]{}[/COLOR] - '.format(itxt.group(1)) if itxt.group(1) else ''
                    title = '{}[COLOR yellow]{}[/COLOR]'.format(ep, itxt.group(2))
                    item = str(item).encode('base64') if self.PY2 else base64.b64encode(str(item).encode('utf-8'))
                    movies.append((title, thumb, item))

        if 'td-icon-menu-right' in str(Paginator).lower():
            pdiv = Paginator.find_all('a')[-1]
            purl = pdiv.get('href')
            movies.append(('Next Page..', self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        html = base64.b64decode(url).decode('utf8')
        links = re.findall('(<a.+?a>)', html, re.DOTALL)
        for link in links:
            vidurl = re.findall('href="([^"]+)', link)[0]
            vidtxt = re.findall('">([^<]+)', link)[0]
            if 'source=vidfy' in vidurl:
                url = 'http://vidfy.me/player.php?vid=' + re.findall(r'\?url=([^&]+)', vidurl)[0]
                html = client.request(url, referer=self.bu)
                if 'video is not available' not in html:
                    vidurl = re.findall('<source.+?src="([^"]+)', html)
                    if not vidurl:
                        vidurl = re.findall(r'src:\s*"([^"]+)', html)
                    if vidurl:
                        vidurl = vidurl[0] + '|Referer={}&User-Agent={}&verifypeer=false'.format(url, self.hdr['User-Agent'])
                        videos.append(('vidfy | {}'.format(vidtxt), vidurl))
            elif 'source=youtube' in vidurl:
                vidurl = 'https://www.youtube.com/embed/' + re.findall(r'\?url=([^&]+)', vidurl)[0]
                self.resolve_media(vidurl, videos, vidtxt)

        return videos
