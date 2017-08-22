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
        children_all = self.root.getchildren()
        children_selected = [cld for cld in children_all if cld.tag != 'script']
        self.dom[self.root] = {
            'parent': None,
            'children': children_selected,
            'text_len': 0
        }
        # Чтобы не делать рекурсию. Очередь для записи нод
        self._nodes_queue = [{'parent': self.root, 'node': node} for node in children_selected]
        while self._nodes_queue:
            self.add_nodes_to_tree(self._nodes_queue[0])
        # TODO to_delete
        print('Общее количество узлов в dom дереве:', str(len(self.dom)), '\n')

    def add_nodes_to_tree(self, node):
        # TODO дублирование
        children_all = node['node'].getchildren()
        children_selected = [cld for cld in children_all if cld.tag != 'script']
        self.dom[node['node']] = {
            'node': node['node'],
            'parent': node['parent'],
            'children': children_selected,
            'text_len': 0}
        for child in children_selected:
            self._nodes_queue.append({'parent': node['node'], 'node': child})
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

    def find_content_blocks(self):
        children = [self.dom[cld] for cld in self.dom[self.root]['children']]
        children.sort(key=lambda d: d['ratio'], reverse=True)
        while children[0]['ratio'] >= 0.5:
            children = [self.dom[cld] for cld in self.dom[children[0]['node']]['children']]
            children.sort(key=lambda d: d['ratio'], reverse=True)
        else:
            print(children[0])
            self.find_all_children_of_element(children[0]['node'])

    def find_all_children_of_element(self, node):
        iterator = node.getiterator()
        for i in iterator:
            if i.text is not None:
                print(i.text)

class Page():

    def __init__(self):
        self.headers={}
        self.text_html = None
        # self.html_tree = None
        self.tree = Tree()

    def get(self, url):
        resp = requests.get(url, headers=self.headers)
        self.text_html = resp.text
        self.tree.get_html_tree(self.text_html)

    def extract_content(self):
        self.tree.calculate_text_length()
        self.tree.calculate_percent_distribution()
        self.tree.find_content_blocks()
        # self.tree.find_all_children_of_element()

if __name__ == '__main__':
    page = Page()
    page.get('https://lenta.ru/articles/2017/08/21/cenistroyka/')
    page.extract_content()
    print('The end')