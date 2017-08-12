#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
import urllib3


class WebSpider:
    settings = dict()

    def __init__(self):
        pass

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
        if not self.validate():
            exit(1)

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        http = urllib3.PoolManager()
        request = http.request('GET', self.target)
        data = request.data;
        soup = BeautifulSoup(data, 'html.parser')

        for line in soup.find_all('a'):
            line = line.get('href')
            print(line)
