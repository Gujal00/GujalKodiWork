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


class tyogi(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://1tamilyogi.horse/'
        self.icon = self.ipath + 'tyogi.png'

    def get_menu(self):
        html = client.request(self.bu)
        items = {}
        cats = re.findall(r'''<li\s*class="menu-item[^>]+><a\s*href="([^"]+)">(?!Home)([^<]+)''', html)
        sno = 1
        for cat, title in cats:
            items['%02d' % sno + title] = cat
            sno += 1
        items['%02d' % sno + '[COLOR yellow]** Search **[/COLOR]'] = self.bu + '?s='
        return (items, 7, self.icon)

    def get_items(self, iurl):
        movies = []
        search = False
        if iurl[-3:] == '?s=':
            search = True
            search_text = self.get_SearchQuery('Tamil Yogi')
            search_text = urllib_parse.quote_plus(search_text)
            iurl += search_text

        nmode = 9
        html = client.request(iurl)

        if search:
            mlink = SoupStrainer('div', {'id': 'content'})
            mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
            items = mdiv.find_all('li', {'class': 'post'})
        else:
            mlink = SoupStrainer('div', {'class': 'grid-items'})
            mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
            items = mdiv.find_all('div', {'class': 'item'})

        plink = SoupStrainer('div', {'class': 'paginate'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        for item in items:
            if search:
                title = item.find('h2').text.strip()
                url = item.find('h2').a.get('href')
            else:
                title = item.find('div', {'class': re.compile('title$')}).text.strip()
                url = item.find('a')['href']
            if ')' in title and '-series' not in iurl:
                title = title.split(')')[0] + ')'
            try:
                img = item.find('img')
                thumb = img.get('data-src') or img.get('src')
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'Next' in str(Paginator):
            purl = Paginator.find('a', {'class': re.compile('next')}).get('href')
            currpg = Paginator.find('span', {'class': re.compile('current$')}).text
            lastpg = Paginator.find_all("a", {'class': 'page-numbers'})[-2].text
            pgtxt = '{0} of {1}'.format(currpg, lastpg)
            title = 'Next Page... (Currently in Page {0})'.format(pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, nmode)

    def get_videos(self, url):
        videos = []

        html = client.request(url, headers=self.hdr)
        mlink = SoupStrainer('div', {'class': 'entry-content'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        links = videoclass.find_all('p')

        try:
            for link in links:
                vidurl = link.find('a').get('href')
                if 'tamilvip.' in vidurl:
                    vidurl = 'https://vidplay.one/xembed-' + vidurl.split('?')[-1]
                vidtxt = self.unescape(link.text)
                self.resolve_media(vidurl, videos, vidtxt=vidtxt)
        except:
            pass

        try:
            for link in links:
                vidurl = link.find('iframe').get('src')
                title = self.unescape(videoclass.find('h1').text)
                if ')' in title:
                    title = title.split(')')[0] + ')'
                self.resolve_media(vidurl, videos, vidtxt=title)
        except:
            pass

        return videos

    def get_video(self, url):
        html = client.request(url, referer=self.bu)
        mlink = SoupStrainer('div', {'class': 'entry-content'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        eurl = mdiv.find('iframe').get('src')
        if self.hmf(eurl):
            return eurl

        self.log('{0} not resolvable {1}.\n'.format(url, eurl), 'info')
        return
