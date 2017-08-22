# -*- coding: utf-8 -*-

import requests
from lxml import html


# TODO разобраться, от чего должен наследоваться этот класс (object?)
# TODO добавить описания модуля, классов и методов
class Tree():

    def __init__(self):
        self.tree = None
        self.root = None
        self.total_text_length = 0
        self.dom = dict()

    def get_html_tree(self, text_html):
        tree = html.fromstring(text_html)
        self.root = tree.xpath('//body')[0]

    def find_text_content(self):
        iterator = self.root.getiterator('p')
        text_content = [{'text': i.text, 'node': i} for i in iterator if i.text]
        for i in text_content:
            parent = i['node'].getparent()
            i['parent_attr'] = parent.attrib
        print('g')

    def calc_text_len(self, text_content):
        total_text_len = 0
        for block in text_content:
            total_text_len += len(block['text'])
        tags = dict()
        for i in text_content:
            if i['tag'] not in tags:
                tags[i['tag']] = len(i['text'])
            else:
                tags[i['tag']] += len(i['text'])
        rating = sorted(tags, key=lambda k: tags[k], reverse=True)
        for i in text_content:
            if i['tag'] == rating[0]:
                print(i['text'])
        print('ssf')

class Page():

    def __init__(self):
        self.headers={}
        self.text_html = None
        self.tree = Tree()

    def get(self, url):
        resp = requests.get(url, headers=self.headers)
        self.text_html = resp.text
        self.tree.get_html_tree(self.text_html)

    def extract_content(self):
        self.tree.find_text_content()

if __name__ == '__main__':
    page = Page()
    page.get('https://rg.ru/2017/08/22/reg-cfo/kalashnikov-pokazal-neletalnoe-oruzhie-novgo-pokoleniia.html')
    page.extract_content()