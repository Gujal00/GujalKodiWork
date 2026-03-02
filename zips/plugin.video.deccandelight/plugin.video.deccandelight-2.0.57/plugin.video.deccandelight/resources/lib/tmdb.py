import json
import pickle
import time

from six.moves import urllib_parse
from resources.lib import access, client, control, db_utils


class TMDB(object):
    '''
    This class performs TMDB lookups.
    '''

    def __init__(self, tmdb_api_key=access.tk, lang='en'):
        # Class variables
        self.lang = lang
        self.tmdb_api_key = tmdb_api_key
        self.tmdb_image_url = ''
        self.path = control._ppath
        self.metacache = control.TRANSLATEPATH(self.path + 'metacache.db')
        self.url_prefix = 'http://api.themoviedb.org/3'

        # Initialize DB
        self.DB = db_utils.DB_Connection(self.metacache)

        # Check TMDB configuration, update if necessary
        self._set_tmdb_config()

    def _get_config(self, setting):
        '''
        Query local Config table for values
        '''

        # Query local table first for current values
        sql_select = "SELECT * FROM config where setting = '%s'" % setting

        control.log('Looking up in local cache for config data: %s' % setting)
        control.log('SQL Select: %s' % sql_select)

        try:
            matchedrow = self.DB.select_single(sql_select)
        except Exception as e:
            control.log('************* Error selecting from cache db: %s' % e, 'error')
            return None

        if matchedrow:
            control.log('Found config data in cache table for setting: %s value: %s' % (setting, dict(matchedrow)))
            return dict(matchedrow)['value']
        else:
            control.log('No match in local DB for config setting: %s' % setting)
            return None

    def _set_config(self, setting, value):
        '''
        Set local Config table for values
        '''
        sql_insert = "REPLACE INTO config (setting, value) VALUES(%s,%s)"
        sql_insert = 'INSERT OR ' + sql_insert.replace('%s', '?')

        control.log('Updating local cache for config data: %s value: %s' % (setting, value))
        control.log('SQL Insert: %s' % sql_insert)

        values = (setting, value)
        self.DB.insert(sql_insert, values)

    def _set_tmdb_config(self):
        '''
        Query config database for required TMDB config values, set constants as needed
        Validate cache timestamp to ensure it is only refreshed once every 7 days
        '''

        control.log('Looking up TMDB config cache values')
        tmdb_image_url = self._get_config('tmdb_image_url')
        tmdb_config_timestamp = self._get_config('tmdb_config_timestamp')

        # Grab current time in seconds
        now = time.time()
        age = 0

        # Cache limit is 7 days, value needs to be in seconds: 60 seconds * 60 minutes * 24 hours * 7 days
        expire = 60 * 60 * 24 * 7

        # Check if image and timestamp values are valid
        if tmdb_image_url and tmdb_config_timestamp:
            created = float(tmdb_config_timestamp)
            age = now - created
            control.log('Cache age: %s , Expire: %s' % (age, expire))

            # If cache hasn't expired, set constant values
            if age <= float(expire):
                control.log('Cache still valid, setting values')
                control.log('Setting tmdb_image_url: %s' % tmdb_image_url)
                self.tmdb_image_url = tmdb_image_url
            else:
                control.log('Cache is too old, need to request new values')

        # Either we don't have the values or the cache has expired, so lets request and set them - update cache in the end
        if (not tmdb_image_url or not tmdb_config_timestamp) or age > expire:
            control.log('No cached config data found or cache expired, requesting from TMDB')

            # tmdb = TMDB(tmdb_api_key=self.tmdb_api_key, lang='en')
            config_data = self.call_config()

            if config_data:
                self.tmdb_image_url = config_data['images']['base_url']
                self._set_config('tmdb_image_url', config_data['images']['base_url'])
                self._set_config('tmdb_config_timestamp', now)
            else:
                self.tmdb_image_url = tmdb_image_url

    def _cache_lookup_by_name(self, name, year=''):
        '''
        Lookup in SQL DB for video meta data by name and year

        Args:
            name (str): full name of movie/tvshow you are searching
        Kwargs:
            year (str): 4 digit year of video, recommended to include the year whenever possible
                        to maximize correct search results.

        Returns:
            DICT of matched meta data or None if no match.
        '''

        name = control.clean_string(name.lower())
        sql_select = "SELECT * FROM meta WHERE title = '%s'" % name
        control.log('Looking up in local cache by name for: %s %s' % (name, year))

        if year:
            sql_select = sql_select + " AND year = %s" % year
        control.log('SQL Select: %s' % sql_select)

        try:
            matchedrow = self.DB.select_single(sql_select)
        except Exception as e:
            control.log('************* Error selecting from cache db: %s' % e, 'error')
            return None

        if matchedrow:
            control.log('Found meta information by name in cache table: %s' % dict(matchedrow))
            return dict(matchedrow)
        else:
            control.log('No match in local DB')
            return None

    def _cache_save_video_meta(self, meta, name):
        '''
        Saves meta data to SQL table given type

        Args:
            meta_group (dict): meta data of video to be added to database
        '''
        # strip title
        title = control.clean_string(name.lower())

        control.log('Saving cache information: %s' % meta)

        sql_insert = 'INSERT INTO meta ' \
                     'VALUES' \
                     '(?, ?, ?, ?)'
        values = (int(meta['tmdb_id']), title, meta['year'], pickle.dumps(meta))

        # Commit all transactions
        self.DB.insert(sql_insert, values)
        control.log('SQL INSERT Successfully Commited')

    def __clean_name(self, mystring):
        newstring = ''
        for word in mystring.split(' '):
            if word.isalnum() is False:
                w = ""
                for i in range(len(word)):
                    if word[i].isalnum():
                        w += word[i]
                word = w
            newstring += ' ' + word
        return newstring.strip()

    def _do_request(self, method, values):
        '''
        Request JSON data from TMDB

        Args:
            method (str): Type of TMDB request to make
            values (str): Value to use in TMDB lookup request

        Returns:
            DICT of meta data found on TMDB
            Returns None when not found or error requesting page
        '''
        url = "%s/%s?language=%s&api_key=%s&%s" % (self.url_prefix, method, self.lang, self.tmdb_api_key, values)
        try:
            meta = json.loads(client.request(url, headers={"Accept": "application/json"}))
        except Exception as e:
            control.log(e)
            return None

        if meta == 'Nothing found.':
            return None
        else:
            return meta

    def call_config(self):
        '''
        Query TMDB config api for current values
        '''
        return self._do_request('configuration', '')

    def _get_info(self, tmdb_id, media_type, values='', q=False):
        ''' Helper method to start a TMDB getInfo request '''
        r = self._do_request('{0}/{1}'.format(media_type, tmdb_id), values)
        if q:
            q.put(r)
        return r

    def _search(self, name, year=''):
        ''' Helper method to start a TMDB Movie.search request - search by Name/Year '''
        name = urllib_parse.quote(self.__clean_name(name))
        if year:
            name = name + '&year=' + year
        return self._do_request('search/multi', 'query=' + name)

    def tmdb_lookup(self, name, year=''):
        '''
        Main callable method which initiates the TMDB/IMDB meta data lookup

        Returns a final dict of meta data

        Args:
            name (str): full name of movie you are searching
        Kwargs:
            tmdb_id (str): TMDB ID
            year (str): 4 digit year of video, recommended to include the year whenever possible
                        to maximize correct search results.

        Returns:
            DICT of meta data
        '''
        md = {}
        tmdb_id = ''

        meta = self._search(name, year)
        if meta and meta['total_results'] == 1 and meta['results']:
            tmdb_id = meta['results'][0].get('id')
            media_type = meta['results'][0].get('media_type')
        elif meta and meta['total_results'] > 1 and meta['results']:
            results = [r for r in meta.get('results')
                       if (r.get('title')
                           and control.clean_string(r.get('title').lower()) == control.clean_string(name.lower()))
                       and r.get('release_date', '0000')[:4] == year]
            if len(results) > 1:
                fresults = [r for r in results if r.get('original_language') != 'en']
                if len(fresults) > 0:
                    tmdb_id = fresults[0].get('id')
                    media_type = fresults[0].get('media_type')
                else:
                    tmdb_id = results[0].get('id')
                    media_type = results[0].get('media_type')
            elif len(results) == 1:
                tmdb_id = results[0].get('id')
                media_type = results[0].get('media_type')

        if tmdb_id:
            # Attempt to grab all info in one request
            meta = self._get_info(tmdb_id, media_type, 'append_to_response=casts,trailers')
            if meta is not None:
                # Parse out extra info from request
                md.update({
                    'tmdb_id': str(meta['id']),
                    'title': meta.get('title'),
                    'tagline': meta.get('tagline'),
                    'mediatype': media_type,
                    'plot': meta.get('overview'),
                    'country': [x.get('name') for x in meta.get('production_countries')],
                    'studio': [x.get('name') for x in meta.get('production_companies')],
                    'rating': meta.get('vote_average'),
                    'votes': meta.get('vote_count'),
                    'premiered': meta.get('release_date'),
                })

                if meta.get('imdb_id'):
                    md.update({'imdb_id': meta.get('imdb_id')})
                if meta.get('release_date'):
                    md.update({'year': int(meta.get('release_date')[:4])})
                else:
                    md.update({'year': 0})
                if meta.get('runtime'):
                    md.update({'duration': meta.get('runtime') * 60})

                cast = meta.get('casts')
                if cast:
                    if cast.get('cast'):
                        castandrole = [(x.get('name'), x.get('character')) for x in cast['cast']]
                        cast2 = [{'name': x.get('name'),
                                  'role': x.get('character'),
                                  'thumbnail': '{0}w138_and_h175_face{1}'.format(self.tmdb_image_url, x.get('profile_path'))}
                                 for x in cast['cast']]
                        md.update({'castandrole': castandrole[:10],
                                   'cast2': cast2[:10]})
                    if cast.get('crew'):
                        director = [x.get('name') for x in cast['crew'] if x.get('job') == 'Director']
                        writer = list(set([x.get('name') for x in cast['crew'] if x.get('job') in ['Story', 'Screenplay', 'Dialogue', 'Writing']]))
                        md.update({'director': director,
                                   'writer': writer})

                genres = meta.get('genres')
                if genres:
                    genre = [x.get('name') for x in genres]
                    md.update({'genre': genre})

                trailers = meta.get('trailers')
                if trailers:
                    # We only want youtube trailers
                    trailers = trailers['youtube']

                    # Only want trailers - no Featurettes etc.
                    found_trailer = next((item for item in trailers if 'Trailer' in item["name"] and item['type'] == 'Trailer'), None)
                    if found_trailer:
                        trailer_id = found_trailer['source']
                        md.update({'trailer': 'plugin://plugin.video.youtube/play/?video_id=%s' % trailer_id})

                art = {}
                if meta.get('poster_path'):
                    art.update({'poster': '{0}w500{1}'.format(self.tmdb_image_url, meta['poster_path'])})
                if meta.get('backdrop_path'):
                    art.update({'fanart': '{0}w1280{1}'.format(self.tmdb_image_url, meta['backdrop_path'])})

                if art:
                    md.update({'art': art})

        return md

    def get_meta(self, name, year=''):
        '''
        Main method to get meta data for movie or tvshow. Will lookup by name/year.

        Args:
            name (str): full name of movie/tvshow you are searching
        Kwargs:
            year (str): 4 digit year of video, recommended to include the year whenever possible
                        to maximize correct search results.

        Returns:
            DICT of meta data or None if cannot be found.
        '''

        control.log('---------------------------------------------------------------------------------------')
        control.log('Attempting to retrieve meta data for %s %s' % (name, year))

        # First check cache for saved entry
        dbmeta = self._cache_lookup_by_name(name, year)
        if dbmeta:
            return pickle.loads(dbmeta.get('meta'))
        else:
            # If meta not found in cache lookup thru online service
            meta = self.tmdb_lookup(name, year)
            if meta:
                self._cache_save_video_meta(meta, name)

        return meta

    def clear_meta(self):
        res = self.DB.delete_cache_db()
        if res:
            msg = 'Cached Metadata has been cleared'
            control.notify(msg)
