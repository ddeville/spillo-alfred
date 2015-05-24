#!/usr/bin/env python

import argparse, getopt, os, sqlite3, sys

from xml.etree.ElementTree import (
    Element,
    SubElement,
    tostring,
)

from Foundation import (
    NSLibraryDirectory,
    NSSearchPathForDirectoriesInDomains,
    NSUserDomainMask,
)

class Query(object):

    class QueryException(Exception):
        pass

    QueryException = QueryException

    def __init__(self, query_string):
        self.value = None
        self.name = None
        self.url = None
        self.tags = None
        self.desc = None

        # try to parse the arguments, if an exception is thrown it's because some args
        # are incomplete and we shouldn't return any result until they are
        try:
            specific = self._parse_query_string(query_string)
        except:
            raise Query.QueryException()

    def _parse_query_string(self, query_string):
        parser = QueryParser()
        parser.add_argument('value', nargs='*')
        parser.add_argument('-n','--name', nargs='+', dest='name')
        parser.add_argument('-u','--url', nargs='+', dest='url')
        parser.add_argument('-d','--desc', nargs='+', dest='desc')
        parser.add_argument('-t','--tags', nargs='+', dest='tags')

        args = vars(parser.parse_args(query_string.split()))

        self.value = ' '.join(args['value']) if args['value'] else None
        self.name = ' '.join(args['name']) if args['name'] else None
        self.url = ' '.join(args['url']) if args['url'] else None
        self.desc = ' '.join(args['desc']) if args['desc'] else None
        self.tags = args['tags']

class QueryParser(argparse.ArgumentParser):
    def _get_action_from_name(self, name):
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        super(QueryParser, self).error(message)

class SpilloDatabase(object):
    def __init__(self):
        self.connection = sqlite3.connect(self._retrieve_database_path())

    def query(self, query):
        cursor = self.connection.cursor()
        if query.value:
            return self._query_general(cursor, query.value)
        else:
            return self._query_specific(cursor, query)

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

    def _query_general(self, cursor, query):
        params = {"t": '%'+query+'%'}
        cursor.execute('SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND (ZTITLE LIKE :t OR ZURL LIKE :t) ORDER BY ZDATE DESC', params)
        return cursor.fetchall()

    def _query_specific(self, cursor, query):
        queries = []
        params = {}
        if query.name:
            queries.append('SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND ZTITLE LIKE :t')
            params["t"] = '%'+query.name+'%'
        if query.url:
            queries.append('SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND ZURL LIKE :u')
            params["u"] = '%'+query.url+'%'
        if query.desc:
            queries.append('SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE ZDELETING=0 AND ZDESC LIKE :d')
            params["d"] = '%'+query.desc+'%'
        if query.tags:
            tag_queries = []
            for tag in query.tags:
                tag_queries.append('SELECT ZTITLE, ZURL, ZIDENTIFIER, ZDATE FROM ZPINBOARDPOST WHERE Z_PK IN (SELECT Z_2POSTS FROM Z_2TAGS WHERE Z_3TAGS IN  (SELECT Z_PK FROM ZPINBOARDTAG WHERE ZTITLE == \"'+tag+'\"))')
            queries.append(' INTERSECT '.join(tag_queries))

        sql = ' INTERSECT '.join(queries) + ' ORDER BY ZDATE DESC'
        cursor.execute(sql, params)
        return cursor.fetchall()

class Emitter(object):
    def generate_empty(self):
        return ""

    def generate_output(self, results):
        return ""

    def generate_error(self, error):
        return ""

class AlfredEmitter(Emitter):
    def generate_empty(self):
        return self.generate_output([])

    def generate_output(self, results):
        items_element = Element('items')

        if not results:
            item_element = SubElement(items_element, 'item', {'valid':'NO'})

            title_element = SubElement(item_element, 'title')
            title_element.text = 'No Results'

            subtitle_element = SubElement(item_element, 'subtitle')
            subtitle_element.text = 'Could not find any bookmark matching your search query'
        else:
            for result in results:
                title = result[0]
                url = result[1]
                identifier = result[2]

                item_element = SubElement(items_element, 'item', {'arg':url, 'uid':identifier})

                title_element = SubElement(item_element, 'title')
                title_element.text = title

                subtitle_element = SubElement(item_element, 'subtitle')
                subtitle_element.text = url

                subtitle_alt_element = SubElement(item_element, 'subtitle', {'mod':'cmd'})
                subtitle_alt_element.text = 'Open bookmark in Spillo'

                subtitle_alt_element = SubElement(item_element, 'subtitle', {'mod':'alt'})
                subtitle_alt_element.text = 'Open URL in the background'

                icon_element = SubElement(item_element, 'icon')
                icon_element.text = 'document.png'

                copy_element = SubElement(item_element, 'text', {'type':'copy'})
                copy_element.text = url

                largetype_element = SubElement(item_element, 'text', {'type':'largetype'})
                largetype_element.text = title

        return tostring(items_element)

    def generate_error(self, error):
        items_element = Element('items')

        item_element = SubElement(items_element, 'item', {'valid':'NO'})

        title_element = SubElement(item_element, 'title')
        title_element.text = 'There was an error while querying Spillo'

        subtitle_element = SubElement(item_element, 'subtitle')
        subtitle_element.text = error

        return tostring(items_element)

def _parse_arguments(argv):
    """Parse the command line arguments and returns the query"""
    usage = 'spillo.py -s <service> -q <query>'

    try:
        opts, args = getopt.getopt(argv, 's:q:', ['service=', 'query='])
    except getopt.GetoptError:
        raise RuntimeError(usage)

    query = None
    service = None

    for opt, arg in opts:
        if opt in ('-s', '--service'):
            service = arg
        elif opt in ('-q', '--query'):
            query = arg

    if service is None or query is None:
        raise RuntimeError(usage)

    return (service, query)

def main(argv):
    def _emit(output):
        sys.stdout.write(output + '\n')

    def _emit_message_and_exit(message, exit_code=1):
        _emit(message)
        sys.exit(exit_code)

    # attempt to parse the command line arguments
    try:
        (s, q) = _parse_arguments(argv)
    except RuntimeError as e:
        _emit_message_and_exit(str(e))

    # get the right emitter based on the service
    if s == 'alfred':
        emitter = AlfredEmitter()
    else:
        _emit_message_and_exit('unknown service ' + s)

    # parse the query and emit an empty response if there is none
    try:
        query = Query(q)
    except Query.QueryException:
        _emit_message_and_exit(emitter.generate_empty(), 0)

    # create a database, query it and generate some output via the emitter
    try:
        database = SpilloDatabase()
        output = emitter.generate_output(database.query(query))
    except IOError:
        output = emitter.generate_error('Cannot find Spillo database, make sure that Spillo is installed')
    except sqlite3.OperationalError:
        output = emitter.generate_error('There was an unknown error while querying the database')

    _emit(output)

if __name__ == "__main__":
    main(sys.argv[1:])
