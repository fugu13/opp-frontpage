
"""
    glashammer.utils.testing
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Helpers for unit testing Glashammer applications

    :copyright: 2008-2009 Glashammer Developers
    :license: MIT

    This module is presented as a py.test plugin. It provides two main features:

        1. Provide a method to extract Application unit tests from declarative
           Yaml files, and
        2. Provide an easily usable temporary application instance, for standard unit
           tests.

    How it works
    ------------

    py.test has a number of hooks that can be accessed to extend its
    behaviour. This plugin uses the `pytest_collect_file` hook which is called
    wih every file available in the test target. The first action of the
    hook-handler is that it checks if the filename is of the form `test*.yml`,
    thus ignoring other Yaml files used for configuration etc.

    If it finds an appropriate file, the hook-handler will generate a number
    of tests based on that file. py.test provides a hierarchical system of
    tests. The top-level of this hierarchy is an object representing the Yaml
    file itself. The lower components are represented by further test
    containers, and subsequent individual tests.

    In order to describe the test hierarchy created, we must first take a look
    at an example declaration of a single Yaml file::

        test_index:
            path: /
            assert_status: 200

        test_new:
            - path: /new
              assert_status: 200
            - path: /new
              method: POST
              data:
                text: newpage
              assert_status: 302

    The file contains two use-cases, the first `test_index` with a single
    target, and the second `test_new` with two targets. Each target contains a
    single assert. This hierarchy is reflected in the structure of the test
    hierarchy created for py.test:

    - YamlTestFile

      - UsecaseTestItem

       - TargetTestItem

         - ConstraintTest

    Each component of the test hierarchy should be a subclass of
    :class:`py.test.collect.Item`, which is either a direct subclass, for leaf
    tests, implementing `runtest()` or a :class:`py.test.collect.File` which
    implements `collect()` and returns a list of items. In this hierarchy,
    only the :class:`ConstraintTest` is an actual leaf test, and each one
    represesents a single `assert_` in the Yaml declaration. In our example
    above that is `assert_status` which asserts that the response status code
    is the numerical value given.

    This hierarchy may seem overly complicated, but it is specifically
    designed to accomodate the sharing of the various tested components. Each
    UsecaseTestItem in a YamlTestFile has it's own
    :class:`glashammer.application.GlashammerApplication` instance, which each
    of the TargetTestItem share. This is important to note in that there is
    persistence between the individual targets within a UsecaseTestItem.
    Because of this it allows sequential testing of targets, rather than just
    single isolated tests. The TargetTestItem has any number of
    ConstraintTest, one for each `assert_` key in the target configuration.
    Each of these map to a single test, which share the response of the
    TargetTestItem's path. This way, multiple tests are generated against the
    single response.

    So, within a UsecaseTestItem each TargetTestItem shares the same
    `GlashammerApplication`, and within a TargetTestItem, each ConstraintTest
    shares the same Response. It is important to keep this in mind when
    writing tests. If a test needs a fresh Application, it should probably be
    in a different UsecaseTestItem.
"""

import os, urllib, urlparse

import yaml

from py.test.collect import File, Collector, Item

from werkzeug.test import Client
from werkzeug.utils import import_string

from glashammer.utils import Response
from glashammer.application import make_app, declare_app


def pytest_funcarg__tmpapp(request):
    """tmpapp Funcarg for py.test

    This funcarg is a factory, that when called with an optional Glashammer
    application setup callable, creates a Glashammer Application instance that
    is bound to py.test's temporary directory.

    Additionally, once tmpapp has been called to create the application, the
    application itself, and the funcarg each have one additional attribute:
    `client` that is a :class:`werkzeug.test.Client` instance bound to the
    application.

    The tmpapp itself is an instance of
    :class:`~glashammer.utils.testing.AppTestingFactory`.
    """
    return AppTestingFactory(request)


def pytest_collect_file(path, parent):
    """Collection hook for py.test

    This collection hook looks for Yaml files which may contain tests. The
    files themselves must be of the glob: `test*.yml`. Once discovered the
    test files are collected into a multiple hierarchy of
    :class:`py.test.collect.Item` which is described in detail in the module
    documentation.
    """
    if str(path.basename).startswith('test') and path.ext == '.yml':
        return YamlTestFile(path, parent=parent)


class AppTestingFactory(object):

    def __init__(self, request):
        self.request = request
        self.tmpdir = request.getfuncargvalue('tmpdir')

    def __call__(self, setup=None):
        if setup is None:
            setup = lambda(app): None
        app = make_app(setup, str(self.tmpdir))
        app.client = self.client = Client(app)
        return app


class YamlTestFile(File):
    """Custom Container for yaml-based files.
    """

    def __init__(self, path, parent):
        super(YamlTestFile, self).__init__(path, parent=parent)

    def collect(self):
        raw = yaml.load(self.fspath.open())
        tests = []
        app_factory = raw.get('__app_factory__')
        if app_factory is None:
            app_file = raw.get('__app_file__') or 'app.yml'
            app_file = _find_app_file(app_file, self.fspath)
            app_factory = lambda: declare_app(app_file)
        else:
            app_factory = import_string(app_factory)
        for name, value in raw.items():
            if not name.lower().startswith('test'):
                continue
            tests.append(UsecaseTestItem(name, parent=self,
                         sequence=value, app_factory=app_factory))
        return tests


class UsecaseTestItem(Collector):
    """Custom container representing a single set of paths to test
    """
    def __init__(self, name, parent, sequence, app_factory):
        super(UsecaseTestItem, self).__init__(name, parent=parent)
        self.app = app_factory()
        self.sequence = sequence

    def _collect_target(self, tests, target, app, name):
        tests.append(TargetTestItem(parent=self,
            target=target, app=app, name=name))

    def collect(self):
        tests = []
        if isinstance(self.sequence, list):
            for target in self.sequence:
                self._collect_target(tests, target, self.app, self.name)
        else:
            self._collect_target(tests, self.sequence, self.app, self.name)
        return tests


class TargetTestItem(Collector):
    """Custom container for a single path target in the test application.
    """

    def __init__(self, parent, target, app, name):
        self.target = target
        self.request_args = dict(i for i in target.items() if not
                                 i[0].startswith('assert_'))
        super(TargetTestItem, self).__init__(name, parent=parent)
        self.app = app
        self.response = self._get_response()

    def _get_response(self):
        client = Client(self.app, response_wrapper=Response)
        return client.open(**self.request_args)

    def collect(self):
        tests = []
        # Now run the tests
        for k in self.target:
            if k.startswith('assert_'):
                tests.append(constraints_tests[k](self))
        return tests


class ConstraintTest(Item):
    """Abstract representing a single testable assertion on the response.
    """
    constraint_name = None

    def __init__(self, parent):
        self.full_path = _generate_full_path(parent.target)
        name = '%s %r %s' % (parent.name, self.full_path, self.constraint_name)
        super(ConstraintTest, self).__init__(name, parent)

    def runtest(self):
        return self.assert_response(self.parent.response)

    def assert_response(self, response):
        raise NotImplementedError()

    def reportinfo(self):
        return self.fspath, None, self.name


class StatusTestItem(ConstraintTest):

    constraint_name = 'assert_status'

    def assert_response(self, response):
        assert self.parent.target['assert_status'] == response.status_code


class ContainsTestItem(ConstraintTest):

    constraint_name = 'assert_contains'

    def assert_response(self, response):
        assert self.parent.target['assert_contains'] in response.data


class RedirectTestItem(ConstraintTest):

    constraint_name = 'assert_redirect'

    def assert_response(self, response):
        assert response.status_code in [301, 302, 303, 304]
        path =  urlparse.urlparse(response.location).path
        assert path == self.parent.target['assert_redirect']


constraints_tests = {
    'assert_status': StatusTestItem,
    'assert_redirect': RedirectTestItem,
    'assert_contains': ContainsTestItem,
}


def _find_app_file(path, testpath):
    if os.path.isabs(path):
        app_file = path
    else:
        app_file = str(testpath.dirpath().join(path))
        if not os.path.exists(app_file):
            app_file = str(testpath.dirpath().dirname().join(path))
    if not os.path.exists(app_file):
        raise ValueError('Application file %r not found' % app_file)
    return app_file


def _generate_full_path(target):
    path = target.get('path')
    query_string = target.get('query_string')
    if query_string:
        if isinstance(query_string, dict):
            extra = urllib.urlencode(query_string)
        else:
            extra = query_string
        full_path = '%s?%s' % (path, extra)
    else:
        full_path = path
    return full_path

