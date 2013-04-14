# -*- coding: utf-8 -*-
import os
import sys
import mimetypes


def is_non_binary(file_path):
    """ check if mimetype matches 'text/*'
    """
    mimetype = mimetypes.guess_type(file_path)[0] or ""
    return mimetype[0:5] == 'text/'


class PanScanner(object):
    reqex = card_regex

    def __init__(self, dirs=None):
        self.dirs = dirs or []
        self.current_filename = None
        self.current_line_number = None
        self.filename_logged = False

    def search(self):
        for d in self.dirs:
            for filename in self.iter_dir(d):
                self.search_file(filename)

    def iter_dir(self, directory):
        for root, dirs, files in os.walk(directory):
            for name in files:
                yield os.path.join(root, name)

    def search_file(self, filename):
        self.current_filename = filename
        if is_non_binary(self.current_filename):
            self.filename_logged = False
            with open(self.current_filename, 'r') as f:
                for num, line in enumerate(f, 1):
                    self.current_line_number = num
                    self.search_line(line)

    def search_line(self, line):
        matches = [m for m in self.reqex.finditer(line)]
        if matches:
            self.log(matches)

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

    @property
    def log_func(self):
        return sys.stdout.write

    @property
    def file_log_message(self):
        return "Found card number in %(filename)s:\n"

    @property
    def line_log_message(self):
        return "* Card number found at line %(line)s in interval: %(span)s\n"

