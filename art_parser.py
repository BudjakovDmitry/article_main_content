# -*- coding: utf-8 -*-

import requests
from lxml import html


# TODO разобраться, от чего должен наследоваться этот класс (object?)
class Page():

    def __init__(self):
        self.headers={}
        self.html_text = None
        self.html_tree = None
        self.text_content = None

    def _get_html_tree(self):
        tree = html.fromstring(self.html_text)
        self.html_tree = tree.xpath('//body')[0]

    def get(self, url):
        resp = requests.get(url, headers=self.headers)
        self.html_text = resp.text
        self._get_html_tree()
