#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains WebSpider class."""

import calendar
import json
import os
import time
from urllib.parse import urlparse, urlsplit
import urllib3
from bs4 import BeautifulSoup
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class WebSpider:
    """Simple WebSpider."""
    settings = dict()
    settings['config_file'] = 'config.json'
    settings['headers'] = dict()
    loot = dict()

    def __init__(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.container = os.path.dirname(os.path.realpath(__file__))
        if not self.container.endswith('/'):
            self.container += '/'

        self.load_config()

    def load_config(self):
        """Parses and loads configuration from config.json file."""
        if os.path.isfile(self.settings['config_file']):
            with open(self.settings['config_file']) as data_file:
                data = json.load(data_file)
                self.settings = data
        else:
            print("> Can't find config file (" + self.settings['config_file'] + ").")
            print(
                '> You can create a new config file by copying "config.json.sample"'
                ' file and renaming it to "config.json".'
            )
            exit(1)

    @staticmethod
    def validate_url(value):
        """Helper method that checks if URL has valid format."""
        validator = URLValidator()
        try:
            validator(value)
            return True
        except ValidationError:
            return False

    @staticmethod
    def combine_uri(part_one, part_two):
        """Method that deals with combining URLs."""
        if not part_one.endswith('/'):
            part_one += '/'
        if part_two.startswith('/'):
            part_two = part_two[1:]

        return part_one + part_two

    @property
    def user_agent(self):
        """Returns value of user_agent property."""
        return self.settings['headers']['user-agent']

    @user_agent.setter
    def user_agent(self, value):
        """Assings new value to user_agent property."""
        self.settings['headers']['user-agent'] = value

    def save_loot(self):
        """Saves fetched results on drive."""
        for target in self.loot:
            if not os.path.isdir(self.container + 'loot/' + target):
                os.makedirs(self.container + 'loot/' + target, 0o700)

            cts = calendar.timegm(time.gmtime())
            path = self.container + 'loot/' + target + '/' + str(cts)

            if not os.path.isdir(path):
                os.mkdir(path, 0o700)

            try:
                with open(path + '/urls.txt', 'w+') as file_handle:
                    for url in self.loot[target]['urls']:
                        file_handle.write(url + "\n")
            except KeyError:
                if os.path.isfile(path + '/urls.txt'):
                    os.remove(path + '/urls.txt')

    def run(self):
        """Method that executes WebSpider."""
        for target in self.settings['targets']:
            netloc = urlsplit(target['url']).netloc
            self.loot[netloc] = dict()

            if target['fetch_urls']:
                self.fetch_urls(target, self.loot[netloc])

        self.save_loot()

    def fetch_urls(self, target, loot):
        """Method that fetches URLs."""
        http = urllib3.PoolManager(headers=self.settings['headers'])
        request = http.request('GET', target['url'])
        protocol = urlparse(target['url'])[0]

        data = request.data
        soup = BeautifulSoup(data, 'html.parser')

        loot['urls'] = list()

        for line in soup.find_all('a'):
            url = line.get('href')

            if not url:
                continue

            if url[:4] != 'http' and url[:2] != '//':
                url = self.combine_uri(target['url'], url)
            elif url[:2] == '//':
                url = protocol + ':' + url

            if url not in loot['urls']:
                loot['urls'].append(url)
