"""
Base deccandelight Scraper class
Copyright (C) 2016 Gujal

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

import base64
import json
import re
import threading

import six
from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client, control, jsunpack, unjuice, unjuice2
from six.moves import urllib_parse
from kodi_six import xbmcvfs


if control.PY2:
    import HTMLParser
    _html_parser = HTMLParser.HTMLParser()
else:
    import html
    _html_parser = html


def check_hosted_media(vid_url, subs=False):
    from resolveurl import HostedMediaFile
    return HostedMediaFile(url=vid_url, subs=subs)


class Scraper(object):

    def __init__(self):
        self.ipath = control._ipath
        self.hdr = control.mozhdr
        self.dhdr = control.droidhdr
        self.jhdr = control.jiohdr
        self.ihdr = control.ioshdr
        self.chdr = control.chromehdr
        self.PY2 = control.PY2
        self.parser = _html_parser
        self.settings = control.get_setting
        self.adult = control.get_setting('adult') == 'true'
        self.mirror = control.get_setting('mirror') == 'true'
        self.nicon = self.ipath + 'next.png'
        self.hmf = check_hosted_media
        self.log = control.log

    class Thread(threading.Thread):
        def __init__(self, target, *args):
            threading.Thread.__init__(self)
            self._target = target
            self._args = args

        def run(self):
            self._target(*self._args)

        def terminate(self):
            pass

    def get_nicon(self):
        return self.nicon

    @staticmethod
    def store(ftext, fname):
        fpath = control.TRANSLATEPATH(control._ppath) + fname
        if control.PY2:
            with open(fpath, 'w') as f:
                f.write(ftext)
        else:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(ftext)

    @staticmethod
    def retrieve(fname):
        fpath = control.TRANSLATEPATH(control._ppath) + fname
        if xbmcvfs.exists(fpath):
            if control.PY2:
                with open(fpath) as f:
                    ftext = f.readlines()
            else:
                with open(fpath, encoding='utf-8') as f:
                    ftext = f.readlines()
            return '\n'.join(ftext)
        else:
            return None

    @staticmethod
    def get_SearchQuery(sitename):
        keyboard = control.keyboard()
        keyboard.setHeading('Search ' + sitename)
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_text = keyboard.getText()

        return search_text

    @staticmethod
    def get_vidhost(url):
        """
        Trim the url to get the video hoster
        :return vidhost
        """
        parts = url.split('/')[2].split('.')
        vidhost = '{}.{}'.format(parts[len(parts) - 2], parts[len(parts) - 1])
        return vidhost

    def resolve_media(self, url, videos, vidtxt=''):
        non_str_list = [
            'olangal.', 'desihome.', 'thiruttuvcd', '.filmlinks4u', '#', '/t.me/',
            'cineview', 'bollyheaven', 'videolinkz', 'moviefk.co', 'goo.gl', '/ads/',
            'imdb.', 'mgid.', 'atemda.', 'movierulz.ht', 'facebook.', 'twitter.',
            'm2pub', 'abcmalayalam', 'india4movie.co', 'embedupload.', 'bit.ly',
            'tamilraja.', 'multiup.', 'filesupload.', 'fileorbs.', 'tamil.ws',
            'insurance-donate.', '.blogspot.', 'yodesi.net', 'desi-tashan.',
            'yomasti.co/ads', 'ads.yodesi', 'mylifeads.', 'yaartv.', '/cdn-cgi/'
            'steepto.', '/movierulztv', '/email-protection', 'oneload.xyz', 'about:',
            'google.com', 'whatsapp.com', 'linkedin.com'
        ]

        apneembed = [
            'newstalks.co', 'newstrendz.co', 'newscurrent.co', 'newsdeskroom.co',
            'newsapne.co', 'newshook.co', 'newsbaba.co', 'articlesnewz.com',
            'articlesnew.com', 'webnewsarticles.com', 'htnews.me'
        ]

        embed_list = [
            'cineview', 'bollyheaven', 'videolinkz', 'vidzcode', 'factualestates.',
            'embedzone', 'embedsr', 'fullmovie-hd', 'links4.pw', 'esr.', 'escr.',
            'embedscr', 'embedrip', 'movembed', 'power4link.us', 'adly.biz', 'kedne.',
            'watchmoviesonline4u', 'nobuffer.info', 'yomasti.co', 'myminiaturez.',
            'techking.me', 'onlinemoviesworld.xyz', 'cinebix.com', 'vids.xyz',
            'desihome.', 'loan-', 'filmshowonline.', 'hinditwostop.', 'media.php',
            'hindistoponline', 'telly-news.', 'tellytimes.', 'tellynews.', 'tvcine.',
            'business-', 'businessvoip.', 'toptencar.', 'serialinsurance.', 'bestarticles.',
            'youpdates', 'loanadvisor.', 'tamilray.', 'embedrip.', 'xpressvids.',
            'beststopapne.', 'bestinforoom.', '?trembed=', 'tamilserene.', 'articleweb.',
            'tvnation.', 'techking.', 'etcscrs.', 'etcsr1.', 'etcrips.', ' etcsrs.',
            'tvpost.cc', 'tellygossips.', 'tvarticles.', 'insurancehubportal.', 'hd-rulez.',
            'directlinktx.', 'filmstream2x.com', 'watchlinksinfo.com', 'esportarenahub.',
            'videoemx2.com', 'movierulz.io', 'coinztechnews.', 'thegadgetsreviewer.',
            'starscopsinsider.', 'dailyeduhub.'
        ]

        headers = {}
        if '|' in url:
            url, hdrs = url.split('|')
            hitems = hdrs.split('&')
            for hitem in hitems:
                hdr, value = hitem.split('=')
                headers.update({hdr: value})

        if url.startswith('magnet:'):
            if check_hosted_media(url):
                vidhost = '[COLOR red]Magnet[/COLOR]'
                r = re.findall(r'([\d\.\s]+\d(?:p|mb|gb))', url.replace('%20', ' '), re.I)
                if r:
                    vidhost = '{0} [COLOR gold]{1}[/COLOR]'.format(vidhost, ' | '.join(r))
                if vidtxt != '':
                    vidhost += ' | %s' % vidtxt
                if (vidhost, url) not in videos:
                    videos.append((vidhost, url))

        elif 'xdownex.xyz/' in url:
            headers.update(self.hdr)
            ehtml = client.request(url, headers=headers)
            s = re.findall(r'''<strong.+\n<a\s*href="([^"]+)''', ehtml, re.IGNORECASE)
            if s:
                for surl in s:
                    if check_hosted_media(surl):
                        vidhost = self.get_vidhost(surl)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, surl) not in videos:
                            videos.append((vidhost, surl))
                    else:
                        self.log('ResolveUrl cannot resolve 1 : {}'.format(surl), 'info')

        elif 'streamnetu.xyz/' in url:
            html = client.request(url, headers=self.hdr)
            mlink = SoupStrainer('div', {'class': re.compile('^entry-content')})
            videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
            links = videoclass.find_all('a')
            for link in links:
                surl = link.get('href')
                if check_hosted_media(surl):
                    vidhost = self.get_vidhost(surl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, surl) not in videos:
                        videos.append((vidhost, surl))
                else:
                    self.log('ResolveUrl cannot resolve 2 : {}'.format(surl), 'info')

        elif 'okmalayalam.' in url:
            mid = url.split('/')[-1]
            params = {'data': mid, 'do': 'getVideo'}
            data = {'hash': mid, 'r': ''}
            jd = client.request(
                'https://v.okmalayalam.org/player/index.php',
                XHR=True, referer=url,
                post=data, params=params
            )
            if jd:
                jd = json.loads(jd)
                # surl = jd.get('videoSource')
                surl = jd.get('securedLink')
                vidhost = self.get_vidhost(surl)
                if vidtxt != '':
                    vidhost += ' | %s' % vidtxt
                if (vidhost, surl) not in videos:
                    videos.append((vidhost, surl))
            else:
                self.log('Cannot resolve : {}'.format(url), 'info')

        elif 'watchlinkx.xyz/' in url:
            html = client.request(url, headers=self.hdr)
            r = re.search(r'class="main-button[^>]+?href="([^"]+)', html)
            if r:
                surl = r.group(1)
                if check_hosted_media(surl):
                    vidhost = self.get_vidhost(surl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, surl) not in videos:
                        videos.append((vidhost, surl))
                else:
                    self.log('ResolveUrl cannot resolve 3 : {}'.format(surl), 'info')

        elif 'filelinkzr.com/' in url:
            html = client.request(url, headers=self.hdr)
            r = re.search(r'<a\s*class="mb-ton\s*ndton"\s+href="([^"]+)', html)
            if r:
                surl = r.group(1)
                surl = re.sub(r'\s', '', surl)
                if 'videoemx2.com/' in surl:
                    html = client.request(surl, headers=self.hdr)
                    r = re.search(r'<iframe.+?src="([^"]+)', html)
                    if r:
                        surl = r.group(1)
                if check_hosted_media(surl):
                    vidhost = self.get_vidhost(surl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, surl) not in videos:
                        videos.append((vidhost, surl))
                else:
                    self.log('ResolveUrl cannot resolve 3a : {}'.format(surl), 'info')
            r = re.search(r'<iframe\s*src="([^"]+)', html, re.DOTALL)
            if r:
                surl = r.group(1)
                surl = re.sub(r'\s', '', surl)
                if check_hosted_media(surl):
                    vidhost = self.get_vidhost(surl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, surl) not in videos:
                        videos.append((vidhost, surl))
                else:
                    self.log('ResolveUrl cannot resolve 3aa : {}'.format(surl), 'info')

        elif 'filmshowonline.net/media/' in url:
            try:
                headers.update(self.hdr)
                r = client.request(url, headers=headers, output='extended')
                clink = r[0]
                cookie = r[4]
                eurl = re.findall(r"var\s*height.+?url:\s*'([^']+)", clink, re.DOTALL)[0]
                if not eurl.startswith('http'):
                    eurl = 'https:' + eurl
                enonce = re.findall(r"var\s*height.+?nonce.+?'([^']+)", clink, re.DOTALL)[0]
                evid = re.findall(r"var\s*height.+?link_id:\s*([^\s]+)", clink, re.DOTALL)[0]
                values = {'echo': 'true',
                          'nonce': enonce,
                          'width': '848',
                          'height': '480',
                          'link_id': evid}
                headers = self.hdr
                headers.update({'Referer': url, 'X-Requested-With': 'XMLHttpRequest'})
                emdiv = client.request(eurl, post=values, headers=headers, cookie=cookie)
                emdiv = json.loads(emdiv).get('embed')
                strurl = re.findall('(http[^"]+)', emdiv)[0]
                if check_hosted_media(strurl):
                    vidhost = self.get_vidhost(strurl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
            except:
                pass

        elif 'cdn.jwplayer.com' in url:
            headers.update(self.hdr)
            media_id = url.split('/')[-1].split('-')[0]
            jurl = 'https://content.jwplatform.com/v2/media/{0}'.format(media_id)
            r = client.request(jurl, headers=headers, output='extended')
            if int(r[1]) < 400:
                vitem = json.loads(r[0]).get('playlist')[0]
                vlink = vitem.get('sources')[0].get('file')
                if vlink:
                    vidhost = self.get_vidhost(vlink)
                    vidtxt = vitem.get('title')
                    if 'part' in vidtxt.lower():
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, vlink) not in videos:
                        videos.append((vidhost, vlink))
                else:
                    self.log('Cannot resolve: {0}'.format(url), 'info')

        elif 'thrfive.io' in url:
            headers.update(self.hdr)
            res = client.request(url, referer='https://www.tamildhool.net/', headers=headers)
            if unjuice2.test(res):
                res = unjuice2.run(res)
            jd = json.loads(re.findall(r'config\s*=\s*([^;]+)', res)[0])
            headers.update({'Origin': 'https://thrfive.io', 'Referer': 'https://thrfive.io/', 'Accept-Language': 'en-US,en;q=0.5'})
            strurl = jd.get('sources').get('file') + '|' + urllib_parse.urlencode(headers)
            vidhost = self.get_vidhost(strurl)
            if vidtxt != '':
                vidhost += ' | %s' % vidtxt
            if (vidhost, strurl) not in videos:
                videos.append((vidhost, strurl))

        elif 'justmoviesonline.com' in url:
            headers.update(self.hdr)
            html = client.request(url, headers=headers)
            src = re.search(r"atob\('(.*?)'", html)
            if src:
                src = src.group(1)
                src = base64.b64decode(src).decode('utf-8')
                try:
                    strurl = re.findall('file":"(.*?)"', src)[0]
                    vidhost = 'GVideo'
                    strurl = urllib_parse.quote_plus(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                except:
                    pass
                try:
                    strurl = re.findall('''source src=["'](.*?)['"]''', src)[0]
                    vidhost = self.get_vidhost(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                except:
                    pass
            elif '?id=' in url:
                src = eval(re.findall('Loading.+?var.+?=([^;]+)', html, re.DOTALL)[0])
                for item in src:
                    if 'http' in item and 'justmovies' not in item:
                        strurl = item
                strurl += url.split('?id=')[1]
                strurl += '.mp4|User-Agent={}'.format(self.mozhdr['User-Agent'])
                vidhost = 'GVideo'
                strurl = urllib_parse.quote_plus(strurl)
                if (vidhost, strurl) not in videos:
                    videos.append((vidhost, strurl))

        elif 'videohost.site' in url or 'videohost1.com' in url:
            try:
                headers.update(self.hdr)
                html = client.request(url, headers=headers)
                pdata = eval(re.findall(r'Run\((.*?)\)', html)[0])
                pdata = base64.b64decode(pdata).decode('utf-8')
                linkcode = jsunpack.unpack(pdata).replace('\\', '')
                sources = json.loads(re.findall(r'sources:(.*?\}\])', linkcode)[0])
                for source in sources:
                    strurl = source['file'] + '|Referer={}'.format(url)
                    vidhost = self.get_vidhost(url) + ' | GVideo | {}'.format(source['label'])
                    strurl = urllib_parse.quote_plus(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
            except:
                pass

        elif 'akamaihd.' in url:
            vidhost = self.get_vidhost(url)
            if (vidhost, url) not in videos:
                videos.append((vidhost, url))

        elif 'videohost2.com' in url:
            headers.update(self.hdr)
            html = client.request(url, headers=headers)

            try:
                pdata = eval(re.findall(r'Loading video.+?(\[.+?\]);', html, re.DOTALL)[0])
                if 'id=' in url:
                    strurl = pdata[7] + url.split('=')[1] + pdata[9]
                else:
                    strurl = pdata[7]
                vidhost = self.get_vidhost(url) + ' | GVideo'
                strurl = urllib_parse.quote_plus(strurl + '|Referer={}'.format(url))
                if (vidhost, strurl) not in videos:
                    videos.append((vidhost, strurl))
            except:
                pass

            try:
                pdata = re.findall(r"atob\('([^']+)", html)[0]
                pdata = base64.b64decode(pdata).decode('utf-8')
                strurl = re.findall(r"source\ssrc='([^']+)", pdata)[0] + '|Referer={}'.format(url)
                vidhost = self.get_vidhost(url)
                strurl = urllib_parse.quote_plus(strurl)
                if (vidhost, strurl) not in videos:
                    videos.append((vidhost, strurl))
            except:
                pass

        elif 'hindistoponline' in url or 'hindigostop' in url:
            headers.update(self.hdr)
            url = url.replace('www.hindistoponline.com', 'hindigostop.com')
            html = client.request(url, headers=headers)

            try:
                strurl = re.findall(r'source:\s*"([^"]+)', html)[0]
                vidhost = self.get_vidhost(strurl)
                strurl = urllib_parse.quote_plus(strurl + '|User-Agent={}&Referer={}'.format(self.mozhdr['User-Agent'], url))
                if (vidhost, strurl) not in videos:
                    videos.append((vidhost, strurl))
            except:
                pass

            try:
                strurl = re.findall('''(?i)<iframe.+?src=["']([^'"]+)''', html)[0]
                if check_hosted_media(strurl):
                    vidhost = self.get_vidhost(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                else:
                    self.log('ResolveUrl cannot resolve 4: {}'.format(url), 'info')
            except:
                pass

        elif 'arivakam.' in url:
            headers.update(self.hdr)
            if '$$' in url:
                url, ref = url.split('$$')
                headers.update({'Referer': ref})
            html = client.request(url, headers=headers, verify=False)
            rurl = urllib_parse.urljoin(url, '/')
            strurl = re.search(r'"file":"([^"]+)', html)
            if strurl:
                embedurl = strurl.group(1)
                if 'playallu' in embedurl:
                    vidhost, strurl = self.playallu(embedurl, rurl)
                    if vidhost is not None:
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                else:
                    vidhost = self.get_vidhost(embedurl)
                    embedurl += '|Referer={0}'.format(rurl)
                    if (vidhost, embedurl) not in videos:
                        videos.append((vidhost, embedurl))
            else:
                embedurl = re.search(r'<iframe.+?src="([^"]+)', html)
                if embedurl:
                    embedurl = embedurl.group(1)
                    if 'playallu' in embedurl:
                        vidhost, strurl = self.playallu(embedurl, rurl)
                        if vidhost is not None:
                            if (vidhost, strurl) not in videos:
                                videos.append((vidhost, strurl))
                    else:
                        vidhost = self.get_vidhost(embedurl)
                        embedurl += '|Referer={0}'.format(rurl)
                        if (vidhost, embedurl) not in videos:
                            videos.append((vidhost, embedurl))
            sources = re.findall(r'"linkserver".+?video="([^"]+)', html)
            if sources:
                for embedurl in sources:
                    headers.update({'Referer': url})
                    if 'playallu' in embedurl:
                        vidhost, strurl = self.playallu(embedurl, rurl)
                        if vidhost is not None:
                            if (vidhost, strurl) not in videos:
                                videos.append((vidhost, strurl))
                    elif embedurl.startswith('api_player') and 'type=default' not in embedurl:
                        ehtml = client.request(rurl + 'player/' + embedurl, headers=headers, verify=False)
                        linkcode = jsunpack.unpack(ehtml).replace('\\', '')
                        elink = re.findall(r'''file"\s*:\s*"([^"]+)''', linkcode)
                        if elink:
                            strurl = elink[0]
                            vidhost = self.get_vidhost(strurl)
                            strurl += '|Referer={0}'.format(rurl)
                            if (vidhost, strurl) not in videos:
                                videos.append((vidhost, strurl))
            mid = url.split('/')[-1]
            aurl = urllib_parse.urljoin(url, '/api/movie')
            headers.update({'Referer': url})
            ehtml = client.request(aurl, headers=headers, params={'id': mid})
            if ehtml:
                sources = json.loads(ehtml).get('movieInfo')
                for iid, src in six.iteritems(sources):
                    strurl = src.get('urlStream')
                    vidhost = self.get_vidhost(strurl)
                    if 'playallu' in strurl:
                        vidhost, strurl = self.playallu(strurl, url)
                    if vidhost is not None:
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))

        elif 'tamildbox' in url or 'tamilhdbox' in url:
            if 'embed' in url:
                thdr = self.mozhdr
                thdr['Referer'] = url
                r = client.request(url, headers=thdr)
                match = re.search(r"domainStream\s*=\s*([^;]+)", r)
                if match:
                    surl = re.findall('file":"([^"]+)', match.group(1))[0]

                    if 'vidyard' in surl:
                        surl += '|Referer=https://play.vidyard.com/'
                    else:
                        surl = surl.replace('/hls/', '/own1hls/2020/')
                        surl += '|Referer=https://embed1.tamildbox.tips/'

                    surl += '&User-Agent={}'.format(self.mozhdr['User-Agent'])
                else:
                    surl = url.replace('hls_vast', 'hls').replace('.tamildbox.tips', '.tamilgun.tv')
                    if '.m3u8' not in surl:
                        surl += '/playlist.m3u8'
                vidhost = self.get_vidhost(surl)
                if (vidhost, surl) not in videos:
                    videos.append((vidhost, surl))
            else:
                link = client.request(url)

                try:
                    mlink = SoupStrainer('div', {'class': re.compile('^video-player-content')})
                    videoclass = BeautifulSoup(link, "html.parser", parse_only=mlink)
                    vlinks = videoclass.find_all('iframe')
                    for vlink in vlinks:
                        iurl = vlink.get('src')
                        if iurl.startswith('//'):
                            iurl = 'https:' + iurl
                        if 'playallu.' in iurl:
                            vidhost, strlink = self.playallu(iurl, url)
                            if vidhost is not None:
                                if (vidhost, strlink) not in videos:
                                    videos.append((vidhost, strlink))
                        else:
                            if check_hosted_media(iurl):
                                vidhost = self.get_vidhost(iurl)
                                if (vidhost, iurl) not in videos:
                                    videos.append((vidhost, iurl))
                except:
                    import traceback
                    traceback.print_exc()
                    pass

                try:
                    mlink = SoupStrainer('div', {'class': 'player-api'})
                    videoclass = BeautifulSoup(link, "html.parser", parse_only=mlink)
                    vlinks = videoclass.find_all('iframe')
                    for item in vlinks:
                        blink = item.get('src')
                        if 'cdn.jwplayer.com' in blink:
                            headers.update(self.hdr)
                            media_id = blink.split('/')[-1].split('-')[0]
                            jurl = 'https://content.jwplatform.com/v2/media/{0}'.format(media_id)
                            jd = json.loads(client.request(jurl, headers=headers))
                            vlink = jd.get('playlist')[0].get('sources')[0].get('file')
                            if vlink:
                                vidhost = self.get_vidhost(vlink)
                                if (vidhost, vlink) not in videos:
                                    videos.append((vidhost, vlink))
                        else:
                            self.log('Cannot resolve : {0}'.format(blink), 'info')
                except:
                    pass

                try:
                    etext = re.search(r'var\s*vidorev_jav_js_object\s*=\s*([^;]+)', link, re.DOTALL)
                    if etext:
                        glink = json.loads(etext.group(1)).get('single_video_url')
                        vidhost = self.get_vidhost(glink)
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    etext = re.search(r'file:\s*"([^"]+).+?type:\s*"([^"]+)', link, re.DOTALL)
                    if etext:
                        glink = etext.group(1)
                        vidhost = self.get_vidhost(glink) + ' | {}'.format(etext.group(2))
                        if 'http' not in glink:
                            glink = 'http:' + glink
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                    etext = re.search(r'file":\s*"([^"]+).+?label":\s*"([^"]+)', link, re.DOTALL)
                    if etext:
                        glink = etext.group(1)
                        vidhost = self.get_vidhost(glink) + ' | {}'.format(etext.group(2))
                        if 'http' not in glink:
                            glink = 'http:' + glink
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    mlink = SoupStrainer('div', {'id': 'player-embed'})
                    dclass = BeautifulSoup(link, "html.parser", parse_only=mlink)
                    if 'unescape' in str(dclass):
                        etext = re.findall("unescape.'[^']*", str(dclass))[0]
                        etext = urllib_parse.unquote(etext)
                        dclass = BeautifulSoup(etext, "html.parser")
                    glink = dclass.iframe.get('src')
                    if check_hosted_media(glink):
                        vidhost = self.get_vidhost(glink)
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    mlink = SoupStrainer('div', {'class': re.compile('^item-content')})
                    dclass = BeautifulSoup(link, "html.parser", parse_only=mlink)
                    glink = dclass.p.iframe.get('src')
                    if check_hosted_media(glink):
                        vidhost = self.get_vidhost(glink)
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    if 'p,a,c,k,e,d' in link:
                        linkcode = jsunpack.unpack(link).replace('\\', '')
                        glink = re.findall(r"file\s*:\s*'(.*?)'", linkcode)[0]
                    if 'youtu.be' in glink:
                        glink = 'https://docs.google.com/vt?id=' + glink[16:]
                    if check_hosted_media(glink):
                        vidhost = self.get_vidhost(glink)
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    codes = re.findall(r'"return loadEP.([^,]*),(\d*)', link)
                    for ep_id, server_id in codes:
                        burl = 'https://{}/actions.php?case=loadEP&ep_id={}&server_id={}'.format(url.split('/')[2], ep_id, server_id)
                        bhtml = client.request(burl)
                        blink = re.findall('<iframe.+?src="([^"]+)', bhtml, re.IGNORECASE)[0]
                        if blink.startswith('//'):
                            blink = 'https:' + blink
                        if 'googleapis' in blink:
                            blink = 'https://drive.google.com/open?id=' + re.findall('docid=([^&]*)', blink)[0]
                            vidhost = 'GVideo'
                            if (vidhost, blink) not in videos:
                                videos.append((vidhost, blink))
                        elif 'cdn.jwplayer.com' in blink:
                            headers.update(self.hdr)
                            media_id = blink.split('/')[-1].split('-')[0]
                            jurl = 'https://content.jwplatform.com/v2/media/{0}'.format(media_id)
                            jd = json.loads(client.request(jurl, headers=headers))
                            vlink = jd.get('playlist')[0].get('sources')[0].get('file')
                            if vlink:
                                vidhost = self.get_vidhost(vlink)
                                if (vidhost, vlink) not in videos:
                                    videos.append((vidhost, vlink))
                            else:
                                self.log('Cannot resolve : {0}'.format(blink), 'info')
                        elif 'tamildbox.' in blink:
                            if 'embed' in blink:
                                thdr = self.mozhdr
                                thdr['Referer'] = blink
                                r = client.request(blink, headers=thdr)
                                match = re.search(r"domainStream\s*=\s*'([^']+)", r)
                                if match:
                                    surl = match.group(1)
                                    if 'vidyard' in surl:
                                        surl += '|Referer=https://play.vidyard.com/'
                                    else:
                                        if '.php' not in surl:
                                            if '.m3u8' not in surl:
                                                surl += '/playlist.m3u8'
                                        surl = surl.replace('/hls/', '/hls1mp4/2020/')
                                        surl += '|Referer=https://embed1.tamildbox.tips/'
                                    surl += '&User-Agent={}'.format(self.mozhdr['User-Agent'])
                                else:
                                    surl = blink.replace('hls_vast', 'hls')
                                    surl = surl.replace('.tamildbox.tips', '.tamilgun.tv')
                                    if '.m3u8' not in surl:
                                        surl += '/playlist.m3u8'
                                vidhost = self.get_vidhost(surl)
                                if (vidhost, surl) not in videos:
                                    videos.append((vidhost, surl))
                            else:
                                link = client.request(blink)
                                etext = re.search(r'file:\s*"([^"]+).+?type:\s*"([^"]+)', link, re.DOTALL)
                                if etext:
                                    glink = etext.group(1)
                                    vidhost = self.get_vidhost(glink) + ' | {}'.format(etext.group(2))
                                    if glink.startswith('//'):
                                        glink = 'https:' + glink
                                    if (vidhost, glink) not in videos:
                                        videos.append((vidhost, glink))
                                etext = re.search(r'file":\s*"([^"]+).+?label":\s*"([^"]+)', link, re.DOTALL)
                                if etext:
                                    glink = etext.group(1)
                                    vidhost = self.get_vidhost(glink) + ' | {}'.format(etext.group(2))
                                    if glink.startswith('//'):
                                        glink = 'https:' + glink
                                    if (vidhost, glink) not in videos:
                                        videos.append((vidhost, glink))
                        else:
                            if check_hosted_media(blink):
                                vidhost = self.get_vidhost(blink)
                                if (vidhost, blink) not in videos:
                                    videos.append((vidhost, blink))
                            else:
                                self.log('Resolveurl cannot resolve 5 : {}'.format(blink), 'info')
                except:
                    pass

        elif 'tamilthee.' in url:
            vidhost = self.get_vidhost(url)
            vidurl = url.replace('/p/', '/v/') + '.m3u8'
            if (vidhost, vidurl) not in videos:
                videos.append((vidhost, vidurl))

        elif 'vidnext.net' in url:
            if 'streaming.php' in url:
                headers.update(self.hdr)
                url = 'https:' + url if url.startswith('//') else url
                chtml = client.request(url, headers=headers)
                clink = SoupStrainer('ul', {'class': 'list-server-items'})
                csoup = BeautifulSoup(chtml, "html.parser", parse_only=clink)
                citems = csoup.find_all('li')
                for citem in citems:
                    link = citem.get('data-video')
                    if link and 'vidnext.net' not in link:
                        if check_hosted_media(link):
                            vidhost = self.get_vidhost(link)
                            if vidtxt != '':
                                vidhost += ' | %s' % vidtxt
                            if (vidhost, link) not in videos:
                                videos.append((vidhost, link))
                        else:
                            self.log('ResolveUrl cannot resolve 6 : {}'.format(link), 'info')

        elif 'bollyfunmaza.' in url:
            if '/vid/' in url and 'multiup' not in url:
                headers.update(self.hdr)
                bhtml = client.request(url, headers=headers)
                r = re.findall(r'''<form.+?action="([^"]+)''', bhtml, re.DOTALL)
                if r:
                    purl = r[-1]
                    headers.update({'Referer': url,
                                    'Origin': urllib_parse.urljoin(url, '/')[:-1]})
                    r1 = re.findall(r"type='hidden'\s*name='([^']+)'\s*value='([^']+)", bhtml)
                    if r1:
                        pd = {x: y for x, y in r1}
                    else:
                        pd = ' '
                    bhtml2 = client.request(purl, post=pd, headers=headers)
                    r = re.findall(r'''<form.+?action="([^"]+)''', bhtml2, re.DOTALL)
                    if r:
                        purl = r[-1]
                        headers.update({'Referer': url,
                                        'Origin': urllib_parse.urljoin(url, '/')[:-1]})
                        r1 = re.findall(r"type='hidden'\s*name='([^']+)'\s*value='([^']+)", bhtml2)
                        if r1:
                            pd = {x: y for x, y in r1}
                        else:
                            pd = ' '
                        ehtml = client.request(purl, post=pd, headers=headers)

                        s = re.search(r'''<iframe.+?src=['"]([^'"]+)''', ehtml, re.IGNORECASE)
                        if s:
                            if check_hosted_media(s.group(1)):
                                vidhost = self.get_vidhost(s.group(1))
                                if vidtxt != '':
                                    vidhost += ' | %s' % vidtxt
                                if (vidhost, s.group(1)) not in videos:
                                    videos.append((vidhost, s.group(1)))
                            else:
                                self.log('ResolveUrl cannot resolve 7 : {}'.format(s.group(1)), 'info')
                else:
                    s = re.search(r'''<iframe.+?src=["']([^"']+)''', bhtml, re.DOTALL)
                    if s:
                        if check_hosted_media(s.group(1)):
                            vidhost = self.get_vidhost(s.group(1))
                            if vidtxt != '':
                                vidhost += ' | %s' % vidtxt
                            if (vidhost, s.group(1)) not in videos:
                                videos.append((vidhost, s.group(1)))
                        else:
                            self.log('ResolveUrl cannot resolve 7b : {}'.format(s.group(1)), 'info')

        elif 'viralnews.' in url:
            headers.update(self.hdr)
            r = client.request(url, headers=headers, output='extended')
            url = r[2].get('Refresh').split(' ')[-1]
            ehtml = client.request(url, headers=headers)
            s = re.search(r'''<iframe.+?src=['"]([^'"]+)''', ehtml, re.IGNORECASE)
            if s:
                if check_hosted_media(s.group(1)):
                    vidhost = self.get_vidhost(s.group(1))
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, s.group(1)) not in videos:
                        videos.append((vidhost, s.group(1)))
                else:
                    self.log('ResolveUrl cannot resolve 8 : {}'.format(s.group(1)), 'info')

        elif 'gomovies.top' in url:
            headers.update(self.hdr)
            chtml = client.request(url, headers=headers)
            clink = SoupStrainer('ul', {'class': 'list-server-items'})
            csoup = BeautifulSoup(chtml, "html.parser", parse_only=clink)
            citems = csoup.find_all('li')
            for citem in citems:
                link = citem.get('data-video')
                if 'gomovies.to' in link:
                    ghtml = client.request(link, headers=headers)
                    glink = re.search(r'file:\s*"([^"]+)', ghtml)
                    if glink:
                        glink = glink.group(1) + '|User-Agent=iPad'
                        vidhost = self.get_vidhost(glink)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, link) not in videos:
                            videos.append((vidhost, glink))
                else:
                    if check_hosted_media(link):
                        vidhost = self.get_vidhost(link)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, link) not in videos:
                            videos.append((vidhost, link))

        elif any([x in url for x in apneembed]):
            headers.update(self.hdr)
            refresh = True
            while refresh:
                r = client.request(url, headers=headers, output='extended')
                html = r[0]
                if r[2].get('Refresh'):
                    url = r[2].get('Refresh').split(' ')[-1]
                elif 'http-equiv="refresh"' in html:
                    url = _html_parser.unescape(re.findall(r'http-equiv="refresh".+?url=([^"]+)', html)[0])
                else:
                    refresh = False

            r = re.findall(r'''<form.+?action="([^"]+)''', html, re.DOTALL)
            if r:
                purl = r[-1]
                headers.update({'Referer': url,
                                'Origin': urllib_parse.urljoin(url, '/')[:-1]})
                r1 = re.findall(r"type='hidden'\s*name='([^']+)'\s*value='([^']+)", html)
                if r1:
                    pd = {x: y for x, y in r1}
                else:
                    pd = ' '
                ehtml = client.request(purl, post=pd, headers=headers)
                s = re.findall(r'''<iframe.+?src=['"]([^"']+)''', ehtml)
                if s:
                    strurl = s[0]
                    if 'url=' in strurl:
                        strurl = strurl.split('url=')[-1]
                    vidhost = self.get_vidhost(strurl)
                    if 'hls' in strurl and 'videoapne' in strurl:
                        strurl = strurl.replace('hls/,', '')
                        strurl = strurl.replace(',.urlset/master.m3u8', '/v.mp4')
                        vidhost = self.get_vidhost(strurl)
                    elif check_hosted_media(strurl):
                        vidhost = self.get_vidhost(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))

        elif '.box.' in url and '.mp4' in url:
            vidhost = self.get_vidhost(url)
            if (vidhost, url) not in videos:
                videos.append((vidhost, url))

        elif 'files.' in url and url.endswith('.mp4'):
            vidhost = self.get_vidhost(url)
            if (vidhost, url) not in videos:
                videos.append((vidhost, url))

        elif any([x in url for x in embed_list]):
            url = url.replace('hd-rulez.info/', 'business-mortgage.biz/')
            vidcount = 0
            headers.update(self.hdr)
            clink = client.request(url, headers=headers)
            csoup = BeautifulSoup(clink, "html.parser")

            try:
                url2 = csoup.find('meta', {'http-equiv': 'refresh'}).get('content').split('URL=')[-1]
                if any([x in url2 for x in embed_list]):
                    clink = client.request(url2, headers=headers)
                    csoup = BeautifulSoup(clink, "html.parser")
                else:
                    self.log('Cannot Process : {}'.format(url2), 'info')
            except:
                pass

            try:
                links = csoup.find_all('iframe')
                headers.update({'Referer': urllib_parse.urljoin(url, '/')})
                for link in links:
                    strurl = link.get('src')
                    if 'about:' in strurl:
                        strurl = link.get('data-phast-src')
                    if any([x in strurl for x in ['apnevideotwo', 'player.business']]):
                        vidhost = 'CDN Direct'
                        if vidtxt:
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    elif 'apnevideoone' in strurl:
                        shtml = client.request(strurl, headers=headers)
                        vidurl = re.findall(r'link_play\s*=\s*\[{"file":"([^"]+)', shtml)[0]
                        vidurl = vidurl.encode('utf8') if self.PY2 else vidurl
                        vhdr = {'Origin': 'https://apnevideoone.co'}
                        vidurl = '{0}|{1}'.format(vidurl, urllib_parse.urlencode(vhdr))
                        vidhost = 'CDN Apne'
                        if vidtxt:
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, vidurl) not in videos:
                            videos.append((vidhost, vidurl))
                        vidcount += 1
                    elif 'flow.' in strurl:
                        headers.update({'Priority': 'u=4'})
                        shtml = client.request(strurl, headers=headers, verify=False)
                        if unjuice.test(shtml):
                            shtml = unjuice.run(shtml)
                        if jsunpack.detect(shtml):
                            shtml = jsunpack.unpack(shtml)
                        vidurl = re.findall(r'sources\s*:\s*\[\{\s*"(?:file|src)"\s*:\s*"([^"]+)', shtml)[0]
                        vidurl = vidurl.encode('utf8') if self.PY2 else vidurl
                        vidhost = self.get_vidhost(vidurl) + ' Direct'
                        refr = urllib_parse.urljoin(strurl, '/')
                        vhdr = {'Referer': refr, 'Origin': refr[:-1], 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0'}
                        vidurl += '|{}'.format(urllib_parse.urlencode(vhdr))
                        if vidtxt:
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, vidurl) not in videos:
                            videos.append((vidhost, vidurl))
                        vidcount += 1
                    elif 'drivewire.' in strurl:
                        vid = strurl.split('id=')[-1]
                        parts = urllib_parse.urlparse(strurl)
                        vidurl = '{0}://{1}/hls/{2}/{2}.m3u8'.format(parts.scheme, parts.netloc, vid)
                        vidhost = 'DriveWire'
                        if vidtxt:
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, vidurl) not in videos:
                            videos.append((vidhost, vidurl))
                        vidcount += 1
                    elif not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                        if check_hosted_media(strurl):
                            vidhost = self.get_vidhost(strurl)
                            if vidtxt != '':
                                vidhost += ' | %s' % vidtxt
                            if (vidhost, strurl) not in videos:
                                videos.append((vidhost, strurl))
                            vidcount += 1
                        else:
                            self.log('Resolveurl cannot resolve 9 : {}'.format(strurl), 'info')
            except Exception as e:
                self.log(e, 'error')
                pass

            try:
                sources = re.findall(r'sources:\s*([^\]]+)', clink, re.DOTALL)[0]
                links = re.findall(r'''src:\s*['"]([^"']+)''', sources)
                for strurl in links:
                    vidhost = self.get_vidhost(strurl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                    vidcount += 1
            except:
                pass

            try:
                r = re.search(r'jwplayer\("container"\).setup\({\s*\n\s*file:\s*"([^"]+)', clink)
                if r:
                    strurl = r.group(1)
                    vidhost = self.get_vidhost(strurl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                    vidcount += 1
            except:
                pass

            try:
                plink = csoup.find('a', {'class': 'main-button dlbutton'})
                strurl = plink.get('href')
                if 'videoemx2.com' in strurl:
                    dlink = client.request(strurl, headers=headers)
                    dlinks = SoupStrainer('div', {'class': 'entry-content'})
                    dsoup = BeautifulSoup(dlink, 'html.parser', parse_only=dlinks)
                    strurl = dsoup.find('iframe').get('src')

                if not any([x in strurl for x in non_str_list]):
                    if check_hosted_media(strurl):
                        vidhost = self.get_vidhost(strurl)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve 10 : {}'.format(strurl), 'info')
            except:
                pass

            try:
                plink = csoup.find('div', {'class': 'aio-pulse'})
                strurl = plink.find('a')['href']
                if not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                    if check_hosted_media(strurl):
                        vidhost = self.get_vidhost(strurl)
                        if vidtxt != '':
                            vidhost += ' | {}'.format(vidtxt)
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve 11 : {}'.format(strurl), 'info')
            except:
                pass

            try:
                plink = csoup.find('div', {'class': re.compile('entry-content')})
                strurl = plink.find('a')['href']
                if not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                    if check_hosted_media(strurl):
                        vidhost = self.get_vidhost(strurl)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve 12 : {}'.format(strurl), 'info')
            except:
                pass

            try:
                for linksSection in csoup.find_all('embed'):
                    strurl = linksSection.get('src')
                    if not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                        if check_hosted_media(strurl):
                            vidhost = self.get_vidhost(strurl)
                            if vidtxt != '':
                                vidhost += ' | %s' % vidtxt
                            if (vidhost, strurl) not in videos:
                                videos.append((vidhost, strurl))
                            vidcount += 1
                        else:
                            self.log('Resolveurl cannot resolve 13 : {}'.format(strurl), 'info')
            except:
                pass

            try:
                plink = csoup.find('div', {'id': 'Proceed'})
                strurl = plink.find('a')['href']
                if not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                    if check_hosted_media(strurl):
                        vidhost = self.get_vidhost(strurl)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve 14 : {}'.format(strurl), 'info')
            except:
                pass

            try:
                vid = re.findall(r'tune\.pk[^?]+\?vid=([^&]+)', clink)[0]
                strurl = 'https://tune.pk/video/{vid}/'.format(vid=vid)
                if check_hosted_media(strurl):
                    vidhost = self.get_vidhost(strurl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                    vidcount += 1
                else:
                    self.log('Resolveurl cannot resolve 15: {}'.format(strurl), 'info')
            except:
                pass

            try:
                vidurl = re.search(r'file\s*:\s*"([^"]+)', clink)
                if vidurl:
                    vidurl = vidurl.group(1)
                    vidhost = self.get_vidhost(vidurl)
                    if (vidhost, vidurl) not in videos:
                        videos.append((vidhost, vidurl))
                    vidcount += 1
            except:
                pass

            if vidcount == 0:
                self.log('Could not process link : {}'.format(url), 'info')

        elif not any([x in url for x in non_str_list]):
            if check_hosted_media(url):
                vidhost = self.get_vidhost(url)
                if 'Referer' in headers.keys():
                    url = '{0}$${1}'.format(url, headers.get('Referer'))
                if vidtxt != '':
                    vidhost += ' | %s' % vidtxt
                if (vidhost, url) not in videos:
                    videos.append((vidhost, url))
            else:
                self.log('ResolveUrl cannot resolve 16 : {}'.format(url), 'info')

        return

    @staticmethod
    def clean_title(title):
        cleanup = [
            'Watch Online Movie', 'Watch Onilne', 'Tamil Movie ', 'Tamil Dubbed', 'WAtch ', 'Online Free',
            'Full Length', 'Latest Telugu', 'RIp', 'DvDRip', 'DvDScr', 'Full Movie Online Free', 'Uncensored',
            'Full Movie Online', 'Watch Online ', 'Free HD', 'Online Full Movie', 'Downlaod', 'Bluray',
            'Full Free', 'Malayalam Movie', ' Malayalam ', 'Full Movies', 'Full Movie', 'Free Online',
            'Movie Online', 'Watch ', 'movie online', 'Wach ', 'Movie Songs Online', 'Full Hindi', 'Korean',
            'tamil movie songs online', 'tamil movie songs', 'movie songs online', 'Tamil Movie', 'In Hindi',
            'Hilarious Comedy Scenes', 'Super Comedy Scenes', 'Ultimate Comedy Scenes', 'Watch...', 'BDRip',
            'Super comedy Scenes', 'Comedy Scenes', 'hilarious comedy Scenes', '...', 'Telugu Movie', 'TodayPk',
            'Sun TV Show', 'Vijay TV Show', 'Vijay Tv Show', 'Vijay TV Comedy Show', 'Hindi Movie', 'Film',
            'Vijay Tv Comedy Show', 'Vijay TV', 'Vijay Tv', 'Sun Tv Show', 'Download', 'Starring', u'\u2013',
            'Tamil Full Movie', 'Tamil Horror Movie', 'Tamil Dubbed Movie', '|', '-', ' Full ', u'\u2019',
            '/', 'Pre HDRip', '(DVDScr Audio)', 'PDVDRip', 'DVDSCR', '(HQ Audio)', 'HQ', ' Telugu', 'BRRip',
            'DVDScr', 'DVDscr', 'PreDVDRip', 'DVDRip', 'DVDRIP', 'WEBRip', 'WebRip', 'Movie ', ' Punjabi',
            'TCRip', 'HDRip', 'HDTVRip', 'HD-TC', 'HDTV', 'TVRip', '720p', 'DVD', 'HD', ' Dubbed', '( )',
            '720p', '(UNCUT)', 'UNCUT', '(Clear Audio)', 'DTHRip', '(Line Audio)', ' Kannada', ' Hollywood',
            'TS', 'CAM', 'Online Full', '[+18]', 'Streaming Free', 'Permalink to ', 'And Download', '()',
            'Full English', ' English', 'Online', ' Tamil', ' Bengali', ' Bhojpuri', 'Print Free', ' Hindi',
            'Free', 'Video Episode Update'
        ]

        for word in cleanup:
            if word in title:
                title = title.replace(word, '')

        title = title.strip()
        title = title.encode('utf8') if control.PY2 else title
        return title

    @staticmethod
    def unescape(title):
        return _html_parser.unescape(title)

    @staticmethod
    def playallu(eurl, referer):
        from resources.lib import jscrypto
        import binascii
        import hashlib

        def pencode(c, m):
            i = jscrypto.encode(c, m)
            f = base64.b64decode(i)
            i = binascii.hexlify(f)
            return six.ensure_str(i)

        def pdecode(i, f):
            y = binascii.unhexlify(i)
            b = base64.b64encode(y)
            k = jscrypto.decode(b, f)
            return k

        headers = control.mozhdr
        refurl = urllib_parse.urljoin(referer, '/')
        pref = urllib_parse.urljoin(eurl, '/')
        headers.update({'Referer': refurl})
        epage = client.request(eurl, headers=headers)
        if isinstance(epage, six.binary_type) and six.PY3:
            epage = epage.decode('latin-1')

        try:
            idfile_enc = re.findall(r'''idfile_enc\s*=\s*["']([^"']+)''', epage)[0]
            iduser_enc = re.findall(r'''idUser_enc\s*=\s*["']([^"']+)''', epage)[0]
            dev_play = re.findall(r'''DEV_PLAY\s*=\s*["']([^"']*)''', epage)[0]
            apiurl = re.findall(r'''DOMAIN_API\s*=\s*["']([^"']+)''', epage)[0]

            idfile_dec = pdecode(idfile_enc, 'jcLycoRJT6OWjoWspgLMOZwS3aSS0lEn')
            iduser_dec = pdecode(iduser_enc, 'PZZ3J3LDbLT0GY7qSA5wW5vchqgpO36O')

            pdata = {
                "idfile": idfile_dec,
                "iduser": iduser_dec,
                "domain_play": "https://my.playhq.net" if dev_play == "thang" else refurl[:-1],
                "platform": "Win32",
                "hlsSupport": True
            }
            z = pencode(json.dumps(pdata), 'vlVbUQhkOhoSfyteyzGeeDzU0BHoeTyZ')
            w = binascii.hexlify(hashlib.md5(six.ensure_binary(z + 'KRWN3AdgmxEMcd2vLN1ju9qKe8Feco5h')).digest())
            data = {'data': z + '|' + six.ensure_str(w)}
            headers.update({'Referer': pref, 'Origin': pref[:-1]})
            jd = json.loads(client.request(apiurl + '/playiframe', headers=headers, post=data))
            mfile = pdecode(jd.get('data'), 'oJwmvmVBajMaRCTklxbfjavpQO7SZpsL')
            return 'Playallu', mfile + '|' + urllib_parse.urlencode(headers)
        except:
            return None, None

    @staticmethod
    def b64decode(text):
        return six.ensure_str(base64.b64decode(text))

    @staticmethod
    def b64encode(text):
        return six.ensure_str(base64.b64encode(six.b(text)))
