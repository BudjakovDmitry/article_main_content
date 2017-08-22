# -*- coding: utf-8 -*-

import requests
from lxml import html


# TODO разобраться, от чего должен наследоваться этот класс (object?)
# TODO добавить описания модуля, классов и методов
class Tree():

    def __init__(self):
        self.tree = None
        self.total_text_length = 0
        self.dom = dict()

    # TODO переименовать метод на get_root
    def get_html_tree(self, text_html):
        tree = html.fromstring(text_html)
        # TODO переименовать переменную на get_root
        self.html_tree = tree.xpath('//body')[0]
        self.dom[self.html_tree] = {
            'parent': None,
            'children': self.html_tree.getchildren(),
            'text_len': 0
        }
        # Чтобы не делать рекурсию. Очередь для записи нод
        children = self.html_tree.getchildren()
        self._nodes_queue = [{'parent': self.html_tree, 'node': node} for node in children if node.tag != 'script']
        while self._nodes_queue:
            self.add_nodes_to_tree(self._nodes_queue[0])
        # TODO to_delete
        print('Общее количество узлов в dom дереве:', str(len(self.dom)), '\n')

    def add_nodes_to_tree(self, node):
        children = node['node'].getchildren()
        self.dom[node['node']] = {'parent': node['parent'], 'children': children, 'text_len': 0}
        for i in children:
            if i.tag == 'script':
                continue
            self._nodes_queue.append({'parent': node['node'], 'node': i})
        self._nodes_queue.remove(node)

    def calculate_text_length(self):
        for node in self.dom:
            if node.text is not None:
                self.total_text_length += len(node.text.strip())
                self.dom[node]['text_len'] = len(node.text.strip())
                parent = self.dom[node]['parent']
                while parent is not None:
                    self.dom[parent]['text_len'] += len(node.text.strip())
                    parent = self.dom[parent]['parent']
        # TODO to_delete
        print('Общая длина текста', str(self.total_text_length), '\n')

    def calculate_percent_distribution(self):
        for item in self.dom:
            self.dom[item]['ratio'] = self.dom[item]['text_len'] / self.total_text_length

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

    def extract_content(self):
        self.tree.calculate_text_length()
        self.tree.calculate_percent_distribution()

if __name__ == '__main__':
    page = Page()
    page.get('https://lenta.ru/articles/2017/08/21/cenistroyka/')
    page.extract_content()