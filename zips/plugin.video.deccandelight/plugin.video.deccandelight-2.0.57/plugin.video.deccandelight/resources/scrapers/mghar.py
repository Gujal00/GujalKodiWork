'''
DeccanDelight scraper plugin
Copyright (C) 2021 gujal

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


class mghar(Scraper):
    def __init__(self):
        Scraper.__init__(self)

        self.bu = 'https://www.watch-movies.com.pk/category/'
        self.icon = self.ipath + 'mghar.png'
        self.list = {'11Hindi Movies': self.bu + 'indian-movies/',
                     '12Hindi Dubbed Movies': self.bu + 'watch-hindi-dubbed-full-movies/',
                     '13English Movies': self.bu + 'english-movies-free/',
                     '14Web Series': self.bu + 'shows-series/',
                     '15Punjabi Movies': self.bu + 'watch-punjabi-movies-online/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Movies Ghar')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'postcont'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('div', {'class': re.compile('^postbox')})
        #
        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        for item in items:
            title = self.unescape(item.h2.a['title'])
            if ')' in title:
                title = title.split(')')[0] + ')'
            title = self.clean_title(title)
            url = item.a.get('href')
            try:
                thumb = item.find('img')['data-src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            purl = Paginator.find('a', {'class': 'nextpostslink'}).get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            lastpg = Paginator.find('a', {'class': 'last'})
            if lastpg:
                lastpg = lastpg.get('href').split('/')[-2]
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'singcont'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('a')
            for link in links:
                videourl = link.get('href')
                self.resolve_media(videourl, videos)
        except:
            pass

        try:
            links = re.findall(r'<a\s*target="_blank"\s*href="([^"]+).+?(\d{3,4}p)', html, re.IGNORECASE)
            for link, qual in links:
                self.resolve_media(link, videos, qual)
        except:
            pass

        try:
            links = re.findall(r'<iframe.+?\ssrc="([^"]+)', html, re.IGNORECASE)
            for link in links:
                self.resolve_media(link, videos)
        except:
            pass

        return videos
