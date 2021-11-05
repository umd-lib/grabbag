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
writer = csv.writer(sys.stdout)
writer.writerow(['FROM', 'TO'])

for row in reader:

    # New paths
    if row[1] != "":
        l1 = row[1]
        l2 = l3 = l4 = NA

    elif row[6] != "":
        l2 = row[6]
        l3 = l4 = NA

    elif row[11] != "":
        l3 = row[11]
        l4 = NA

    elif row[16] != "":
        l4 = row[16]

    # Migration URLs
    if url := extract_migration_url(row[4]):
        writer.writerow([f'{url}', f'{l1}'])

    elif url := extract_migration_url(row[9]):
        writer.writerow([f'{url}', f'{l1}{l2}'])

    elif url := extract_migration_url(row[14]):
        writer.writerow([f'{url}', f'{l1}{l2}{l3}'])

    elif url := extract_migration_url(row[19]):
        writer.writerow([f'{url}', f'{l1}{l2}{l3}{l4}'])

