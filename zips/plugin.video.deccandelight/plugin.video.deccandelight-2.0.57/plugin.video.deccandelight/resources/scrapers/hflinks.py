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


class hflinks(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://hindilinks4u.courses//genre/'
        self.icon = self.ipath + 'hflinks.png'

        self.list = {'01Dual Audio': 'dual audio',
                     '02Hindi': 'bollywood',
                     '03Hindi Web Series': 'hindi series',
                     '04English': 'hollywood',
                     '05English Series': self.bu[:-6] + 'series/MMMM7',
                     '06Extra Movies': 'extramovies',
                     '97[COLOR cyan]Adult Erotic Movies[/COLOR]': self.bu + 'erotic-movies/MMMM7',
                     '98[COLOR cyan]Adult Hot[/COLOR]': 'hot series',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-6] + '?s='}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of categories.
        """
        cats = []
        page = client.request(self.bu[:-6])
        mlink = SoupStrainer('div', {'id': 'menu'})
        mdiv = BeautifulSoup(page, "html.parser", parse_only=mlink)
        submenus = mdiv.find_all('li', {'class': re.compile('^menu-item')})
        for submenu in submenus:
            if iurl == submenu.a.text.lower():
                title = submenu.a.text
                url = submenu.a['href']
                cats.append((title, self.icon, url))
                break
        items = submenu.find_all('li')
        for item in items:
            title = item.text
            url = item.find('a')['href']
            url = url if url.startswith('http') else self.bu[:-6] + url
            cats.append((title, self.icon, url))

        return (cats, 7)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Hindi Links 4U')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url.replace('&amp;', '&'))
        mlink = SoupStrainer('div', {'class': 'movies-list movies-list-full'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'id': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': re.compile('^ml-item')})
        for item in items:
            title = self.unescape(item.find('a')['oldtitle'])
            title = self.clean_title(title)
            iurl = item.find('a')['href']
            try:
                thumb = item.find('img')['data-original']
            except:
                thumb = self.icon
            movdet = item.find('div', {'id': 'hidden_tip'})
            if 'Adult' not in movdet.text and 'Erotic' not in movdet.text:
                movies.append((title, thumb, iurl))
            elif self.adult:
                movies.append((title, thumb, iurl))

        r = re.search('class="active".+?href="([^"]+)', str(Paginator))
        if r:
            currpg = Paginator.find('li', {'class': 'active'}).text
            lastpg = Paginator.find_all('li')[-1].find('a')['href'].split('/')[-2]
            title = 'Next Page.. (Currently in Page {} of {})'.format(currpg, lastpg)
            movies.append((title, self.nicon, r.group(1)))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = client.request(url)
        mlink = SoupStrainer('div', {'itemprop': 'description'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        mlink1 = SoupStrainer('div', {'id': 'player2'})
        videoclass1 = BeautifulSoup(html, "html.parser", parse_only=mlink1)

        try:
            vtabs = videoclass.find_all('a')
            for vtab in vtabs:
                videourl = vtab.get('href')
                if 'speedostream' in videourl or 'embdproxy' in videourl:
                    videourl = '{0}|Referer={1}'.format(videourl, self.bu[:-6])
                self.resolve_media(videourl, videos)
        except:
            pass

        try:
            vtabs = videoclass1.find_all('div', {'class': re.compile('movieplay')})
            for vtab in vtabs:
                if vtab.find('iframe') is not None:
                    videourl = vtab.find('iframe')['src']
                    if 'speedostream' in videourl or 'embdproxy' in videourl:
                        videourl = '{0}|Referer={1}'.format(videourl, self.bu[:-6])
                    self.resolve_media(videourl, videos)
        except:
            pass

        return videos
