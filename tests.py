import unittest
import time

from flask.ext.stats import stats_backend, BaseBackend, Stats
from flask import Flask
import mock


@stats_backend
class FakeTestingBackend(BaseBackend):

    name = 'fake-testing-backend'

    def __init__(self, config):
        self.timing = mock.Mock()


class TestStats(unittest.TestCase):

    def test_measure_context(self):
        app = Flask(__name__)
        app.config['STATS_BACKEND'] = FakeTestingBackend.name
        stats = Stats(app=app)
        stat_name = 'some_metric'
        with stats.measure_context(stat_name) as m:
            self.assertTrue(isinstance(m.backend, FakeTestingBackend))
            self.assertTrue(m.t0 > 0)
            self.assertEqual(stat_name, m.stat_name)
        self.assertEqual(1, stats.timing.call_count)
        self.assertEqual(stat_name, stats.timing.call_args[0][0])
        self.assertTrue(stats.timing.call_args[0][1] > 0)

    def test_measure_decorator(self):
        app = Flask(__name__)
        app.config['STATS_BACKEND'] = FakeTestingBackend.name
        stats = Stats(app=app)
        stat_name = 'some_metric'

        sleep_time = 0.1

        @stats.measure(stat_name)
        def measured_method():
            time.sleep(sleep_time)
        measured_method()
        self.assertEqual(1, stats.timing.call_count)
        self.assertEqual(stat_name, stats.timing.call_args[0][0])
        self.assertTrue(stats.timing.call_args[0][1] >= sleep_time * 1000)


class TestStatsDBackend(unittest.TestCase):

    @mock.patch('statsd.StatsClient.gauge')
    def test_gauge(self, statsd_mock):
        app = Flask(__name__)

        rate = 35

        app.config['STATS_BACKEND'] = 'statsd'
        app.config['STATS_RATE'] = rate

        stats = Stats(app=app)
        stat_name = 'statsd_xx'
        stat_value = 20
        stats_delta = False

        stats.gauge(stat_name, stat_value)
        statsd_mock.assert_called_once_with(stat_name, stat_value, rate, stats_delta)

    @mock.patch('statsd.StatsClient.incr')
    def test_incr(self, statsd_mock):
        app = Flask(__name__)

        rate = 35

        app.config['STATS_BACKEND'] = 'statsd'
        app.config['STATS_RATE'] = rate

        stats = Stats(app=app)
        stat_name = 'statsd_xx'
        stat_value = 20

        stats.incr(stat_name, stat_value)
        statsd_mock.assert_called_once_with(stat_name, stat_value, rate)

    @mock.patch('statsd.StatsClient.decr')
    def test_decr(self, statsd_mock):
        app = Flask(__name__)

        rate = 35

        app.config['STATS_BACKEND'] = 'statsd'
        app.config['STATS_RATE'] = rate

        stats = Stats(app=app)
        stat_name = 'statsd_xx'
        stat_value = 20

        stats.decr(stat_name, stat_value)
        statsd_mock.assert_called_once_with(stat_name, stat_value, rate)

    @mock.patch('statsd.StatsClient.timing')
    def test_timing(self, statsd_mock):
        app = Flask(__name__)

        rate = 35

        app.config['STATS_BACKEND'] = 'statsd'
        app.config['STATS_RATE'] = rate

        stats = Stats(app=app)
        stat_name = 'statsd_xx'
        stat_value = 20

        stats.timing(stat_name, stat_value)
        statsd_mock.assert_called_once_with(stat_name, stat_value, rate)
