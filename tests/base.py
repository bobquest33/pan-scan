# -*- coding: utf-8 -*-
import os
import unittest
from pan_scan import PanScanner, is_non_binary


path = os.path.dirname(os.path.abspath(__file__))


def get_absolute_path(relative_path):
    return os.path.join(path, relative_path)


class PanScanner(PanScanner):
    """ replaces `self.log` to save log internally in `self._log`
    """
    def __init__(self, dirs=None):
        super(PanScanner, self).__init__()
        self._log = []

    @property
    def log_func(self):
        return self._log.append


class NonBinaryCheckerTest(unittest.TestCase):
    def test_png(self):
        filename = get_absolute_path('test_dir/binary.png')
        self.assertFalse(is_non_binary(filename))

    def test_log(self):
        filename = get_absolute_path('test_dir/deeper/contains.log')
        self.assertTrue(is_non_binary(filename))

    def test_py(self):
        filename = get_absolute_path('test_dir/without.py')
        self.assertTrue(is_non_binary(filename))


class PanScannerTest(unittest.TestCase):
    def test_iter_dir_absolute_path(self):
        ps = PanScanner()
        directory = get_absolute_path('test_dir')
        self.assertEqual(
            [v for v in ps.iter_dir(directory)],
            [get_absolute_path('test_dir/binary.png'),
             get_absolute_path('test_dir/without.py'),
             get_absolute_path('test_dir/deeper/contains.log')])

    def test_search_file_text(self):
        ps = PanScanner()
        filename = get_absolute_path('test_dir/deeper/contains.log')
        ps.search_file(filename)
        self.assertEqual(ps._log, [
            'Found card number in %s:\n' % filename,
            '* Card number found at line 1 in interval: (28, 44)\n',
            '* Card number found at line 2 in interval: (16, 32), (57, 73)\n'
        ])

    def test_search_file_binary(self):
        searched_lines = []
        ps = PanScanner()
        ps.search_line = lambda l: searched_lines.append(l)

        filename = get_absolute_path('test_dir/binary.png')
        ps.search_file(filename)
        self.assertEqual(searched_lines, [])

    def test_search(self):
        directory = get_absolute_path('test_dir')
        ps = PanScanner([directory])
        ps.search()
        self.assertEqual(ps._log, [
            'Found card number in %s:\n' %
            get_absolute_path('test_dir/deeper/contains.log'),
            '* Card number found at line 1 in interval: (28, 44)\n',
            '* Card number found at line 2 in interval: (16, 32), (57, 73)\n'
        ])

    def test_matches_to_string(self):
        class Match:
            def __init__(self, span):
                self._span = span

            def span(self):
                return self._span
        matches = [Match((1, 2)), Match((10, 11))]
        ps = PanScanner()
        matches_string = ps.matches_to_string(matches)
        self.assertEqual(matches_string, '(1, 2), (10, 11)')

    def test_search_line_one_match(self):
        ps = PanScanner()
        self.overwrite_log(ps)
        ps.search_line('there is one match: 4111111111111111')
        self.assertEqual(len(self._matches), 1)
        self.assertEqual(self._matches[0].span(), (20, 36))

    def test_search_line_two_match(self):
        ps = PanScanner()
        self.overwrite_log(ps)
        ps.search_line('there is one match: 4111111111111111'
                       'no two matches (!): 4111111111111111')
        self.assertEqual(len(self._matches), 2)
        self.assertEqual(self._matches[0].span(), (20, 36))
        self.assertEqual(self._matches[1].span(), (56, 72))

    def test_search_line_no_matches(self):
        ps = PanScanner()
        self.overwrite_log(ps)
        ps.search_line('there is no match :(')
        self.assertRaises(AttributeError, getattr, self, '_matches')

    def overwrite_log(self, pan_scanner):
        """ overwrites `PanScanner.log` to test `PanScanner.search_line
        """
        def log_matches(matches):
            self._matches = matches
        pan_scanner.log = log_matches
