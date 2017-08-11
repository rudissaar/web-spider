#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from web_spider import WebSpider

spider = WebSpider()
spider.target = sys.argv[1]
spider.run();