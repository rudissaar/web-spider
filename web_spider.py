#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import urllib3
from bs4 import BeautifulSoup
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

class WebSpider:
    settings = dict()

    settings['config_file'] = 'config.json'
    settings['headers'] = dict()

    def __init__(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.load_config()

    def load_config(self):
        if os.path.isfile(self.settings['config_file']):
            with open(self.settings['config_file']) as data_file:
                data = json.load(data_file)
                self.settings = data
        else:
            print("> Can't find config file (" + self.settings['config_file'] + ").")
            print("> You can create a new config file by copying 'config.json.sample' file and renaming it.")
            exit(1)

    @staticmethod
    def validate_url(value):
        validator = URLValidator()
        try:
            validator(value)
            return True
        except ValidationError:
            return False

    @staticmethod
    def combine_uri(part_one, part_two):
        if not part_one.endswith('/'):
            part_one += '/'
        if part_two.startswith('/'):
            part_two = part_two[1:]

        return part_one + part_two

    @property
    def user_agent(self):
        return self.settings['headers']['user-agent']

    @user_agent.setter
    def user_agent(self, value):
        self.settings['headers']['user-agent'] = value

    def run(self):
        http = urllib3.PoolManager(headers=self.settings['headers'])

        for target in self.settings['targets']:
            request = http.request('GET', target['url'])
            protocol = urlparse(target['url'])[0]

            data = request.data;
            soup = BeautifulSoup(data, 'html.parser')

            for line in soup.find_all('a'):
                url = line.get('href')

                if not url:
                    continue

                if url[:4] != 'http' and url[:2] != '//':
                    url = self.combine_uri(target['url'], url)
                elif url[:2] == '//':
                    url = protocol + ':' + url

                print(url)
