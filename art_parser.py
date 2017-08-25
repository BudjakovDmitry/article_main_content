# -*- coding: utf-8 -*-
"""
,
https://rg.ru,
https://www.gazeta.ru,
https://lenta.ru
"""

import requests
import os
import argparse
from lxml import html
from configparser import ConfigParser

text_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
config = ConfigParser()
cwd = os.getcwd()
config.read(os.path.join(cwd, 'config.ini'))

content = {
    'text_blocks': list(),
    'title': None,
    'text_includes_header': False,
    'full_text': ''}

# TODO проверить описание всех методов и классов
class Tree:
    """
    Класс, моделирующий DOM-дерево страницы
    """
    def __init__(self):
        self.body = None
        self.head = None
        self.total_text_length = 0
        self.dom = dict()
        self.content_blocks = None

    # TODO от этого метода наверное можно избаивться, так как есть готовые атрибуты head и body
    def get_body(self, html_text):
        """
        Создаёт экземпляр объекта body, моделирующий тело страницы.
        :param html_text: html код страницы в текстовом формате
        """
        tree = html.fromstring(html_text)
        self.body = tree.xpath('//body')[0]
        self.head = tree.xpath('//head')[0]

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
        main_blocks = list()
        class_keywords = ['article', 'body']
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
            # ищем по ключевым словам класса
            for kw in class_keywords:
                if kw in block['attrib']['class'] and block not in main_blocks:
                    main_blocks = (self.body.xpath(parent_blocks[0]['xpath']))
        if len(main_blocks) == 0:
            parent_blocks.sort(key=lambda k: k['text_len'], reverse=True)
            main_blocks = self.body.xpath(parent_blocks[0]['xpath'])
        return main_blocks

    def get_art_title(self):
        """
        Метод берет заголовок статьи из контейнера <title>. В дальнейшем заголовок послужит именем файла.
        """
        title = self.head.xpath('//title')[0]
        content['title'] = title.text_content()

    def get_art_text(self, block):
        for container in block.getchildren():
            # try нужна для того чтобы исключить блоки с html-комментариями. Из-за них парсер падает.
            try:
                text_content = container.text_content()
                tag = container.tag
                tail = container.tail
                if tail is not None:
                    tail = tail.strip()
            except ValueError:
                continue
            if text_content is not None and tag in text_tags:
                links = self.find_links_in_container(container)
                content['text_blocks'].append({'tag': container.tag, 'text': container.text_content(), 'links': links})
                if container.tag == 'h1':
                    content['text_includes_header'] = True
            if tail is not None and len(tail) > 0:
                links = self.find_links_in_container(block)
                content['text_blocks'].append({'tag': 'root', 'text': tail, 'links': links})
        headers = self.find_headers()
        if content['text_includes_header'] is False and headers is not None:
            content['text_blocks'].insert(0, headers)

    def find_links_in_container(self, container):
        link_objects = container.xpath('a')
        links = [{'text': i.text_content(), 'href': i.attrib['href']} for i in link_objects]
        return links

    def find_headers(self):
        headers = {'tag': None, 'text': None, 'links': list()}
        header_obj = self.body.xpath('//h1')
        if len(header_obj) > 0:
            headers['tag'] = header_obj[0].tag
            headers['text'] = header_obj[0].text_content().upper()
            return headers


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
        for block in main_blocks:
            self.tree.get_art_text(block)
        self.tree.get_art_title()


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
        for block in self.text['text_blocks']:
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
        for block in self.text['text_blocks']:
            block['text'].strip()
            if block['text'] == '':
                continue
            block['text'] += '\n'*(number_of_lines + 1)

    def decorate_links(self):
        for block in self.text['text_blocks']:
            for link in block['links']:
                start_text_index = block['text'].find(link['text'])
                end_text_index = start_text_index + len(link['text'])
                pre = block['text'][:end_text_index ]
                aft = block['text'][end_text_index:]
                # block['text'] = pre + '['link['href'] + aft
                block['text'] = '{0} [{1}] {2}'.format(pre, link['href'], aft)

    def check_file_name(self, file_name):
        forbidden_symbols = ['~', '#' '%', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '"']
        for symbol in forbidden_symbols:
            if symbol in file_name:
                file_name = file_name.replace(symbol, ' ')
        return file_name

    def agregate_text(self):
        for i in self.text['text_blocks']:
            self.text['full_text'] += i['text']

    def save(self):
        dir_path = config['GENERAL']['result_dir']
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        name = self.check_file_name(self.text['title'])
        file_name = '{0}.txt'.format(name)
        full_path = os.path.join(dir_path, file_name)
        self.agregate_text()
        with open(full_path, 'w') as art:
            for i in self.text['full_text']:
                try:
                    art.write(i)
                except UnicodeEncodeError:
                    continue


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u')
    return parser
"""
if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    url = args.url
    if url:
        page = Page()
        page.get(url)
        page.extract_content()
        text = Text(content)
        text.decorate_links()
        text.set_line_width()
        text.add_margins()
        text.save()
    else:
        print('Ошибка: Не задан обязательный аргумент --url')
"""
if __name__ == '__main__':
    page = Page()
    page.get('http://tass.ru/mezhdunarodnaya-panorama/4506469')
    page.extract_content()
    text = Text(content)
    text.decorate_links()
    text.set_line_width()
    text.add_margins()
    text.save()