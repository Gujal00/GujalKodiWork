from kodi_six import xbmcvfs
from resources.lib import control


class DB_Connection():

    def __init__(self, metacache):
        """
        Initialize SQLITE DB
        """
        from sqlite3 import dbapi2 as new_database
        self.metacache = metacache
        self.database = new_database
        self.dbcon = self.database.connect(metacache)
        self.dbcon.row_factory = self.database.Row  # return results indexed by field names and not numbers so we can convert to dict
        self.dbcur = self.dbcon.cursor()

        # initialize cache db
        self.__create_cache_db()

    def __del__(self):
        ''' Cleanup db when object destroyed '''
        try:
            self.dbcur.close()
            self.dbcon.close()
        except:
            pass

    def __create_cache_db(self):
        ''' Creates the cache tables if they do not exist.  '''

        # Create Movie table
        sql_create = "CREATE TABLE IF NOT EXISTS meta ("\
                     "tmdb_id INTEGER, "\
                     "title TEXT, "\
                     "year INTEGER,"\
                     "meta BINARY, "\
                     "UNIQUE(tmdb_id)"\
                     ");"

        self.dbcur.execute(sql_create)
        self.dbcur.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_tmdb on "meta" (tmdb_id ASC )')
        control.log('Table meta initialized')

        # Create Configuration table
        sql_create = "CREATE TABLE IF NOT EXISTS config ("\
                     "setting TEXT, "\
                     "value TEXT, "\
                     "UNIQUE(setting)"\
                     ");"

        self.dbcur.execute(sql_create)
        self.dbcur.connection.commit()
        control.log('Table config initialized')

    def select_single(self, query):
        try:
            self.dbcur.execute(query)
            return self.dbcur.fetchone()
        except Exception as e:
            control.log('************* Error selecting from cache table: %s ' % e, 'error')
            pass

    def select_all(self, query, parms=None):
        try:
            if parms:
                self.dbcur.execute(query, parms)
            else:
                self.dbcur.execute(query)
            return self.dbcur.fetchall()
        except Exception as e:
            control.log('************* Error selecting from cache table: %s ' % e, 'error')
            pass

    def insert(self, query, values):
        try:
            self.dbcur.execute(query, values)
            self.dbcon.commit()
        except Exception as e:
            control.log('************* Error inserting to cache table: %s ' % e, 'error')
            pass

    def commit(self, query):
        try:
            self.dbcur.execute(query)
            self.dbcon.commit()
        except Exception as e:
            control.log('************* Error committing to cache table: %s ' % e, 'error')
            pass

    def delete_cache_db(self):
        control.log("Deleting metacache database...")
        try:
            if xbmcvfs.exists(self.metacache):
                self.__del__()
                xbmcvfs.delete(self.metacache)
            return True
        except Exception as e:
            control.log('Failed to delete cache DB: %s' % e, 'error')
            return False
