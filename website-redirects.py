#!/usr/bin/env python3

import sys
import csv
import re

# Exract redirects from the Sitemap CSV which maps pages from the old
# Hippo based website to the new Drupal based website.

NA = "/MISSING"
l1 = l2 = l3 = l4 = NA

def extract_migration_url(s):
    m = re.search('lib\.umd\.edu([A-Za-z/_-]+)', s)
    if m:
        return m.group(1)
    else:
        return None

reader = csv.reader(sys.stdin)
writer = csv.writer(sys.stdout, delimiter='\t')
writer.writerow(['FROM', 'TO'])

for row in reader:
    l1p, l1m, l2p, l2m, l3p, l3m, l4p, l4m = [row[i] for i in (1,4,6,7,9,10,11,12)]

    # New paths
    if l1p != "":
        l1 = l1p
        l2 = l3 = l4 = NA

    elif l2p != "":
        l2 = l2p
        l3 = l4 = NA

    elif l3p != "":
        l3 = l3p
        l4 = NA

    elif l4p != "":
        l4 = l4p

    # Migration URLs
    if url := extract_migration_url(l1m):
        writer.writerow([f'{url}', f'{l1}'])

    elif url := extract_migration_url(l2m):
        writer.writerow([f'{url}', f'{l1}{l2}'])

    elif url := extract_migration_url(l3m):
        writer.writerow([f'{url}', f'{l1}{l2}{l3}'])

    elif url := extract_migration_url(l4m):
        writer.writerow([f'{url}', f'{l1}{l2}{l3}{l4}'])

