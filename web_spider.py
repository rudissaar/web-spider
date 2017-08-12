#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import urllib3
import json
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup


class WebSpider:
    settings = dict()

    settings['config_file'] = 'config.json'

    def __init__(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.load_config()

    def load_config(self):
        if os.path.isfile(self.settings['config_file']):
            with open(self.settings['config_file']) as data_file:
                data = json.load(data_file)
                self.settings['targets'] = data['targets']

    @property
    def target(self):
        return self.settings['target']

    @target.setter
    def target(self, value):
        self.settings['target'] = value

    @staticmethod
    def validateUrl(value):
        validator = URLValidator()
        try:
            validator(value)
            return True
        except ValidationError:
            return False

    def validate(self):
        if not self.validateUrl(self.target):
            return False

        return True

    def run(self):
        http = urllib3.PoolManager()

        for target in self.settings['targets']:
            print(target['url'])
            request = http.request('GET', target['url'])
            data = request.data;
            soup = BeautifulSoup(data, 'html.parser')

            for line in soup.find_all('a'):
                line = line.get('href')
                print(line)
