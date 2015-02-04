from __future__ import with_statement # we'll use this later, has to be here
from argparse import ArgumentParser

# Copied from https://gist.github.com/chrisguitarguy/1305010

import requests
from bs4 import BeautifulSoup as Soup
from test.warning_tests import outer

def parse_sitemap(url):
    resp = requests.get(url)
    
    # we didn't get a valid response, bail
    if 200 != resp.status_code:
        print "Error: {} response code for {}".format(resp.status_code, url)
        return False
    
    # BeautifulSoup to parse the document
    soup = Soup(resp.content, features="xml")
    
    # look for the <sitemap> tags in the document
    sitemaps = soup.findAll('sitemap')
    if sitemaps:
        # this is a sitemap index
        return parse_sitemap_index(sitemaps)

    # find all the <url> tags in the document
    urls = soup.findAll('url')
    
    # no urls? bail
    if not urls:
        print "Error: no urls found for {}".format(url)
        return False
    
    # storage for later...
    out = []
    
    #extract what we need from the url
    for u in urls:
        loc = u.find('loc').string

        try:
            prio = u.find('priority').string
        except:
            prio = 'n/a'

        try:
            change = u.find('changefreq').string
        except:
            change = 'n/a'

        try:
            last = u.find('lastmod').string
        except:
            last = 'n/a'

        out.append([loc, prio, change, last])
    return out

def parse_sitemap_index(sitemaps):
    out = []
    
    for sitemap in sitemaps:
        try:
            loc = sitemap.find('loc').string
            locout = parse_sitemap(loc)
            if locout:
                out.extend(locout)
        except:
            print "Error: exception processing sitemap entry {}".format(sitemap)

    return out

if __name__ == '__main__':
    options = ArgumentParser()
    options.add_argument('-u', '--url', action='store', dest='url', help='The file contain one url per line')
    options.add_argument('-o', '--output', action='store', dest='out', default='out.txt', help='Where you would like to save the data')
    args = options.parse_args()
    urls = parse_sitemap(args.url)
    if not urls:
        print 'There was an error!'
    with open(args.out, 'w') as out:
        for u in urls:
            out.write('\t'.join([i.encode('utf-8') for i in u]) + '\n')
