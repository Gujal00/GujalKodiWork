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


class sghar(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://serialghar.pro/'
        self.icon = self.ipath + 'sghar.png'
        self.videos = []

    def get_menu(self):
        html = client.request(self.bu)
        mlink = SoupStrainer('ul', {'id': 'menu-main-menu'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('li')
        mlist = {}
        ino = 1
        for item in items:
            title = item.find('a').text
            if 'Home' not in title and 'Bigg' not in title:
                mlist.update({'{0:02d}{1}'.format(ino, title): item.find('a').get('href')})
                ino += 1
        mlist.update({'99[COLOR yellow]** Search **[/COLOR]': '{0}?s=MMMM7'.format(self.bu)})
        return (mlist, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        """
        shows = []
        ch_name = iurl.split('/')[-2]
        html = client.request(self.bu)
        mlink = SoupStrainer('div', {'class': 'menu-{0}-container'.format(ch_name)})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.findAll('li')
        for source in items:
            url = source.find('a')['href']
            title = self.unescape(source.text).strip()
            if ch_name in url.lower():
                shows.append((title.strip(), self.icon, url))
        return (shows, 7)

    def get_items(self, iurl):
        episodes = []
        if iurl[-3:] == '?s=':
            search_text = self.get_SearchQuery('Serial Ghar')
            search_text = urllib_parse.quote_plus(search_text)
            iurl += search_text
        html = client.request(iurl)
        mlink = SoupStrainer('article', {'class': 'item-list'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        for item in mdiv:
            itemurl = item.find('h2', {'class': 'post-box-title'})
            url = itemurl.find('a')['href']
            title = self.unescape(itemurl.text)
            try:
                icon = item.find('img')['src']
            except:
                icon = self.icon
            episodes.append((title.strip(), icon, url))

        plink = SoupStrainer('div', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        if str(Paginator):
            itemurl = Paginator.find('a')
            nitemurl = itemurl.get('href')
            if itemurl:
                currpg = Paginator.find('span', {'class': 'current'}).text
                title = '(Current Page {0} Next Page: {1})'.format(currpg, itemurl.text)
                episodes.append((title, self.nicon, nitemurl))
        return (episodes, 8)

    def get_videos(self, iurl):
        def process_item(item):
            vidlink = item.get('href')
            vidtxt = self.unescape(item.text)
            vidtxt = re.search(r'(Part\s*\d*)', vidtxt)
            vidtxt = vidtxt.group(1) if vidtxt else ''
            self.resolve_media(vidlink, self.videos, vidtxt)

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'entry'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        itemdiv = videoclass.find('p')
        items = itemdiv.find_all('a')
        if not items:
            itemdiv = videoclass.find_all('p')
            items = [x.find('a') for x in itemdiv if x.find('a')]
        threads = []
        for item in items:
            threads.append(self.Thread(process_item, item))

        [i.start() for i in threads]
        [i.join() for i in threads]

        return sorted(self.videos)
