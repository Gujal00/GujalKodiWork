"""
DeccanDelight scraper plugin
Copyright (C) 2018 gujal

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

import json
import random
import re
import time

from bs4 import BeautifulSoup, SoupStrainer
from kodi_six import xbmc
from resources.lib import cache, client, control
from resources.lib.base import Scraper
from six.moves import urllib_parse


class einthusan(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://einthusan.tv/'
        self.icon = self.ipath + 'einthusan.png'
        self.list = {'01Tamil': self.bu + 'launcher/?lang=tamil',
                     '02Telugu': self.bu + 'launcher/?lang=telugu',
                     '03Malayalam': self.bu + 'launcher/?lang=malayalam',
                     '04Kannada': self.bu + 'launcher/?lang=kannada',
                     '05Hindi': self.bu + 'launcher/?lang=hindi',
                     '06Bengali': self.bu + 'launcher/?lang=bengali',
                     '07Marathi': self.bu + 'launcher/?lang=marathi',
                     '08Punjabi': self.bu + 'launcher/?lang=punjabi'}
        self.list2 = {'Recent': 'Recently Added',
                      'StaffPick': 'Staff Picks',
                      'Popularity': 'Most Watched'}
        self.hdr.update({'Referer': self.bu, 'Origin': self.bu[:-1]})

    def decrypt(self, e):
        t = 10
        i = e[0:t] + e[-1] + e[t + 2:-1]
        i = self.b64decode(i)
        return json.loads(i)

    def encrypt(self, t):
        e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        n = 10
        a = json.dumps(t)
        a = self.b64encode(a)
        a = a[0:n] + random.choice(e) + random.choice(e) + a[n + 1:] + a[n]
        return a

    def get_sort_cdn(self, slist):
        ejo = []
        for server in slist:
            params = {'_': int(time.time() * 1000)}
            response = client.request(server, params=params, output='elapsed')
            ejo.append((response, server))
        ejo = self.encrypt([x for _, x in sorted(ejo)])
        return ejo

    def get_menu(self):
        return (self.list, 4, self.icon)

    def get_top(self, iurl):
        """
        Get the list of categories.
        """
        cats = []
        html = client.request(iurl)
        mlink = SoupStrainer('section', {'id': 'UILaunchPad'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('li')
        lang = iurl.split('=')[1]
        thumb = 'http://s3.amazonaws.com/einthusanthunderbolt/etc/img/{}.jpg'.format(lang)
        for item in items:
            if 'input' not in str(item) and 'data-disabled' not in str(item):
                title = item.p.text
                if title not in ['Feed', 'Contact', 'Go Premium']:
                    url = self.bu[:-1] + item.find('a')['href']
                    cats.append((title, thumb, url))
        for i in self.list2.keys():
            title = self.list2[i]
            url = '{0}movie/results/?lang={1}&find={2}MMMM7'.format(self.bu, lang, i)
            if i == 'Popularity':
                url = url.replace('MMMM7', '&ptype=View&tp=l30dMMMM7')
            cats.append((title, thumb, url))

        surl = '{0}movie/results/?lang={1}&query=MMMM7'.format(self.bu, lang)
        cats.append(('[COLOR yellow]** Search Movies **[/COLOR]', thumb, surl))
        return cats, 5

    def get_second(self, iurl):
        """
        Get the list of types.
        """
        thumb = 'http://s3.amazonaws.com/einthusanthunderbolt/etc/img/{}.jpg'.format(iurl.split('=')[1])
        cats = [('Alphabets', thumb, iurl + 'XXXXAlphabets|Numbers'),
                ('Years', thumb, iurl + 'XXXXYear')]
        return cats, 6

    def get_third(self, iurl):
        """
        Get the list of types.
        """
        cats = []
        iurl, sterm = iurl.split('XXXX')
        html = client.request(iurl)
        if sterm == 'Year':
            spat = 'href="([^"]+(?:{})[^"]+)">([^<]+)'.format(sterm)
        else:
            spat = r'href="([^"]+(?:{})[^"]+)"\s*data-disabled="">([^<]+)'.format(sterm)
        items = re.findall(spat, html)
        thumb = 'http://s3.amazonaws.com/einthusanthunderbolt/etc/img/{}.jpg'.format(iurl.split('=')[1])
        for url, title in items:
            url = self.bu[:-1] + url.replace('&amp;', '&')
            if '/playlist/' in url:
                title += '  [COLOR cyan][I]Playlists[/I][/COLOR]'
            cats.append((title, thumb, url))

        return cats, 7

    def get_items(self, iurl):
        clips = []
        if iurl.endswith('='):
            search_text = self.get_SearchQuery('Einthusan')
            search_text = urllib_parse.quote_plus(search_text)
            iurl += search_text
        nextpg = True
        nmode = 9
        while nextpg and len(clips) < 18:
            html = client.request(iurl)
            if '/movie-clip/' in iurl:
                items = re.findall(r'data-disabled="false"\s*href="([^"]+)">\s*<img\s*src="([^"]+).+?>([^<]+)</h3.+?info">(.+?)</div', html)
            else:
                items = re.findall(r'data-disabled="false"\s*href="([^"]+)"><img\s*src="([^"]+).+?h3>([^<]+).+?info">(.+?)</div', html)
            for url, thumb, title, info in items:
                title = self.unescape(title)
                title = title.encode('utf8') if self.PY2 else title
                r = re.search(r'<p>(\d{4})', info)
                if r:
                    title += ' ({0})'.format(r.group(1))
                if 'Subtitle' in info:
                    title += '  [COLOR cyan][I]with subtitles[/I][/COLOR]'
                elif '/movie-clip/' in iurl and '/playlist/' not in url:
                    mtitle = self.unescape(re.findall('title="([^"]+)', info)[0])
                    mtitle = mtitle.encode('utf8') if self.PY2 else mtitle
                    title = '[COLOR cyan]{}[/COLOR] - [COLOR yellow]{}[/COLOR]'.format(mtitle, title)
                url = self.bu[:-1] + url
                if not thumb.startswith('http'):
                    thumb = 'http:' + thumb
                clips.append((title, thumb, url))
            if len(clips) > 0 and '/playlist/' in url:
                nmode = 7

            paginator = re.search(r'>(Page[^<]+).+?data-disabled=""\s*href="([^"]+)"><i>&#xe956;</i><p>Next<', html, re.DOTALL)
            if paginator:
                iurl = self.bu[:-1] + paginator.group(2).replace('&amp;', '&')
            else:
                nextpg = False

            xbmc.sleep(3000)

        if nextpg:
            title = 'Next Page.. (Currently in {})'.format(paginator.group(1))
            clips.append((title, self.nicon, iurl))

        return clips, nmode

    def get_video(self, iurl):
        headers = self.hdr
        stream_url = ''
        r = client.request(iurl, headers=headers, output='extended')
        token = self.unescape(re.findall('data-pageid="([^"]+)', r[0])[0])
        ej = re.search('data-ejpingables="([^"]+)', r[0])
        if ej:
            ej = self.decrypt(ej.group(1))
            xj = {"EJOutcomes": cache.get(self.get_sort_cdn, 168, ej),
                  "NativeHLS": False}
            pdata = {'xEvent': 'UIVideoPlayer.PingOutcome',
                     'xJson': json.dumps(xj).replace(' ', ''),
                     'gorilla.csrf.Token': token}
            headers.update({'X-Requested-With': 'XMLHttpRequest'})
            aurl = iurl.replace('/movie', '/ajax/movie')
            r2 = client.request(aurl, post=pdata, headers=headers, cookie=r[4])
            stream_url = self.decrypt(json.loads(r2)['Data']['EJLinks'])['MP4Link']
        else:
            control.notify('Einthusan Servers Full. Try after sometime')

        return stream_url
