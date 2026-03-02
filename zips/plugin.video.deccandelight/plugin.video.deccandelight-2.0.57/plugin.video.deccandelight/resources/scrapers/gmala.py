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


class gmala(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.hindilyrics4u.com'
        self.icon = self.ipath + 'gmala.png'
        self.list = {'02Browse by Movie Titles': self.bu + '/ZZZZTitles',
                     '03Browse Yearwise': self.bu + '/ZZZZYearwise',
                     '04Browse by Singer': self.bu + '/ZZZZSinger',
                     '05[COLOR yellow]** Search by Singer **[/COLOR]': self.bu + '/search.php?type=1&value=MMMM7',
                     '06[COLOR yellow]** Search by Composer **[/COLOR]': self.bu + '/search.php?type=2&value=MMMM7',
                     '07[COLOR yellow]** Search by Movie **[/COLOR]': self.bu + '/search.php?type=3&value=MMMM7',
                     '08[COLOR yellow]** Search by Song **[/COLOR]': self.bu + '/search.php?type=8&value=MMMM7'}

    def get_menu(self):
        return (self.list, 4, self.icon)

    def get_top(self, iurl):
        """
        Get the list of Categories.
        :return: list
        """
        categories = []
        url = iurl.split('ZZZZ')[0]
        category = iurl.split('ZZZZ')[1]
        html = client.request(url)
        mlink = SoupStrainer('td', {'class': re.compile('^h20')})
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        for item in items:
            if category in item.span.text:
                letters = item.find_all('a')
                for letter in letters:
                    title = letter.text
                    url = self.bu + letter.get('href')
                    categories.append((title, self.icon, url))

        return (categories, 5)

    def get_second(self, iurl):
        """
        Get the list of categories.
        :return: list
        """
        categories = []
        html = client.request(iurl)

        mlink = SoupStrainer('table', {'class': re.compile('alcen$')})
        itemclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = itemclass.find_all('td', {'class': 'w25p h150'})
        for item in items:
            title = item.text.strip()
            url = self.bu + item.find('a').get('href')
            icon = item.find('img').get('src') if item.find('img') else self.icon
            categories.append((title, icon, url))

        plink = SoupStrainer('td', {'class': re.compile(r'vatop\s*w140$')})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        if 'next' in str(Paginator):
            ppath = Paginator.find('a').get('href')
            if 'page' in ppath:
                if ppath.startswith('/'):
                    purl = self.bu + ppath
                else:
                    pparts = iurl.split('/')
                    pparts[-1] = ppath
                    purl = '/'.join(pparts)
                pgtxt = re.findall('(Page.*?)"', html)[0]
                if pgtxt.split()[1] != pgtxt.split()[3]:
                    title = 'Next Page.. (Currently in {0})'.format(pgtxt)
                    categories.append((title, self.nicon, purl))
        else:
            plink = SoupStrainer('ul', {'class': 'pagination'})
            Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
            s = re.search(r'<li\s*class="disabled"><a\s*href.+?>&gt', str(Paginator))
            if not s:
                ppath = Paginator.find_all('a')[-1].get('href')
                purl = urllib_parse.urljoin(self.bu, ppath)
                pgtxt = Paginator.find_all('li', {'class': 'active'})[-1].text
                title = 'Next Page.. (Currently in Page {0})'.format(pgtxt)
                categories.append((title, self.nicon, purl))

        return (categories, 7)

    def get_items(self, iurl):
        movies = []
        if iurl[-7:] == '&value=':
            search_text = self.get_SearchQuery('Hindi Geetmala')
            search_text = urllib_parse.quote_plus(search_text)
            iurl = iurl + search_text
        nextpg = True
        while len(movies) < 50 and nextpg:
            html = client.request(iurl)
            mlink = SoupStrainer('table', {'class': 'w760', 'itemtype': None})
            mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
            items = mdiv.find_all('table', {'class': re.compile('allef$')})
            for item in items:
                albumdiv = item.find('span', {'itemprop': 'inAlbum'})
                title = '[COLOR cyan]{0}:[/COLOR] '.format(albumdiv.find('span').text) if albumdiv else ''
                title += item.find('span', {'itemprop': 'name'}).text
                itemdiv = item.find('td', {'class': 'w105 vatop'})
                url = self.bu + itemdiv.find('a').get('href')
                icon = self.bu + itemdiv.find('img').get('src')
                movies.append((title, icon, url))

            plink = SoupStrainer('ul', {'class': 'pagination'})
            Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
            s = re.search(r'<li\s*class="disabled"><a\s*href.+?>&gt', str(Paginator))
            if not s:
                ppath = Paginator.find_all('a')[-1].get('href')
                if 'page' in ppath:
                    iurl = urllib_parse.urljoin(self.bu, ppath)
                else:
                    nextpg = False
            else:
                nextpg = False

        if nextpg:
            pgtxt = Paginator.find_all('li', {'class': 'active'})[-1].text
            title = 'Next Page.. (Currently in Page {0})'.format(pgtxt)
            movies.append((title, self.nicon, iurl))

        return (movies, 9)

    def get_video(self, url):
        html = client.request(url)
        mlink = SoupStrainer('table', {'class': 'b1 w760 alcen'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        if videoclass.find('iframe'):
            vidurl = videoclass.find('iframe').get('src')
        elif videoclass.find('a'):
            vidurl = videoclass.find('a').get('href')
        else:
            vidurl = ''

        return vidurl
