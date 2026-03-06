'''
movierulz deccandelight plugin
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
import ssl
from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client, control
from resources.lib.base import Scraper
from six.moves import urllib_parse

# Try to disable SSL warnings (not critical if fails)
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass


class mrulz(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        # Read domain from settings, with fallback to default
        domain = self.settings('mrulz_domain') or 'https://www.5movierulz.claims'
        self.bu = domain + '/category/'
        self.icon = self.ipath + 'mrulz.png'
        self.list = {'01Tamil Movies': self.bu + 'tamil-movie/',
                     '02Telugu Movies': self.bu + 'telugu-movie/',
                     '03Malayalam Movies': self.bu + 'malayalam-movie/',
                     '04Kannada Movies': self.bu + 'kannada-movie/',
                     '11Hindi Movies': self.bu[:-9] + 'bollywood-movie-free/',
                     '21English Movies': self.bu + 'hollywood-movie-2023/',
                     '31Tamil Dubbed Movies': self.bu + 'tamil-dubbed-movie-2/',
                     '32Telugu Dubbed Movies': self.bu + 'telugu-dubbed-movie-2/',
                     '33Hindi Dubbed Movies': self.bu + 'hindi-dubbed-movie/',
                     '34Bengali Movies': self.bu + 'bengali-movie/',
                     '35Punjabi Movies': self.bu + 'punjabi-movie/',
                     '41[COLOR cyan]Adult Movies[/COLOR]': self.bu + 'adult-movie/',
                     '42[COLOR cyan]Adult 18+[/COLOR]': self.bu + 'adult-18/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def _fetch_html_with_retry(self, url):
        """
        Fetch HTML with retries and enhanced headers for SSL/WAF bypass
        Works on both desktop and Android Kodi
        """
        control.log('[MRULZ] Fetching: ' + url, 'info')
        
        # Enhanced user agents to match real browsers
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Brave/1.73',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
        
        headers = self.hdr.copy() if self.hdr else {}
        
        # Set best user agent and browser headers
        headers['User-Agent'] = user_agents[0]
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        headers['Accept-Language'] = 'en-US,en;q=0.5'
        headers['Accept-Encoding'] = 'gzip, deflate'
        headers['DNT'] = '1'
        headers['Connection'] = 'keep-alive'
        headers['Upgrade-Insecure-Requests'] = '1'
        
        # Try with SSL verification disabled (works with Kodi's client module)
        try:
            control.log('[MRULZ] Trying with verify=False', 'info')
            html = client.request(url, headers=headers, verify=False)
            if html and len(html) > 100:
                control.log('[MRULZ] Got HTML: %d bytes' % len(html), 'info')
                return html
        except Exception as e:
            control.log('[MRULZ] verify=False failed: ' + str(e), 'warning')
            pass
        
        try:
            # Try with verifypeer header (alternative for Kodi)
            control.log('[MRULZ] Trying with verifypeer header', 'info')
            headers['verifypeer'] = 'false'
            html = client.request(url, headers=headers)
            if html and len(html) > 100:
                control.log('[MRULZ] Got HTML: %d bytes' % len(html), 'info')
                return html
        except Exception as e:
            control.log('[MRULZ] verifypeer failed: ' + str(e), 'warning')
            pass
        
        # Final fallback - try with default headers
        try:
            control.log('[MRULZ] Trying with default headers', 'info')
            html = client.request(url, headers=self.hdr)
            if html and len(html) > 100:
                control.log('[MRULZ] Got HTML: %d bytes' % len(html), 'info')
                return html
        except Exception as e:
            control.log('[MRULZ] Default headers failed: ' + str(e), 'warning')
            pass
        
        control.log('[MRULZ] All fetch attempts failed', 'warning')
        return ""

    def _get_html(self, url):
        """
        Fetch HTML with automatic retry and SSL/WAF bypass
        """
        html = self._fetch_html_with_retry(url)
        if html and len(html) > 100:
            return html
        control.log('[MRULZ] No valid HTML received', 'warning')
        return ""

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Movie Rulz')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = self._get_html(url)
        control.log('[MRULZ] Parsing HTML from: ' + url, 'info')
        
        # Debug: Log first 500 chars of HTML
        if html:
            control.log('[MRULZ] HTML preview: ' + html[:500], 'debug')
        
        mlink = SoupStrainer('div', {'id': 'content'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('nav', {'id': 'posts-nav'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'boxed film'})
        
        control.log('[MRULZ] Found %d movies' % len(items), 'info')
        
        # If no items found, try alternate selector
        if not items:
            control.log('[MRULZ] No items with boxed film, trying alternate selectors', 'warning')
            items = BeautifulSoup(html, "html.parser").find_all('div', {'class': 'film'})
            control.log('[MRULZ] Found %d items with film selector' % len(items), 'info')

        for item in items:
            title = self.unescape(item.text)
            if ')' in title:
                title = title.split(')')[0] + ')'
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'Older' in str(Paginator):
            nextli = Paginator.find('div', {'class': 'nav-older'})
            purl = nextli.find('a')['href']
            pages = purl.split('/')
            currpg = int(pages[len(pages) - 2]) - 1
            title = 'Next Page.. (Currently in Page {})'.format(currpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = self._get_html(url)
        mlink = SoupStrainer('div', {'class': 'entry-content'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('a')
            for link in links:
                vidurl = link.get('href')
                self.resolve_media(vidurl, videos)
        except:
            pass

        r = re.search(r'var\s*locations\s*=\s*([^;]+)', html)
        if r:
            links = json.loads(r.group(1))
            for link in links:
                if 'vcdnlare' in link:
                    link += '$${0}'.format(url)
                self.resolve_media(link, videos)

        return videos
