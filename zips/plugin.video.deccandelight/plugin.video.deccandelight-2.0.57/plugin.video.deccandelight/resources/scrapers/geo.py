'''
DeccanDelight scraper plugin
Copyright (C) 2017 gujal

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
import json
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper


class geo(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://harpalgeo.tv/'
        self.icon = self.ipath + 'geo.png'
        self.list = {'01Dramas': self.bu + 'programs/'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        """
        shows = []

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'row'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'cat_inr_placement'})
        for item in items:
            title = self.unescape(item.h4.text)
            title = title.encode('utf8') if self.PY2 else title
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['data-src']
            except:
                thumb = self.icon
            shows.append((title, thumb, url))

        if 'next' in str(Paginator):
            purl = Paginator.find('a', {'rel': 'next'}).get('href')
            currpg = Paginator.find('strong').text
            lastpg = Paginator.find_all('a')[-1].get('data-ci-pagination-page')
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            shows.append((title, self.nicon, purl))
        return (shows, 7)

    def get_items(self, url):
        movies = []

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': 'programVideos'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        nurl = self.bu + 'program/more_videos/{}'
        nextpg = True
        page = 1
        catid = re.search(r'id="category_id"\s*value="([^"]+)', html)
        if catid:
            data = {'category_id': catid.group(1)}
            headers = self.hdr
            headers.update({'Referer': self.bu,
                            'X-Requested-With': 'XMLHttpRequest'})
            while nextpg and page < 3:
                items = mdiv.find_all('div', {'class': re.compile('^col-lg-2')})
                for item in items:
                    title = self.unescape(item.find_all('p')[-1].text)
                    title = title.encode('utf8') if self.PY2 else title
                    if 'teaser' not in title.lower() and 'promo' not in title.lower():
                        title = title.split('|')[0]
                        title = title.replace('Har Pal Geo', '').replace('Dramas', '')
                        url = item.find('a')['href']
                        try:
                            thumb = item.find('img').get('data-src') or item.find('img').get('src')
                        except:
                            thumb = self.icon
                        movies.append((title, thumb, url))
                page += 1
                html = client.request(nurl.format(page), headers=headers, post=data)
                if len(html) > 0:
                    mdiv = BeautifulSoup(html, "html.parser")
                else:
                    nextpg = False
        return (movies, 9)

    def get_video(self, url):
        html = client.request(url)
        r = re.search(r"hls:\s*'([^']+)", html)
        if r:
            return r.group(1)
        r = re.search(r"mp4:\s*'([^']+)", html)
        if r:
            return r.group(1)
        r = re.search(r'"contentUrl":\s*"([^"]+)', html)
        if r:
            if r.group(1).startswith('http'):
                return r.group(1)

        vlink = SoupStrainer('video-js')
        vdiv = BeautifulSoup(html, "html.parser", parse_only=vlink)
        acct = vdiv.find('video-js').get('data-account')
        player = vdiv.find('video-js').get('data-player')
        vid = vdiv.find('video-js').get('data-video-id')
        jsurl = "https://players.brightcove.net/{0}/{1}_default/index.min.js"
        apiurl = "https://edge.api.brightcove.com/playback/v1/accounts/{0}/videos/{1}"
        headers = self.hdr
        headers.update({'Referer': self.bu, 'Origin': self.bu[:-1]})
        js = client.request(jsurl.format(acct, player), headers=headers)
        pk = re.findall('policyKey:"([^"]+)', js)[0]
        headers.update({'Accept': 'application/json;pk={0}'.format(pk)})
        sources = json.loads(client.request(apiurl.format(acct, vid), headers=headers)).get('sources')
        for source in sources:
            if source['type'] == "application/x-mpegURL":
                return source['src']
