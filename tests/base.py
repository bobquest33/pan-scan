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
        super(PanScanner, self).__init__(dirs)
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
        ps.search_string = lambda l: searched_lines.append(l)

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

    def test_search_string_one_match(self):
        ps = PanScanner()
        matches = ps.search_string('there is one match: 4111111111111111')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].span(), (20, 36))
        self.assertEqual(matches[0].group(0), '4111111111111111')

    def test_search_string_two_match(self):
        ps = PanScanner()
        matches = ps.search_string('there is one match: 4111111111111111'
                                   'no two matches (!): 4111111111111111')
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].span(), (20, 36))
        self.assertEqual(matches[1].span(), (56, 72))
        self.assertEqual(matches[0].group(0), '4111111111111111')
        self.assertEqual(matches[1].group(0), '4111111111111111')

    def test_search_string_no_matches(self):
        ps = PanScanner()
        matches = ps.search_string('there is no match :(')
        self.assertEqual(len(matches), 0)

    def test_search_string_number_surrounded(self):
        ps = PanScanner()
        matches = ps.search_string('3334111111111111111333')
        self.assertEqual(len(matches), 0)

    def test_search_string_not_surrounded(self):
        ps = PanScanner()
        matches = ps.search_string('4111111111111111')
        self.assertEqual(len(matches), 1)

    def test_search_string_letter_surrounded(self):
        ps = PanScanner()
        matches = ps.search_string('asd4111111111111111asd')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group(0), '4111111111111111')

    def test_search_string_non_luhn(self):
        ps = PanScanner()
        n = '4111111111111113'
        test_match = ps.reqex.match(n)
        self.assertTrue(test_match)
        matches = ps.search_string(n)
        self.assertEqual(len(matches), 0)


if __name__ == '__main__':
    unittest.main()
