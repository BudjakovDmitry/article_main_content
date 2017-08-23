# -*- coding: utf-8 -*-
"""
https://ria.ru,
http://tass.ru,
https://rg.ru,
https://www.gazeta.ru,
https://lenta.ru
"""

import requests
from lxml import html


# TODO разобраться, от чего должен наследоваться этот класс (object?)
# TODO добавить описания модуля, классов и методов
class Tree():

    def __init__(self):
        self.root = None
        self.total_text_length = 0
        self.dom = dict()
        self.text_content = None

    def get_html_root(self, text_html):
        tree = html.fromstring(text_html)
        self.root = tree.xpath('//body')[0]

    def find_content_nodes(self, node_name='p'):
        # На первой итерации считаем, что весь контент статьи находится в блоках <p>..</p>
        iterator = self.root.getiterator(node_name)
        self.text_content = [{'text': it.text, 'node': it} for it in iterator if it.text]

    def find_main_blocks(self):
        parent_blocks = list()
        for i in self.text_content:
            parent = i['node'].getparent()
            parent_discr = {'tag': parent.tag, 'attrib': parent.attrib}
            if parent_discr not in parent_blocks:
                parent_blocks.append(parent_discr)
        for block in parent_blocks:
            xpath = '//{0}[@class="{1}"]'.format(block['tag'], block['attrib']['class'])
            block['xpath'] = xpath
            block['text_len'] = len(self.root.xpath(xpath)[0].text_content())
        parent_blocks.sort(key=lambda k: k['text_len'], reverse=True)
        main_blocks = self.root.xpath(parent_blocks[0]['xpath'])
        # content = self.root.xpath(main_blocks['xpath'])[0].text_content()
        self.find_main_text(main_blocks)

    def find_main_text(self, main_blocks):
        text_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        text = list()
        for block in main_blocks:
            iterator = block.getiterator()
            for item in iterator:
                if item.text is not None and item.tag in text_tags:
                    text.append({'tag': item.tag, 'text': item.text})
        for i in text:
            print(i['tag'], i['text'])

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

class Page():

    def __init__(self):
        self.headers={}
        self.text_html = None
        self.tree = Tree()

    def get(self, url):
        resp = requests.get(url, headers=self.headers)
        self.text_html = resp.text
        self.tree.get_html_root(self.text_html)

    def extract_content(self):
        self.tree.find_content_nodes()
        self.tree.find_main_blocks()
        # self.tree.group_content_by_blocks()

if __name__ == '__main__':
    page = Page()
    page.get('https://lenta.ru/articles/2017/08/23/reddebt/')
    page.extract_content()
