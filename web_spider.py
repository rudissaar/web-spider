#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains WebSpider class."""

import calendar
import json
import os
import time
import re
import sys

from urllib.parse import urlsplit
from bs4 import BeautifulSoup

import web_spider_helper as helper
from web_spider_target import WebSpiderTarget


class WebSpider:
    """Simple WebSpider."""
    settings = dict()
    settings['config_file'] = 'config.json'
    settings['headers'] = dict()

    media_types = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.pptx', '.ppt', '.svg']

    pile = list()
    trash = list()
    loot = dict()

    def __init__(self):
        self.container = os.path.dirname(os.path.realpath(__file__))
        if not self.container.endswith('/'):
            self.container += '/'

        self.load_config()
        self.cts = calendar.timegm(time.gmtime())
        self.counter = 0

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

    @property
    def user_agent(self):
        """Returns value of user_agent property."""
        return self.settings['headers']['user-agent']

    @user_agent.setter
    def user_agent(self, value):
        """Assigns new value to user_agent property."""
        self.settings['headers']['user-agent'] = value

    def save_loot(self):
        """Saves fetched results on drive."""
        for target in self.loot:
            if not os.path.isdir(self.container + 'loot/' + target):
                os.makedirs(self.container + 'loot/' + target, 0o700)

            path = self.container + 'loot/' + target + '/' + str(self.cts)

            if not os.path.isdir(path):
                os.mkdir(path, 0o700)

            for pool, _ in self.loot[target].items():
                try:
                    if self.loot[target][pool]:
                        with open(path + '/' + pool + '.txt', 'a+') as file_handle:
                            for resource in self.loot[target][pool]:
                                file_handle.write(resource + "\n")
                except KeyError:
                    pass

        # Flush.
        for target in self.loot.copy():
            self.loot.pop(target, None)

    def run(self):
        """Method that executes WebSpider."""
        for target_dict in self.settings['targets']:
            target = WebSpiderTarget(target_dict)

            if target.skip:
                continue

            sys.setrecursionlimit(target.limit)

            print('> Spidering domain: ' + target.netloc)

            self.loot[target.netloc] = dict()
            self.pile = [target.url]
            self.trash.clear()
            self.counter = 0

            try:
                while bool(self.pile):
                    for url in self.pile:
                        if target.limit is not None and self.counter >= target.limit:
                            self.pile.clear()
                            break

                        self.counter += 1
                        print('.', end='', flush=True)
                        target.url = url

                        self.pile.remove(url)
                        self.trash.append(url)

                        if target.fetch_urls:
                            if target.netloc not in self.loot:
                                self.loot[target.netloc] = dict()

                            self.fetch_urls(target, self.loot[target.netloc])

                        if target.fetch_emails:
                            self.fetch_emails(target, self.loot[target.netloc])

                        if target.fetch_comments:
                            self.fetch_comments(target, self.loot[target.netloc])

                self.save_loot()
                print("\n")
            except KeyboardInterrupt:
                print("\n")
                self.save_loot()
                exit(0)

    def fetch_urls(self, target, loot):
        """Method that fetches URLs and also drives whole Web Spider."""
        # pylint: disable=R0912
        url = helper.finalise_url(target.url, target.netloc, target.scheme)
        data = target.get_page_source(url, self.settings['headers'])

        soup = BeautifulSoup(data, 'html.parser', from_encoding="iso-8859-1")
        media = False

        if 'urls' not in loot:
            loot['urls'] = list()

        # If we are fetching for emails, then we need loot pool for it.
        if target.fetch_emails and 'emails' not in loot:
            loot['emails'] = list()

        for line in soup.find_all('a'):
            url = line.get('href')

            # If href is empty then there is no need to execute rest of the logic.
            if not bool(url):
                continue

            # Remove any whitespace surrounding URL.
            url = url.strip()

            # If href is link to email and we are also fetching for emails,
            # then append email to loot.
            if url.startswith('mailto:'):
                if target.fetch_emails:
                    email = url[url.index('mailto:') + 7:]
                    email = helper.finalise_email(email)

                    if bool(email) and email not in loot['emails']:
                        loot['emails'].append(email)

                # We found out it was email link, we dont need to execute rest of the block.
                continue

            # If href is link for telephone number then we are just ignoring it for the moment.
            if url.startswith('tel:'):
                continue

            # This Web Spider is currently only processing static output,
            # as hashtags/anchors are browser's thing we are currently trimming it from URL.
            if url and '#' in url:
                url = url[:url.index('#')]

            if not bool(url):
                continue

            # Assign finalised URL to variable.
            url = helper.finalise_url(url, target.netloc, target.scheme)

            if str(os.path.splitext(urlsplit(url).path)[1]).lower() in self.media_types:
                media = True

            if not media and url not in loot['urls']:
                loot['urls'].append(url)

            try:
                if target.recursive:
                    same_domain = urlsplit(url).netloc == target.netloc
                    same_path = urlsplit(url).path == urlsplit(target.url).path

                    # Logic that decides if we are going to process given URL.
                    if (
                            same_domain and
                            not same_path and
                            not media and
                            url not in self.pile and
                            url not in self.trash):
                        self.pile.append(url)
            except KeyError:
                pass

    def fetch_emails(self, target, loot):
        """Method that fetches emails."""
        try:
            url = helper.finalise_url(target.url, target.netloc, target.scheme)
            data = target.get_page_source(url, self.settings['headers']).decode('utf8')
        except UnicodeDecodeError:
            return

        regex = re.compile(r'[\w\.-]+@[\w\.-]+')
        emails = re.findall(regex, data)

        if 'emails' not in loot:
            loot['emails'] = list()

        for email in emails:
            email = helper.finalise_email(email)

            if bool(email) and email not in loot['emails']:
                loot['emails'].append(email)

        if self.settings['escaped_email_symbols']:
            for escaped_symbol in self.settings['escaped_email_symbols']:
                regex = re.compile(r'[\w\.-]+' + re.escape(escaped_symbol) + r'[\w\.-]+')
                emails = re.findall(regex, data)

                for escaped_email in emails:
                    email = escaped_email.replace(escaped_symbol, '@')
                    email = helper.finalise_email(email)

                    if bool(email) and not email in loot['emails']:
                        loot['emails'].append(email)

    def fetch_comments(self, target, loot):
        """Method that fetches comments."""
        try:
            url = helper.finalise_url(target.url, target.netloc, target.scheme)
            data = target.get_page_source(url, self.settings['headers']).decode('utf8')
        except UnicodeDecodeError:
            return

        regex = re.compile(r'<!--(.*)-->')
        comments = re.findall(regex, data)

        if 'comments' not in loot:
            loot['comments'] = list()

        for comment in comments:
            comment = comment.strip()

            if comment not in loot['comments']:
                loot['comments'].append(comment)


if __name__ == "__main__":
    SPIDER = WebSpider()
    SPIDER.run()
