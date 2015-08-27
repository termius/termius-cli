from mock import patch, Mock
from unittest import TestCase
from serverauditor_sshconfig.core.storage.query import Query


class QueryCase(TestCase):

    def setUp(self):
        self.sa = 'asd'
        self.first_mock = Mock(**{'wind': 'short', 'length': 42})
        self.second_mock = Mock(**{'wind': 'long', 'length': 0})

    def test_defaults(self):
        query = Query(wind='short')
        self.assertTrue(query(self.first_mock))
        self.assertFalse(query(self.second_mock))

    def test_eq_only_first(self):
        query = Query(**{'wind.eq': 'short'})
        self.assertTrue(query(self.first_mock))
        self.assertFalse(query(self.second_mock))

    def test_ge(self):
        query = Query(**{'length.ge': 42})
        self.assertTrue(query(self.first_mock))
        self.assertFalse(query(self.second_mock))

    def test_gt_only_first(self):
        query = Query(**{'length.gt': 41})
        self.assertTrue(query(self.first_mock))
        self.assertFalse(query(self.second_mock))

    def test_gt_nothing(self):
        query = Query(**{'length.gt': 42})
        self.assertFalse(query(self.first_mock))
        self.assertFalse(query(self.second_mock))

    def test_le(self):
        query = Query(**{'length.le': 0})
        self.assertFalse(query(self.first_mock))
        self.assertTrue(query(self.second_mock))

    def test_lt_only_first(self):
        query = Query(**{'length.lt': 1})
        self.assertFalse(query(self.first_mock))
        self.assertTrue(query(self.second_mock))

    def test_lt_nothing(self):
        query = Query(**{'length.lt': 0})
        self.assertFalse(query(self.first_mock))
        self.assertFalse(query(self.second_mock))
