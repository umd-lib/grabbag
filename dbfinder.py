#!/usr/bin/env python3

import json
import sys
import csv

# Export Database Finder databases to dbfinder.csv
#
# 1. In the Hippo console, export path=/content/documents/dbfinder/databases
# to databases.yaml
#
# 2. Use yq to convert YAML to JSON
# yq -j -P write databases.yaml - > databases.json
#
# 3. Convert JSON to CSV
# python3 dbfinder.py < databases.json > dbfinder.csv

def traverse(e):
    """ Traverse the JSON document. """
    if isinstance(e, dict):

        is_database = (
            "jcr:primaryType" in e
            and e["jcr:primaryType"] == "public:database"
            and "hippostd:state" in e
            and e["hippostd:state"] == "published"
            and "hippo:availability" in e
            and "live" in e["hippo:availability"])

        if is_database:
            handle_database(e)
        else:
            for v in e.values():
                traverse(v)


def handle_text(e, key):
    """ Handle a text field. """
    value = ""
    if key in e:
        value = e[key]
    return value


def handle_html(e, key):
    """ Handle an HTML field. """
    value = ""
    if key in e:
        value = e[key]["hippostd:content"] \
                .replace('\n','') \
                .replace('\t','')
    return value


def handle_url(e, key):
    """ Handle a public:hostURL field. """
    url, useProxy = "", ""
    if key in e:
        url = e[key]["public:url"]
        useProxy = str(e[key]["public:useProxy"])
    return url, useProxy


def handle_list(e, key):
    """ Handle an array field. """
    if key in e:
        return e[key]
    else:
        return []


def handle_database(e):
    """ Handle a single database. """

    global rowcount, writer

    row = []
    headers = []

    headers.append("ResourceID")
    row.append(e["public:resourceID"])

    headers.append("Name")
    row.append(e["public:name"])

    headers.append("Description")
    row.append(handle_html(e, "/public:description"))

    headers.append("Coverage")
    row.append(handle_html(e, "/public:coverage"))

    headers.append("Time Span")
    row.append(handle_text(e, "public:timeSpan"))

    headers.append("URL")
    url, useProxy = handle_url(e, "/public:hostURL")
    row.append(url)

    headers.append("Vendor")
    row.append(handle_text(e, "public:vendor"))

    headers.append("Type")
    row.append('; '.join(handle_list(e, "public:type")))

    headers.append("Keywords (displayed)")
    row.append('; '.join(handle_list(e, "public:keywords")))

    headers.append("Use Proxy")
    row.append(useProxy)

    headers.append("Subject")
    row.append('; '.join(handle_list(e, "public:subject")))

    headers.append("Notes")
    row.append(handle_text(e, "public:notes"))

    headers.append("Search Hints")
    row.append(handle_html(e, "/public:searchHints"))

    headers.append("Best Bets")
    row.append('; '.join(handle_list(e, "public:bestBets")))

    headers.append("Restriction Type")
    row.append(handle_text(e, "public:restrictionType"))

    headers.append("Keywords (not displayed)")
    row.append('; '.join(handle_list(e, "public:keywords_hide")))

    if rowcount == 0:
        writer.writerow(headers)

    writer.writerow(row)
    rowcount += 1


doc = json.load(sys.stdin)
writer = csv.writer(sys.stdout)

rowcount = 0

traverse(doc)

