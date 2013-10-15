import time
import functools
from statsd import StatsClient


BACKENDS = {}


class Stats(object):
    """
        Flask extension for measuring stats, using different backends
    """
    def __init__(self, app=None, config=None):
        self.config = None
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def __getattr__(self, name):
        return getattr(self.backend, name)

    def init_app(self, app, config=None):
        self.config = self.config or config or app.config
        self.app = app

        self.config.setdefault('STATS_BACKEND', 'statsd')
        self.config.setdefault('STATS_RATE', 1)

        self.backend = BACKENDS[self.config['STATS_BACKEND'].upper()](self.config)

    def measure(self, stat_name):
        """
            Decorator used to measure methods. It should be used as:
            >>>@stats.measure('metric_name')
            >>>def my_method():
            >>>    do_something()
        """
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                with self.measure_context(stat_name):
                    return fn(*args, **kwargs)
            return wrapper
        return decorator

    def measure_context(self, stat_name):
        """
            Context manager for measuring.
            >>>with stats.measure_context('metric_name'):
            >>>    do_something()
        """
        return Measurer(self.backend, stat_name)


def stats_backend(cls):
    BACKENDS[cls.name.upper()] = cls
    return cls


class BaseBackend(object):

    name = None

    def timing(self, stat_name, delta):
        raise NotImplementedError

    def incr(self, stat_name, count=1):
        raise NotImplementedError

    def decr(self, stat_name, count=1):
        raise NotImplementedError

    def gauge(self, stat_name, value, delta=False):
        raise NotImplementedError


@stats_backend
class StatsDBackend(BaseBackend):

    name = 'statsd'

    def __init__(self, config):
        self.config = config
        self.config.setdefault('STATSD_HOST', 'localhost')
        self.config.setdefault('STATSD_PORT', 8125)
        self.config.setdefault('STATSD_PREFIX', None)

        self.statsd = StatsClient(self.config['STATSD_HOST'],
                                  self.config['STATSD_PORT'],
                                  self.config['STATSD_PREFIX'])

    def timing(self, stat_name, delta):
        return self.statsd.timing(stat_name, delta, self.config['STATS_RATE'])

    def incr(self, stat_name, count=1):
        return self.statsd.incr(stat_name, count, self.config['STATS_RATE'])

    def decr(self, stat_name, count=1):
        return self.statsd.decr(stat_name, count, self.config['STATS_RATE'])

    def gauge(self, stat_name, value, delta=False):
        return self.statsd.gauge(stat_name, value, self.config['STATS_RATE'], delta)


class Measurer(object):
    """
        Context manager for measuring times
    """

    def __init__(self, backend, stat_name):
        self.backend = backend
        self.stat_name = stat_name

    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, type, value, traceback):
        delta = (time.time() - self.t0) * 1000
        self.backend.timing(self.stat_name, delta)
