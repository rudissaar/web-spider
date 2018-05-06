#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains WebSpiderTarget class."""

import urllib3
from urllib.parse import urlparse, urlsplit

class WebSpiderTarget:
    config = dict()
    config['skip'] = None
    config['limit'] = None
    config['url'] = None
    config['netloc'] = None
    config['scheme'] = None
    config['recursive'] = None
    config['page_source_origin'] = None
    config['page_source'] = None
    config['fetch_urls'] = None
    config['fetch_emails'] = None
    config['fetch_comments'] = None

    def __init__(self, target_dict):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if 'skip' in target_dict:
            self.skip = target_dict['skip']
        if 'limit' in target_dict:
            self.limit = target_dict['limit']
        if 'url' in target_dict:
            self.url = target_dict['url']
        if 'recursive' in target_dict:
            self.recursive = target_dict['recursive']
        if 'fetch_urls' in target_dict:
            self.fetch_urls = target_dict['fetch_urls']
        if 'fetch_emails' in target_dict:
            self.fetch_emails = target_dict['fetch_emails']
        if 'fetch_comments' in target_dict:
            self.fetch_comments = target_dict['fetch_comments']

    @property
    def skip(self):
        return self.config['skip']

    @skip.setter
    def skip(self, value):
        self.config['skip'] = bool(value)

    @property
    def limit(self):
        return self.config['limit']

    @limit.setter
    def limit(self, value):
        self.config['limit'] = int(value)

    @property
    def url(self):
        return self.config['url']

    @url.setter
    def url(self, value):
        self.config['url'] = value

    @property
    def netloc(self):
        return urlsplit(self.url).netloc

    @property
    def scheme(self):
        return urlparse(self.url)[0]

    @property
    def recursive(self):
        return self.config['recursive']

    @recursive.setter
    def recursive(self, value):
        self.config['recursive'] = bool(value)

    @property
    def page_source_origin(self):
        return self.config['page_source_origin']

    @page_source_origin.setter
    def page_source_origin(self, value):
        self.config['page_source_origin'] = value

    @property
    def page_source(self):
        return self.config['page_source']

    @page_source.setter
    def page_source(self, value):
        self.config['page_source'] = value

    @property
    def fetch_urls(self):
        return self.config['fetch_urls']

    @fetch_urls.setter
    def fetch_urls(self, value):
        self.config['fetch_urls'] = bool(value)

    @property
    def fetch_emails(self):
        return self.config['fetch_emails']

    @fetch_emails.setter
    def fetch_emails(self, value):
        self.config['fetch_emails'] = bool(value)

    @property
    def fetch_comments(self):
        return self.config['fetch_comments']

    @fetch_comments.setter
    def fetch_comments(self, value):
        self.config['fetch_comments'] = bool(value)

    def get_page_source(self, url, headers=dict()):
        """Makes request to target and returns result."""
        if url != self.page_source_origin or not self.page_source:
            try:
                http = urllib3.PoolManager(headers=headers)
                request = http.request('GET', url)
            except UnicodeEncodeError:
                print('> Failed to encode URL: ' + url)
                return b''

            self.page_source_origin = url
            self.page_source = request.data

        return self.page_source
