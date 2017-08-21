# -*- coding: utf-8 -*-

import requests
from lxml import html


# TODO разобраться, от чего должен наследоваться этот класс (object?)
class Page():

    def __init__(self):
        self.headers={}
        self.html_text = None
        self.body = None

    def _conv_text_to_html(self):
        tree = html.fromstring(self.html_text)
        self.body = tree.xpath('//body')[0]

    def get(self, url):
        resp = requests.get(url, headers=self.headers)
        self.html_text = resp.text
        self._conv_text_to_html()
