# -*- coding: utf-8 -*-
"""
https://ria.ru,
http://tass.ru,
https://rg.ru,
https://www.gazeta.ru,
https://lenta.ru
"""

import requests
import os
from lxml import html
from uuid import uuid4

text_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

# TODO добавить описания модуля, классов и методов
class Tree:
    """
    Класс, моделирующий DOM-дерево страницы
    """
    def __init__(self):
        self.body = None
        self.total_text_length = 0
        self.dom = dict()
        self.content_blocks = None

    def get_body(self, html_text):
        """
        Создаёт экземпляр объекта body, моделирующий тело страницы.
        :param html_text: html код страницы в текстовом формате
        """
        tree = html.fromstring(html_text)
        self.body = tree.xpath('//body')[0]

    def find_content_nodes(self, node_name='p'):
        """
        Находит в теле страницы блоки, которые содержат основной контент
        :param node_name: название тега, в котором содержится текст статьи
        """
        # На первой итерации считаем, что весь контент статьи находится в блоках <p>..</p>
        iterator = self.body.getiterator(node_name)
        self.content_blocks = [{'text': it.text_content(), 'node': it} for it in iterator if it.text_content()]

    def find_main_blocks(self):
        """
        Находит родительские контейнеры для блоков с текстом статьи.
        Если родительских блоков несколько, то по размеру текста определяет, в каком блоке основной контент
        :return: список, содержащий экземпляры контейнеров, в которых находится текст статьи
        """
        parent_blocks = list()
        for b in self.content_blocks:
            parent = b['node'].getparent()
            parent_info = {'tag': parent.tag, 'attrib': parent.attrib}
            if parent_info not in parent_blocks:
                parent_blocks.append(parent_info)
        for block in parent_blocks:
            xpath = '//{0}[@class="{1}"]'.format(block['tag'], block['attrib']['class'])
            block['xpath'] = xpath
            node = self.body.xpath(xpath)[0]
            block['text_len'] = len(node.text_content())
        parent_blocks.sort(key=lambda k: k['text_len'], reverse=True)
        main_blocks = self.body.xpath(parent_blocks[0]['xpath'])
        return main_blocks

    def find_main_text(self, main_blocks):
        """
        Находит текстовые блоки внутри главного блока, который включаев всю статью
        :param main_blocks: список блоков, в которых находится свтатья
        :return: статья, разделённая по блокам
        """
        text_blocks = list()
        for block in main_blocks:
            iterator = block.getiterator()
            for item in iterator:
                if item.text_content() is not None and item.tag in text_tags:
                    text_blocks.append({'tag': item.tag, 'text': item.text_content()})
        return text_blocks


class Page:
    """
    Класс, моделирующий страницу
    """

    def __init__(self):
        self.headers={}
        self.html_text = None
        self.tree = Tree()

    def get(self, url):
        """
        Получает страницу по указанному url, сохраниет html-текст и экземпляр объекта body.
        :param url: адрес страницы
        """
        resp = requests.get(url, headers=self.headers)
        self.html_text = resp.text
        self.tree.get_body(self.html_text)

    def extract_content(self):
        """
        Извлекает из страницы основной контент.
        :return: основной контент, разделённый на контейнеры.
        """
        self.tree.find_content_nodes()
        main_blocks = self.tree.find_main_blocks()
        main_content = self.tree.find_main_text(main_blocks)
        return main_content


class Text:
    """
    Класс для форматирования текста
    """
    def __init__(self, text):
        self.text = text

    def set_line_width(self, line_width=80):
        """
        Форматрует текст по ширине строки
        :param line_width: максимальная ширина строки в символах.
        """
        for block in self.text:
            words = block['text'].split()
            width = 0
            for i, word in enumerate(words):
                width += len(word) + 1
                if width > line_width:
                    width = len(word) + 1
                    words[i] = '\n' + words[i]
            block['text'] = ' '.join(words)

    def add_margins(self, number_of_lines=1):
        """
        Добавляет поля между абзацами и заголовками
        :param number_of_lines: вуличина поля, выраженная в количестве пустых строк
        """
        for block in self.text:
            block['text'] += '\n'*(number_of_lines + 1)

    def save(self):
        cwd = os.getcwd()
        folder = uuid4().hex
        path = os.path.join(cwd, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            path = os.path.join(path, 'art.txt')
        f = open(path, 'w')
        for i in self.text:
            f.write(i['text'])
        f.close()


if __name__ == '__main__':
    page = Page()
    page.get('https://lenta.ru/news/2017/08/23/arrest/')
    content = page.extract_content()
    text = Text(content)
    text.set_line_width()
    text.add_margins()
    text.save()
