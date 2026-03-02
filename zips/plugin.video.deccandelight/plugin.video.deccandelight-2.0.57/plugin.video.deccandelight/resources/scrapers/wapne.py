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

import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper


class wapne(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://watchapne.to/web-series/channel/'
        self.icon = self.ipath + 'wapne.png'
        self.videos = []
        self.list = {'31ALT Balaji': self.bu + 'altbalaji',
                     '32ErosNow': self.bu + 'erosnow',
                     '33Hoichoi': self.bu + 'hoichoi',
                     '34HotStar': self.bu + 'hotstar',
                     '35Hungama': self.bu + 'hungama',
                     '36MX Originals': self.bu + 'mx-originals',
                     '37Netflix': self.bu + 'netflex',
                     '38Prime': self.bu + 'prime',
                     '39SonyLiv': self.bu + 'sonyliv',
                     '40TVF Orignals': self.bu + 'tvf-orignals',
                     '41Voot': self.bu + 'voot',
                     '42ViuOrignals': self.bu + 'viuorignals',
                     '43VB Web Series': self.bu + 'vb-web-series',
                     '44Web Movies': self.bu + 'web-movies',
                     '45Zee5': self.bu + 'zee5',
                     '46Award Shows': self.bu[:-19] + 'award-showsMMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'channel'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        try:
            thumb = mdiv.find('figure').find('img').get('src')
        except:
            thumb = self.icon
        mlink = SoupStrainer('div', {'class': 'chshows'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('li')
        for item in items:
            title = self.unescape(item.find('a').text)
            title = title.encode('utf8') if self.PY2 else title
            url = item.find('a').get('href')
            url = url.encode('utf8') if self.PY2 else url
            shows.append((title, thumb, url))

        return (shows, 7)

    def get_items(self, iurl):
        episodes = []
        html = client.request(iurl)
        if '/award-shows' in iurl:
            mlink = SoupStrainer('div', {'class': re.compile('^latest_videos_list')})
            mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
            items = mdiv.find_all('div', {'class': re.compile('web-series-grid$')})
            nmode = 7
        else:
            mlink = SoupStrainer('div', {'class': 'latest-pisode-list'})
            mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
            items = mdiv.find_all('div', {'class': re.compile('^s-epidode')})
            nmode = 8
        for item in items:
            try:
                try:
                    title = item.find('div', {'class': 'epi-name'}).text
                except AttributeError:
                    title = item.h4.text.strip()
                title = title.encode('utf8') if self.PY2 else title
                tdiv = item.find('figure')['style']
                thumb = re.findall("'([^']+)", tdiv)[0]
                url = item.a['href']
                url = url.encode('utf8') if self.PY2 else url
                episodes.append((title, thumb, url))
            except:
                pass

        plink = SoupStrainer('div', {'class': 'pagination_btns'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        if 'Next' in str(Paginator):
            nlinks = Paginator.find_all('a', {'class': 'prev_next_btns'})
            iurl = nlinks[-2].get('href')
            currpg = Paginator.find('a', {'class': re.compile('^page_active')}).text
            lastpg = nlinks[-1].get('href').split('/')[-1]
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            episodes.append((title, self.nicon, iurl))

        return (episodes, nmode)

    def get_videos(self, iurl):
        def process_item(item):
            vid_link = item.find('a')['href'] + '|Referer=' + self.bu
            self.resolve_media(vid_link, self.videos)

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'bottom_episode_list'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('li')
        threads = []
        for item in items:
            threads.append(self.Thread(process_item, item))

        [i.start() for i in threads]
        [i.join() for i in threads]

        return sorted(self.videos)
