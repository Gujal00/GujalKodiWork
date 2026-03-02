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


class gomovies(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://ogomovies.mobi/genre/'
        self.icon = self.ipath + 'gomovies.png'

        self.list = {'01Tamil Movies': self.bu + 'watch-tamil-movies/',
                     '02Telugu Movies': self.bu + 'telugu/',
                     '03Malayalam Movies': self.bu + 'gomovies-malayalam/',
                     '04Kannada Movies': self.bu + 'kannada/',
                     '05Hindi': self.bu + 'watch-hindi-movies/',
                     '06Punjabi Movies': self.bu + 'punjabi/',
                     '07Multi Audio Movies': self.bu + 'multi-language/',
                     '08Hollywood': self.bu + 'hollywood/',
                     '09Hindi Dubbed': self.bu + 'hindi-dubbed/',
                     '10Tamil Dubbed': self.bu + 'tamil-dubbed/',
                     '11South Dubbed': self.bu + 'south-dubbed/',
                     '50Web Series': self.bu + 'hindi-web-series/',
                     '87[COLOR cyan]Adult 18+[/COLOR]': self.bu + 'erotic-movies/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-6] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Go Movies')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url, verify=False)
        mlink = SoupStrainer('div', {'class': 'movies-list movies-list-full'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'id': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': re.compile('^ml-item')})

        for item in items:
            title = self.unescape(item.find('a')['oldtitle'])
            title = title.encode('utf-8') if self.PY2 else title
            qual = item.find('span', {'class': 'mli-quality'})
            if qual:
                title += ' [COLOR cyan]{0}[/COLOR]'.format(qual.text)

            iurl = item.find('a')['href']
            try:
                thumb = item.find('img')['data-original']
            except:
                thumb = self.icon
            if self.bu[:-6] in thumb:
                thumb += '|verifypeer=false'

            mode = 6 if 'hindi-web-series' in url else 8
            movies.append((title, thumb, iurl))

        r = re.search('class="active".+?href="([^"]+)', str(Paginator))

        if r:
            currpg = Paginator.find('span', {'class': 'active'}).text
            lastpg = Paginator.find_all('li')[-1].find('a')['href'].split('/')[-2]
            title = 'Next Page.. (Currently in Page {} of {})'.format(currpg, lastpg)
            movies.append((title, self.nicon, r.group(1)))

        return (movies, mode)

    def get_third(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        iurl = iurl + 'watching/'
        shows = []
        edata = {}
        html = client.request(iurl, verify=False)
        mlink = SoupStrainer('ul', {'class': 'dropdown-menu'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        vtabs = videoclass.find_all('li')
        for vtab in vtabs:
            eurl = vtab.get('data-drive') or vtab.get('data-openload')
            if eurl:
                html1 = client.request(eurl, verify=False)
                mlink1 = SoupStrainer('div', {'class': 'content-pt'})
                videoclass1 = BeautifulSoup(html1, "html.parser", parse_only=mlink1)
                vtabs1 = videoclass1.find_all('a')
                for vtab1 in vtabs1:
                    videourl = vtab1.get('href')
                    videourl = videourl.split('?link=')[-1]
                    title = re.sub(r'PLAYER\s*\d', '', vtab1.text).strip()
                    if title in edata.keys():
                        edata[title].append(videourl)
                    else:
                        edata.update({title: [videourl]})

        for key in edata.keys():
            shows.append((key, self.icon, 'ZZZZ'.join(edata[key])))

        return (shows, 8)

    def get_videos(self, url):
        videos = []
        if 'ZZZZ' in url:
            for eurl in url.split('ZZZZ'):
                self.resolve_media(eurl, videos)
        else:
            url = url + 'watching/'
            html = client.request(url, verify=False)
            mlink = SoupStrainer('ul', {'class': 'dropdown-menu'})
            videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
            links = videoclass.find_all('li')
            for link in links:
                iurl = link.get('data-drive') or link.get('data-openload') or link.get('data-streamgo') or link.get('data-putload')
                if '/hls/' in iurl:
                    videos.append(('CDN Direct', iurl + '|User-Agent=iPad'))
                elif 'download' not in link.text.lower():
                    self.resolve_media(iurl, videos)
        return videos
