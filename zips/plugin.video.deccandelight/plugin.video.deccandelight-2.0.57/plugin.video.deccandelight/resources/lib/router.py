"""
    Deccan Delight Kodi Addon
    Copyright (C) 2016 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from six.moves import urllib_parse


def routing(paramstring):
    # """
    # Router function that calls other functions
    # depending on the provided paramstring

    # :param paramstring:
    # Action Definitions:
    # 1 : List Site
    # 4 : List Top Menu (Channels, Languages)
    # 5 : List Secondary Menu (Shows, Categories)
    # 6 : List Third Menu
    # 7 : List Individual Items (Movies, Episodes)
    # 8 : List Playable Videos
    # 9 : Play Video
    # """
    # # Parse a URL-encoded paramstring to the dictionary of
    # # {<parameter>: <value>} elements
    # params = dict(urllib_parse.parse_qsl(paramstring))
    # # Check the parameters passed to the plugin

    params = dict(urllib_parse.parse_qsl(paramstring.replace('?', '')))
    # logger(f'routing params>>>> {params}')
    if params:
        action = params.get('action', '')
        if action == '0':
            from resources.lib.deccandelight import clear_cache
            clear_cache()
        elif action == '1':
            from resources.lib.deccandelight import list_menu
            list_menu(params['site'])
        elif action == '4':
            from resources.lib.deccandelight import list_top
            list_top(params['site'], params['iurl'])
        elif action == '5':
            from resources.lib.deccandelight import list_second
            list_second(params['site'], params['iurl'])
        elif action == '6':
            from resources.lib.deccandelight import list_third
            list_third(params['site'], params['iurl'])
        elif action == '7':
            from resources.lib.deccandelight import list_items
            list_items(params['site'], params['iurl'])
        elif action == '8':
            from resources.lib.deccandelight import list_videos
            list_videos(params['site'], params['title'], params['iurl'], params['thumb'])
        elif action == '9':
            from resources.lib.deccandelight import play_video
            play_video(params['iurl'])
        elif action == '10':
            from resources.lib.deccandelight import play_video
            play_video(params['iurl'], dl=True)
        elif action == '11':
            from resources.lib.tmdb import TMDB
            TMDB().clear_meta()
    else:
        from resources.lib.deccandelight import list_sites
        list_sites()
