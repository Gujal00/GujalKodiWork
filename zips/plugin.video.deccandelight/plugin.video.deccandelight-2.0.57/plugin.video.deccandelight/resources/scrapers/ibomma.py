'''
DeccanDelight scraper plugin
Copyright (C) 2022 gujal

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
from six.moves import urllib_parse


class ibomma(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://axn.bappam.eu/'
        self.icon = self.ipath + 'ibomma.png'
        self.list = {
            '01Telugu Movies': self.bu + 'telugu-movies/',
            '99[COLOR yellow]** Search **[/COLOR]': 'https://n_2v-fx.x-search.link/?label=telugu&q='
        }

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []

        if url[-3:] == '&q=':
            search_text = self.get_SearchQuery('iBomma')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url, referer=self.bu)
        mlink = SoupStrainer('article', {'itemscope': None})
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        if len(items) > 1:
            for item in items:
                title = self.unescape(item.h3.a.text)
                title = title.encode('utf8') if self.PY2 else title
                title += ' [COLOR yellow]({0})[/COLOR]'.format(item.h3.span.text)
                thumb = item.img.get('data-src')
                url = item.find('a').get('href')
                movies.append((title, thumb, url))
        else:
            items = re.findall(r'(?:data={},\s*)?data=\s*(.+?)</script>', html)[0]
            items = json.loads(items)
            items = items.get('hits', {}).get('hits', [])
            for item in items:
                item = item.get('_source')
                desc = item.get('description')
                title = item.get('title').split('Telugu')[0].strip()
                title = title.encode('utf8') if self.PY2 else title
                r = re.search(r'\d{4}', desc)
                if r:
                    title += ' [COLOR yellow][{0}][/COLOR]'.format(r.group(0))
                thumb = item.get('image_link')
                url = item.get('location')
                movies.append((title, thumb, url))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        html = client.request(url, referer=self.bu)

        try:
            mlink = SoupStrainer('button', {'class': 'server-button'})
            items = BeautifulSoup(html, "html.parser", parse_only=mlink)
            urls = re.search(r'const\s*\w\s*=\s*(\[[^]]+])', html)
            if urls:
                import ast
                urls = ast.literal_eval(urls.group(1))
                for item in items:
                    linkcode = int(item.get('data-index'))
                    vurl = urls[linkcode]
                    vidhost = '{0} [COLOR yellow]{1}[/COLOR]'.format(self.get_vidhost(vurl), item.text)
                    videos.append((vidhost, vurl))
        except:
            import traceback
            traceback.print_exc()
            pass

        return videos

    def get_video(self, url):
        ehtml = client.request(url, referer=self.bu)
        s = re.search(r'file:"([^"]+)', ehtml)
        if s:
            s = s.group(1)
            ref = urllib_parse.urljoin(url, '/')
            headers = {
                'Referer': ref,
                'Orogin': ref[:-1],
                'User-Agent': self.hdr.get('User-Agent')
            }
            return s + '|{0}'.format(urllib_parse.urlencode(headers))
