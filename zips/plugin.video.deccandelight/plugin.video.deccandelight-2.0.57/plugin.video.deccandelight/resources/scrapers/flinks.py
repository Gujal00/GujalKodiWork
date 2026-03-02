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


class flinks(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://filmlinks4u.cloud/genre/'
        self.icon = self.ipath + 'flinks.png'
        self.list = {'01Tamil Movies': self.bu + 'tamil/',
                     '02Telugu Movies': self.bu + 'telugu/',
                     '03Malayalam Movies': self.bu + 'malayalam/',
                     '04Kannada Movies': self.bu + 'kannada/',
                     '05Hindi': self.bu + 'bollywood/',
                     '06Hindi Web Series': self.bu + 'web-series/',
                     '11English': self.bu + 'hollywood/',
                     '12English Series': self.bu[:-6] + 'series/MMMM5',
                     '21Dual Audio': self.bu + 'dual-audio/',
                     '31Bengali Movies': self.bu + 'bengali/',
                     # '32Bhojpuri Movies': self.bu + 'bhojpuri/',
                     '33Gujarati Movies': self.bu + 'gujarati/',
                     '34Marathi Movies': self.bu + 'marathi/',
                     '36Punjabi Movies': self.bu + 'punjabi/',
                     '38Urdu Movies': self.bu + 'pakistani/',
                     '96[COLOR cyan]Adult Erotic Movies[/COLOR]': self.bu + 'erotic-movies/',
                     '97[COLOR cyan]Adult Hot[/COLOR]': self.bu + 'tv-shows/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-6] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'movies-list movies-list-full'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'id': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': re.compile('^ml-item')})

        for item in items:
            title = self.unescape(item.find('a')['oldtitle'])
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['data-original']
            except:
                thumb = self.icon
            movdet = item.find('div', {'id': 'hidden_tip'})
            if 'Adult' not in movdet.text and 'Erotic' not in movdet.text:
                shows.append((title, thumb, url))
            elif self.adult:
                shows.append((title, thumb, url))

        r = re.search('class="active".+?href="([^"]+)', str(Paginator))
        if r:
            currpg = Paginator.find('li', {'class': 'active'}).text
            lastpg = Paginator.find_all('li')[-1].find('a')['href'].split('/')[-2]
            title = 'Next Page.. (Currently in Page {} of {})'.format(currpg, lastpg)
            shows.append((title, self.nicon, r.group(1)))

        return (shows, 6)

    def get_third(self, iurl):
        """
        Get the list of episodes.
        :return: list
        """
        episodes = []
        html = client.request(iurl)
        mlink = SoupStrainer('div', {'id': 'mv-info'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        thumb = mdiv.find('div', {'class': 'thumb'})['style'].split("'")[1]
        idiv = mdiv.find('div', {'class': 'les-content'})
        items = idiv.find_all('a')
        for item in items:
            url = item.get('href')
            title = item.text
            episodes.append((title, thumb, url))

        return (episodes, 8)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Hindi Links 4U')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'movies-list movies-list-full'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'id': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': re.compile('^ml-item')})

        for item in items:
            title = self.unescape(item.find('a')['oldtitle'])
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['data-original']
            except:
                thumb = self.icon
            movdet = item.find('div', {'id': 'hidden_tip'})
            if 'Adult' not in movdet.text and 'Erotic' not in movdet.text:
                movies.append((title, thumb, url))
            elif self.adult:
                movies.append((title, thumb, url))

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
                if 'speedostream' in videourl:
                    videourl = '{0}|Referer={1}'.format(videourl, self.bu[:-6])
                self.resolve_media(videourl, videos)
        except:
            pass

        try:
            vtabs = videoclass1.find_all('div', {'class': re.compile('movieplay')})
            for vtab in vtabs:
                if vtab.find('iframe') is not None:
                    videourl = vtab.find('iframe')['src']
                    if 'speedostream' in videourl:
                        videourl = '{0}|Referer={1}'.format(videourl, self.bu[:-6])
                    self.resolve_media(videourl, videos)
        except:
            pass

        return videos
