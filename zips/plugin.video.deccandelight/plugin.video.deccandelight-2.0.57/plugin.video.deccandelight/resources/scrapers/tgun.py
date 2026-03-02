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
import json
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import control, client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class tgun(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://tamilgun.group'
        self.icon = self.ipath + 'tgun.png'

    def get_menu(self):
        html = client.request(self.bu)
        items = {}
        cats = re.findall(r'<li\s*id="menu[^>].+?href="([^"]+?category[^"]+)">([^<]+)', html)
        sno = 1
        for url, title in cats:
            title = self.unescape(title)
            title = title.encode('utf8') if self.PY2 else title
            items['{:02d}'.format(sno) + title] = url
            sno += 1
        items['{:02d}'.format(sno) + 'Special TV Shows'] = self.bu + '/video-category/special-tv-shows/'
        items['99[COLOR yellow]** Search **[/COLOR]'] = self.bu + '/?s='
        return (items, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Tamil Gun')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        mlink = SoupStrainer('article', {'class': re.compile('video')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)

        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        for item in mdiv:
            title = self.unescape(item.h3.text).strip()
            title = title.encode('utf8') if self.PY2 else title
            title = title.replace(' HDTV', '').replace(' HD', '')
            iurl = item.h3.find('a')['href']
            if 'all episodes' in title.lower():
                iurl = iurl + 'MMMM7'
            try:
                thumb = item.find('img').get('src').strip()
                cpath = urllib_parse.urlparse(thumb).netloc
                if control.pathExists(control.TRANSLATEPATH(control._ppath) + cpath + '.json'):
                    cfhdrs = json.loads(client.retrieve(cpath + '.json'))
                    thumb += '|{0}'.format(urllib_parse.urlencode(cfhdrs))
            except:
                thumb = self.icon

            movies.append((title, thumb, iurl))

        if 'rel="next"' in str(Paginator):
            nextli = Paginator.find('a', {'class': 'nextpostslink'})
            purl = nextli.get('href')
            pgtxt = Paginator.find('span', {'class': 'pages'}).text
            title = 'Next Page... (Currently in %s)' % (pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        if 'cinebix.com' in url:
            self.resolve_media(url, videos)
            return videos

        elif 'tamildbox.' in url or 'tamilhdbox' in url:
            self.resolve_media(url, videos)
            return videos

        html = client.request(url)

        r = re.findall(r"unescape\('([^']+)", html)
        if r:
            for item in r:
                linkcode = urllib_parse.unquote(item)
                source = re.findall('<iframe.+?src="([^"]+)', linkcode, re.IGNORECASE)
                if source:
                    self.resolve_media(source[0], videos)

        mlink = SoupStrainer('div', {'id': 'videoframe'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                iurl = link.get('src')
                if iurl.startswith('//'):
                    iurl = 'https:' + iurl
                if 'playallu.' in iurl:
                    vidhost, strlink = self.playallu(iurl, self.bu)
                    if vidhost is not None:
                        videos.append((vidhost, strlink))
                else:
                    self.resolve_media(iurl, videos)
        except:
            pass

        try:
            links = videoclass.find_all('a')
            for link in links:
                if 'href' in str(link):
                    iurl = link.get('href')
                else:
                    iurl = link.get('onclick').split("'")[1]
                if iurl.startswith('//'):
                    iurl = 'https:' + url
                self.resolve_media(iurl, videos)
        except:
            pass

        mlink = SoupStrainer('div', {'class': 'post-entry'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                iurl = link.get('src').replace('&amp;', '&')
                if iurl.startswith('//'):
                    iurl = 'https:' + iurl
                if 'playallu.' in iurl:
                    vidhost, strlink = self.playallu(iurl, self.bu)
                    if vidhost is not None:
                        videos.append((vidhost, strlink))
                else:
                    iurl += '|Referer={}'.format(urllib_parse.urljoin(url, '/'))
                    self.resolve_media(iurl, videos)
        except:
            pass

        mlink = SoupStrainer('div', {'class': 'entry-excerpt'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            pdivs = videoclass.find_all('p')
            for pdiv in pdivs:
                links = pdiv.find_all('a')
                for link in links:
                    if 'href' in str(link):
                        iurl = link.get('href')
                    else:
                        iurl = link.get('onclick').split("'")[1]
                    if iurl.startswith('//'):
                        iurl = 'https:' + iurl
                    self.resolve_media(iurl, videos)
        except:
            pass

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                iurl = link.get('src')
                if 'latest.htm' not in iurl:
                    self.resolve_media(iurl, videos)
        except:
            pass

        mlink = SoupStrainer('article')
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                iurl = link.get('src')
                if 'playallu.' in iurl:
                    vidhost, strlink = self.playallu(iurl, self.bu)
                    if vidhost is not None:
                        videos.append((vidhost, strlink))
                elif 'bit.ly' not in iurl:
                    self.resolve_media(iurl, videos)
        except:
            pass

        r = re.findall('vdf-data-json">(.*?)<', html)
        if r:
            sources = json.loads(r[0])
            iurl = 'https://www.youtube.com/watch?v={}'.format(sources['videos'][0]['youtubeID'])
            self.resolve_media(iurl, videos)

        r = re.search(r'beeteam368_pro_player\((.*?)\);\s', html)
        if r:
            iurl = re.findall('<iframe.+?src="([^"]+)', r.group(1).replace('\\', ''))[0]
            if iurl:
                if 'playallu.' in iurl:
                    vidhost, strlink = self.playallu(iurl, self.bu)
                    if vidhost is not None:
                        videos.append((vidhost, strlink))
                elif 'player3.' in iurl:
                    ihtml = client.request(iurl, referer=self.bu + '/')
                    s = re.search(r'urlStream":"([^"]+)', ihtml)
                    if s:
                        ref = urllib_parse.urljoin(iurl, '/')
                        headers = {'User-Agent': self.hdr, 'Referer': ref, 'Origin': ref[:-1]}
                        strlink = s.group(1) + '|{}'.format(urllib_parse.urlencode(headers))
                        videos.append(('player3', strlink))
                else:
                    self.resolve_media(iurl + '$$' + self.bu, videos)

        return videos
