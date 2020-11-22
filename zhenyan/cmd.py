#!/usr/bin/python
from scrapy import cmdline

print "begin to debug"
cmdline.execute("scrapy crawl juzimicontent".split())
