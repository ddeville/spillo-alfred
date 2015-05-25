import os, sqlite3

from query import Query
from bookmark import Bookmark

from Foundation import (
    NSLibraryDirectory,
    NSSearchPathForDirectoriesInDomains,
    NSUserDomainMask,
)

class Database(object):
    class DatabaseException(Exception):
        pass

    DatabaseException = DatabaseException

    def __init__(self):
        self.connection = sqlite3.connect(self._retrieve_database_path())

    def query(self, query):
        try:
            cursor = self.connection.cursor()
            if query.value:
                return self._query_general(cursor, query.value)
            else:
                return self._query_specific(cursor, query)
        except sqlite3.OperationalError:
            raise Database.DatabaseException('There was an unknown error while querying the database')

    def _retrieve_database_path(self):
        path = NSSearchPathForDirectoriesInDomains(NSLibraryDirectory, NSUserDomainMask, True).firstObject()
        path = os.path.join(path,
            'Group Containers',
            'Q8B696Y8U4.com.ddeville.spillo',
            'Library',
            'Application Support',
            'Stores',
            'Pinboard',
            'Pinboard.sqlite'
        )
        # attempt to open the file so that we throw if it doesn't exist
        with open(path) as f:
            pass
        return path

    # the name is like the search term
    NAME_QUERY = 'SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND ZTITLE LIKE ? COLLATE NOCASE'
    # the url is like the search term
    URL_QUERY = 'SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND ZURL LIKE ? COLLATE NOCASE'
    # the desc is like the search term
    DESC_QUERY = 'SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND ZDESC LIKE ? COLLATE NOCASE'
    # the tag is exactly the search term
    TAG_QUERY = 'SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND Z_PK IN (SELECT Z_2POSTS FROM Z_2TAGS WHERE Z_3TAGS == (SELECT Z_PK FROM ZPINBOARDTAG WHERE ZTITLE == ? COLLATE NOCASE))'
    # the name or url or desc is like the search term or the tag is exactly the search term
    FULL_QUERY = 'SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND (ZTITLE LIKE ? OR ZURL LIKE ? OR ZDESC LIKE ? OR Z_PK IN (SELECT Z_2POSTS FROM Z_2TAGS WHERE Z_3TAGS == (SELECT Z_PK FROM ZPINBOARDTAG WHERE ZTITLE == ? COLLATE NOCASE))) COLLATE NOCASE'

    def _query_general(self, cursor, query):
        # construct a LIKE search for each word in the query and intersect the queries
        queries = []
        params = []
        for word in query.split():
            queries.append(Database.FULL_QUERY)
            params.append('%'+word+'%') # name
            params.append('%'+word+'%') # url
            params.append('%'+word+'%') # desc
            params.append(word)         # tag
        sql = ' INTERSECT '.join(queries) + ' ORDER BY ZDATE DESC'
        cursor.execute(sql, params)
        return self._generate_bookmarks(cursor)

    def _query_specific(self, cursor, query):
        queries = []
        params = []
        if query.name:
            queries.append(Database.NAME_QUERY)
            params.append('%'+query.name+'%')
        if query.url:
            queries.append(Database.URL_QUERY)
            params.append('%'+query.url+'%')
        if query.desc:
            queries.append(Database.DESC_QUERY)
            params.append('%'+query.desc+'%')
        if query.tags:
            # construct an intersection of queries for each tag
            tag_queries = []
            for tag in query.tags:
                tag_queries.append(Database.TAG_QUERY)
                params.append(tag)
            queries.append(' INTERSECT '.join(tag_queries))

        sql = ' INTERSECT '.join(queries) + ' ORDER BY ZDATE DESC'
        cursor.execute(sql, params)
        return self._generate_bookmarks(cursor)

    def _generate_bookmarks(self, cursor):
        bookmarks = []
        for row in cursor:
            bookmarks.append(Bookmark(title=row[0], url=row[1], identifier=row[2], date=row[3]))
        return bookmarks
