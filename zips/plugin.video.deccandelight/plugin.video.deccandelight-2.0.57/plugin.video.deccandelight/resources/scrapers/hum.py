'''
DeccanDelight scraper plugin
Copyright (C) 2017 gujal

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
from resources.lib import control, client
from resources.lib.base import Scraper


class hum(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://hum.tv/'
        self.icon = self.ipath + 'hum.png'
        self.list = {'01Dramas': self.bu + 'latest-dramas/MMMM5',
                     '02Shows': self.bu + 'awards-shows/',
                     '03Telefilms': self.bu + 'latest-telefilms/'}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        """
        shows = []

        html = client.request(iurl)
        mlink = SoupStrainer('article')
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('div', {'class': 'vc_column-inner'})
        for item in items:
            title = item.text.strip()
            url = item.find('a')['href']
            if not url.startswith('http'):
                url = 'https://' + url
            icon = item.find('img').get('src')
            shows.append((title, icon, url))

        return (shows, 7)

    def get_items(self, url):
        movies = []

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'tabs-content'}) if '/dramas/' in url \
            else SoupStrainer('div', {'class': 'vc_column-inner'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        if 'telefilms/' in url:
            items = mdiv.find_all('div', {'class': 'vc_grid-item'})
        elif '/dramas/' in url:
            items = mdiv.find_all('div', {'class': 'item'})
        else:
            items = mdiv.find_all('figure', {'class': 'wpb_wrapper'})

        for item in items:
            if item.find('a'):
                title = item.h6.text.strip() if item.h6 else item.find('img').get('alt')
                title = self.unescape(title)
                title = title.encode('utf8') if self.PY2 else title
                iurl = item.find('a').get('href')
                iurl = iurl.encode('utf8') if self.PY2 else iurl
                thumb = item.find('img').get('src') if item.find('img') else self.icon
                movies.append((title, thumb, iurl))

        if 'next' in str(Paginator):
            purl = Paginator.find('a', {'class': 'next'}).get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            lastpg = Paginator.find_all('a', {'class': 'page-numbers'})[-2].text
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 9)

    def get_video(self, url):
        videos = []
        sources = []
        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'embeded'})
        eclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        eclass = BeautifulSoup(eclass.text, "html.parser")
        items = eclass.find_all('iframe')
        for item in items:
            vidurl = item.get('src')
            vidhost = self.get_vidhost(vidurl)
            sources.append(vidhost)
            videos.append(vidurl)
        if videos:
            eurl = videos[0]
            if len(sources) > 1:
                ret = control.select('Choose a Source', sources)
                eurl = videos[ret]
            return eurl
