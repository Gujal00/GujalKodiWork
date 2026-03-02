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


class skytamil(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.skytamil.net/'
        self.icon = self.ipath + 'skytamil.png'

    def get_url(self, url, headers=None):
        if headers is None:
            headers = self.hdr
        cpath = urllib_parse.urlparse(url).netloc + '.txt'
        cookie = self.retrieve(cpath)
        resp = client.request(url, headers=headers, cookie=cookie, error=True, output='extended')
        if int(resp[1]) == 403 and resp[2].get('Server') == 'ddos-guard':
            host = urllib_parse.urljoin(url, '/')
            ddg = client.request('https://check.ddos-guard.net/check.js', referer=host)
            src = re.findall(r"new Image\(\).src = '(.+?)';", ddg.decode('utf-8'))[0]
            ddg2 = client.request(host[:-1] + src, referer=host, output='cookie')
            cookie = resp[4] + '; ' + ddg2
            resp = client.request(url, headers=headers, cookie=cookie, output='extended')
            cookie += '; ' + resp[4]
            self.store(cookie, cpath)
        return resp[0]

    def get_menu(self):
        html = self.get_url(self.bu)
        items = {
            '01Bigg Boss Tamil 6': self.bu + 'category/bigg-boss-tamil-season-6/',
            '02Bigg Boss Telugu 6': self.bu + 'category/bigg-boss-telugu-6/'
        }
        cats = re.findall('id="menu-item-(?!755|758|757).+?href="([^"]+)">([^<]+)', html, re.DOTALL)
        sno = 3
        for caturl, cat in cats:
            items['{0:02d}{1}'.format(sno, cat)] = caturl
            sno += 1
        items['99[COLOR yellow]** Search **[/COLOR]'] = self.bu + '?s='
        return (items, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Sky Tamil')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        headers = self.hdr
        headers.update({'Referer': self.bu})
        html = self.get_url(url, headers=headers)
        mlink = SoupStrainer("main")
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        Paginator = mdiv.find("div", {"class": "post-pagination"})
        items = mdiv.find_all('article')

        for item in items:
            title = self.unescape(item.find('h4').text)
            title = self.clean_title(title)
            url = item.a.get('href')
            try:
                thumb = item.img.get('src')
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextpg = Paginator.find('a', {'class': 'next'})
            purl = nextpg.get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            pages = Paginator.find_all('a', {'class': 'page-numbers'})
            lastpg = pages[-2].text
            title = 'Next Page.. (Currently in Page %s of %s)' % (currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        headers = self.hdr
        headers.update({'Referer': self.bu})
        html = self.get_url(url, headers=headers)
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
