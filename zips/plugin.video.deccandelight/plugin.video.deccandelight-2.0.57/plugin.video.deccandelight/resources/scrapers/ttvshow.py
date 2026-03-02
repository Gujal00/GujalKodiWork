'''
DeccanDelight scraper plugin
Copyright (C) 2023 gujal

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


class ttvshow(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'http://www.tamiltvshow.net/'
        self.icon = self.ipath + 'ttvshow.png'

    def get_menu(self):
        html = client.request(self.bu)
        mlist = {}
        mlink = SoupStrainer('nav', {'id': 'main-navigation'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.findAll('li', {'id': re.compile(r'menu-item-(?:2[1-6]|\d{5})')})
        ino = 1
        for item in items:
            mlist['{:02d}{}'.format(ino, item.find('a').text)] = item.find('a').get('href')
            ino += 1
        mlist['99[COLOR yellow]** Search **[/COLOR]'] = self.bu + '?s='
        return (mlist, 7, self.icon)

    def get_items(self, iurl):
        movies = []
        if iurl[-3:] == '?s=':
            search_text = self.get_SearchQuery('Tamil TV Show')
            search_text = urllib_parse.quote_plus(search_text)
            iurl = iurl + search_text

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': re.compile('^post-four-column')})
        plink = SoupStrainer('div', {'class': re.compile('^post-pagination')})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('article')
        for item in items:
            title = item.find('h4').text
            thumb = item.find('img').get('src')
            url = item.find('a').get('href')
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            purl = Paginator.find('a', {'class': 'next page-numbers'}).get('href')
            currpg = Paginator.find('span', {'class': 'page-numbers current'}).text
            lastpg = Paginator.find_all('a', {'class': 'page-numbers'})[-2].text
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        html = client.request(url)
        mlink = SoupStrainer('div', {'class': re.compile('^entry-content')})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                iurl = link.get('src')
                if 'videoslala.com' in iurl:
                    iurl += '$$' + urllib_parse.urljoin(url, '/')
                elif 'vimeo.com' in iurl:
                    iurl = iurl.split('?')[0] + '$$' + urllib_parse.urljoin(url, '/')
                self.resolve_media(iurl, videos)
        except:
            pass

        try:
            links = videoclass.find_all('a')
            for link in links:
                iurl = link.get('href')
                if 'http' not in iurl:
                    iurl = ''
                    click = link.get('onclick')
                    if click:
                        iurl = click[13:-16]
                        ehtml = client.request(iurl, referer=url)
                        mlink = SoupStrainer('div', {'class': 'row_player'})
                        videoclass = BeautifulSoup(ehtml, "html.parser", parse_only=mlink)
                        iurl = videoclass.find('iframe').get('src')
                if iurl:
                    if 'videoslala.com' in iurl:
                        iurl += '$$' + urllib_parse.urljoin(url, '/')
                    elif 'vimeo.com' in iurl:
                        iurl = iurl.split('?')[0] + '$$' + urllib_parse.urljoin(url, '/')
                    self.resolve_media(iurl, videos)
        except:
            pass

        return videos
