# -*- coding: utf-8 -*-
"""Provide an easy way to convert a function to a Command Line Interface.

There are two main methods in the one class provided (Cli):

    command - A decorator which converts a function to a CLI based
              on function signature
    run     - A method which parses the command line arguments and
              executes the appropriate function"""
import sys
import inspect
import argparse


class Cli(object):

    def __init__(self, description="", main=None, optionals=None):
        self.main = main
        self.optionals = optionals
        self.functions = {}
        self.parser = argparse.ArgumentParser(description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter)
        if self.main is None:
            self.subparsers = self.parser.add_subparsers()
        else:
            self.create_subparser(self.main)

    def create_subparser(self, fn):
        """collects information about decorated function, builds a
        subparser then returns the function unchanged"""
        name = fn.__name__
        self.functions[name] = fn

        desc = fn.__doc__
        args, _, __, defaults = inspect.getargspec(fn)

        args = [] if not args else args
        defaults = [] if not defaults else defaults

        if self.main is None:
            _parser = self.subparsers.add_parser(name, description=desc,
                formatter_class=argparse.RawDescriptionHelpFormatter)
            _parser.set_defaults(func=self.functions[name])
        else:
            _parser = self.parser
            _parser.set_defaults(func=self.main)

        positionals = args[:len(args) - len(defaults)]
        keywords = [x for x in zip(args[len(args) - len(defaults):], defaults)]

        for arg in positionals:
            if arg in self.optionals:
                _parser.add_argument(
                    arg, nargs='?', default=self.optionals[arg])
            else:
                _parser.add_argument(arg)

        for arg, default in keywords:
            # Try the lower case first letter for the short option first
            params = _parser._option_string_actions
            if '-{}'.format(arg[0]) not in params:
                flag = ('-{}'.format(arg[0]), '--{}'.format(arg))
            # Then the upper-case first letter for the short option
            elif '-{}'.format(arg[0]).upper() not in params:
                flag = ('-{}'.format(arg[0]).upper(), '--{}'.format(arg))
            # otherwise no short option
            else:
                flag = ('--{}'.format(arg))
            if isinstance(default, basestring):
                _parser.add_argument(*flag, type=str, default=default)
            elif isinstance(default, list):
                _parser.add_argument(*flag, nargs='+')
            elif isinstance(default, bool):
                if default:
                    _parser.add_argument(
                        *flag, action='store_false', default=default)
                else:
                    _parser.add_argument(
                        *flag, action='store_true', default=default)
            elif isinstance(default, int):
                _parser.add_argument(*flag, type=int, default=default)

    def command(self):
        def inner(fn):
            if self.main is not None:
                print "The Cli decorator cannot be used when main is specified"
                sys.exit(-1)
            self.create_subparser(fn)
            return fn
        return inner

    def run(self):
        args = self.parser.parse_args()
        func = args.func
        _args, _, __, defaults = inspect.getargspec(func)
        kwargs = {}
        for arg in _args:
            kwargs[arg] = getattr(args, arg)
        func(**kwargs)

