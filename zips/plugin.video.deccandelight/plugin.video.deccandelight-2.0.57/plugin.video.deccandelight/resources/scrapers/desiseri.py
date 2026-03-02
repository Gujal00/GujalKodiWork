"""
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
"""
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class desiseri(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.desi-serials.to'
        self.icon = self.ipath + 'desiseri.png'
        self.videos = []
        self.list = {'01Star Plus': self.bu + '/star-plus-hdepisodes/',
                     '02Colors': self.bu + '/color-tv-hd/',
                     '03Zee TV': self.bu + '/zee-tv/',
                     '04Sony TV': self.bu + '/sony-tv/',
                     '05SAB TV': self.bu + '/sab-tv-hd/',
                     '06Star Bharat': self.bu + '/star-bharat/',
                     '07& TV': self.bu + '/and-tv/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu + '?s=MMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        """
        shows = []

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'porto-sicon-img'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        for source in mdiv:
            try:
                icon = source.find('img')['src']
            except:
                icon = self.icon
            url = source.find('a')['href']
            s_title = url.split('/')[-2]
            s_title = s_title.replace('-', ' ').title()
            if icon.startswith('/'):
                icon = self.bu + icon
            if 'completed shows' not in s_title.lower():
                shows.append((s_title, icon, url))
        return (shows, 7)

    def get_items(self, iurl):
        episodes = []
        if iurl[-3:] == '?s=':
            search_text = self.get_SearchQuery('Desi Serials')
            search_text = urllib_parse.quote_plus(search_text)
            iurl += search_text
        html = client.request(iurl)
        mlink = SoupStrainer('div', {'id': 'content'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        try:
            icon = mdiv.find('img')['src']
        except:
            icon = self.icon
        items = mdiv.find_all('article')
        for item in items:
            url = item.find('a')['href']
            title = self.unescape(item.find('a').text)
            title = self.clean_title(title)
            episodes.append((title, icon, url))

        plink = SoupStrainer('div', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        if 'next' in str(Paginator):
            iurl = Paginator.find('a', {'class': 'next page-numbers'}).get('href')
            currpg = Paginator.find('span', {'class': 'page-numbers current'}).text
            try:
                lastpg = Paginator.find_all('a', {'class': 'page-numbers'})[-2].text
            except:
                lastpg = 0
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            episodes.append((title, self.nicon, iurl))
        return (episodes, 8)

    def get_videos(self, iurl):
        def process_item(item):
            vid_link = item.get('href')
            vidtxt = self.unescape(item.text)
            vidtxt = re.search(r'(Part\s*\d*)', vidtxt)
            vidtxt = vidtxt.group(1) if vidtxt else ''
            self.resolve_media(vid_link, self.videos, vidtxt)

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'entry-content'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = videoclass.find_all('a', {'target': '_blank'})
        threads = []
        self.videos = []
        for item in items:
            if not (re.search(r'facebook|twitter|pinterest|protection|tumblr|reddit', str(item), re.IGNORECASE)):
                threads.append(self.Thread(process_item, item))

        [i.start() for i in threads]
        [i.join() for i in threads]

        return sorted(self.videos)
