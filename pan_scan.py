# -*- coding: utf-8 -*-
import os
import sys
import re
import mimetypes
import argparse
import baluhn


# regex taken from http://www.regular-expressions.info/creditcard.html for:
# Visa, MasterCard, American Express, Diners Club, Discover, and JCB cards
card_regex = re.compile(
    r'(?<![0-9.,])'  # don't catch card numbers in longer number sequence
    r'(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|'
    r'5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|'
    r'[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})'
    r'(?![0-9.,])')   # don't catch card numbers in longer number sequence


test_card_numbers = [
    "5431111111111111",
    "341111111111111",
    "6011601160116611",
    "378282246310005",
    "371449635398431",
    "378734493671000",
    "30569309025904",
    "38520000023237",
    "6011111111111117",
    "6011000990139424",
    "3530111333300000",
    "3566002020360505",
    "5555555555554444",
    "5105105105105100",
    "4111111111111111",
    "4012888888881881",
    "4222222222222"
]


def is_non_binary(file_path):
    """ check if mimetype matches 'text/*'
    """
    mimetype = mimetypes.guess_type(file_path)[0] or ""
    return mimetype[0:5] == 'text/'


class PanScanner(object):
    reqex = card_regex
    test_card_numbers = test_card_numbers

    def __init__(self, dirs=None, ignore_test_card_numbers=True):
        self.dirs = dirs or []
        self.ignore_test_card_numbers = ignore_test_card_numbers
        self.current_filename = None
        self.current_line_number = None
        self.filename_logged = False
        self.failed_to_open = []

    def search(self):
        for d in self.dirs:
            for filename in self.iter_dir(d):
                self.search_file(filename)
        self.log_failed_to_open()

    def iter_dir(self, directory):
        for root, dirs, files in os.walk(directory):
            for name in files:
                yield os.path.join(root, name)

    def search_file(self, filename):
        self.current_filename = filename
        if is_non_binary(self.current_filename):
            self.filename_logged = False
            try:
                with open(self.current_filename, 'r') as f:
                    for num, line in enumerate(f, 1):
                        self.current_line_number = num
                        matches = self.search_string(line)
                        if matches:
                            self.log(matches)
            except IOError:
                self.failed_to_open.append(self.current_filename)

    def search_string(self, string):
        matches = []
        for match in self.reqex.finditer(string):
            card_number = match.group(0)
            if baluhn.verify(card_number):
                matches.append(match)
        return matches

    def log(self, matches):
        if not self.filename_logged:
            self.log_func(self.file_log_message %
                          {'filename': self.current_filename})
            self.filename_logged = True
        self.log_func(self.line_log_message %
                      {'line': self.current_line_number,
                       'span': self.matches_to_string(matches)})

    def matches_to_string(self, matches):
        return ", ".join((str(m.span()) for m in matches))

    def log_failed_to_open(self):
        if self.failed_to_open:
            headline = "Failed to open:\n"
            filenames = ["* %s\n" % n for n in self.failed_to_open]
            self.log_func(headline + ''.join(filenames))

    @property
    def log_func(self):
        return sys.stdout.write

    @property
    def file_log_message(self):
        return "Found card number in %(filename)s:\n"

    @property
    def line_log_message(self):
        return "* Card number found at line %(line)s in interval: %(span)s\n"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A pan scanner.')
    parser.add_argument('-d', '--directories', nargs='+', required=True,
        help='a list of directories to scan recursively')
    args = parser.parse_args()

    PanScanner(args.directories).search()
