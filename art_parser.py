# -*- coding: utf-8 -*-

import requests
from lxml import html


# TODO разобраться, от чего должен наследоваться этот класс (object?)
# TODO добавить описания модуля, классов и методов
class Tree():

    def __init__(self):
        self.tree = None

    def get_html_tree(self, text_html):
        tree = html.fromstring(text_html)
        self.html_tree = tree.xpath('//body')[0]

    def calclulate_total_text_length(self):
        # TODO возможно стоит добавить проверку self.html_tree на предмет None
        nodes_iterator = self.html_tree.getiterator()
        total_text_length = 0
        for node in nodes_iterator:
            # TODO данный алгоритм не работает из-за того, что метод getparent() создаёт новый экземпляр объекта,
            # TODO у которого отсутствует атрибут text_length. Нужно создавать свою структуру данных
            if node.tag == 'script':
                continue
            node.text_length = 0
            if node.text is not None:
                node.text = node.text.strip()
                total_text_length += len(node.text)
                parent = node.getparent()
                while parent.tag != 'body':
                    parent.text_length += len(node.text)
                    parent = parent.getparent()
                    print(parent)
        return total_text_length

    def calculate_percent_distribution(self, text_content):
        nodes_iterator = self.html_tree.getiterator()

        for block in text_content['text_blocks']:
            ratio = len(block['text']) / text_content['total_text_length']
            block['ratio'] = ratio

class Page():

    def __init__(self):
        self.headers={}
        self.text_html = None
        self.html_tree = None
        self.tree = Tree()

    def get(self, url):
        resp = requests.get(url, headers=self.headers)
        self.text_html = resp.text
        self.tree.get_html_tree(self.text_html)

if __name__ == '__main__':
    page = Page()
    page.get('https://lenta.ru/articles/2017/08/21/cenistroyka/')
    page.tree.calclulate_total_text_length()