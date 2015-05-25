import argparse, sys

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
        parser = _QueryParser()
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
