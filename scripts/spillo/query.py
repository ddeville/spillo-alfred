import argparse, sys

class Query(object):
    class QueryException(Exception):
        pass

    QueryException = QueryException

    _value = None
    _name = None
    _url = None
    _tags = None
    _desc = None

    def __init__(self, query_string):
        # try to parse the arguments, if an exception is thrown it's because some args
        # are incomplete and we shouldn't return any result until they are
        try:
            specific = self._parse_query_string(query_string)
        except:
            raise Query.QueryException()

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def tags(self):
        return self._tags

    @property
    def desc(self):
        return self._desc

    def _parse_query_string(self, query_string):
        parser = _QueryParser()
        parser.add_argument('value', nargs='*')
        parser.add_argument('-n', '--name', nargs='+', dest='name')
        parser.add_argument('-u', '--url', nargs='+', dest='url')
        parser.add_argument('-d', '--desc', nargs='+', dest='desc')
        parser.add_argument('-t', '--tags', nargs='+', dest='tags')

        args = vars(parser.parse_args(query_string.split()))

        self._value = ' '.join(args['value']) if args['value'] else None
        self._name = ' '.join(args['name']) if args['name'] else None
        self._url = ' '.join(args['url']) if args['url'] else None
        self._desc = ' '.join(args['desc']) if args['desc'] else None
        self._tags = args['tags']

class _QueryParser(argparse.ArgumentParser):
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
