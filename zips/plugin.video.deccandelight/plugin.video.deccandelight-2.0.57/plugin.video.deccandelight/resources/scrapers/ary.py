'''
DeccanDelight scraper plugin
Copyright (C) 2019 gujal

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
from six.moves import urllib_parse
from resources.lib import client
from resources.lib.base import Scraper


class ary(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://arydigital.tv/'
        self.icon = self.ipath + 'ary.png'
        self.list = {'01On Air Dramas': 'on-air',
                     '02Current Dramas': 'popularplaylists',
                     '03Finished Dramas': 'archiveplaylists',
                     '04Latest Videos': 'latestvideosMMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        """
        shows = []
        html = client.request(self.bu)
        r = re.search(r'"buildId":"([^"]+)', html)
        if r:
            html = client.request('{0}_next/data/{1}/{2}.json'.format(self.bu, r.group(1), iurl))
            items = json.loads(html).get('pageProps').get('data').get('series')
            for item in items:
                title = self.unescape(item.get('title'))
                title = title.encode('utf8') if self.PY2 else title
                url = item.get('seriesDM')
                thumb = 'https://node.aryzap.com/public/' + urllib_parse.quote(item.get('imagePoster'))
                shows.append((title, thumb, url))
        return (shows, 7)

    def get_items(self, iurl):
        movies = []
        """
        https://api.dailymotion.com/playlist/x7uqr9/videos?fields=title%2Cthumbnail_360_url%2Cid&page=1&limit=50
        params = {'fields': 'title,thumbnail_360_url,id', 'page': 1, 'limit': 50}
        """
        page = '1'
        if '#' in iurl:
            iurl, page = iurl.split('#')
        if iurl == 'latestvideos':
            plurl = 'https://api.dailymotion.com/user/arydigitalofficial/videos'
        else:
            plurl = 'https://api.dailymotion.com/playlist/{0}/videos'.format(iurl)
        params = {'fields': 'title,thumbnail_360_url,id', 'page': page, 'limit': 50}
        html = client.request(plurl, params=params)
        jd = json.loads(html)
        items = jd.get('list')

        for item in items:
            title = item.get('title')
            if '|' in title:
                title = title.split('|')
                if 'digital' in title[-1].lower():
                    _ = title.pop(-1)
                if iurl != 'latestvideos':
                    _ = title.pop(0)
                title = '-'.join(title)
            url = 'https://www.dailymotion.com/video/' + item.get('id')
            thumb = item.get('thumbnail_360_url')
            movies.append((title, thumb, url))

        np = False
        total = jd.get('total')
        if total is None:
            np = jd.get('has_more')
        else:
            np = jd.get('page') * jd.get('limit') < total
        if np:
            purl = '{0}#{1}'.format(iurl, int(page) + 1)
            title = 'Next Page...'
            movies.append((title, self.nicon, purl))

        return (movies, 9)
