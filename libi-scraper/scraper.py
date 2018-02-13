#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import pdfkit
import requests
import os, errno
import logging
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup

# Constants
LIBI_URL = 'http://libi.local'
LIBI_URL_PREFIX = 'http://libi.local/'
OUTPUT_PATH_PREFIX = 'OUTPUT/'
STUDENT_APPLICATION_STR = 'Federal Work Study'
STUDENT_APPLICATION_PATH = 'student_applications/'
ATTACHMENT_DIR_SUFFIX = '_attachments/'
ATTACHMENT_PATH_PATTERN = '/sites/default/files/'
PDF_SUFFIX = '.pdf'
PDF_OPTIONS = {
    'quiet': '',
    'page-size': 'Letter',
    'dpi': 400,
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'custom-header' : [
        ('Accept-Encoding', 'gzip')
    ],
    'no-outline': None
}
INPUT_DB_ATT = 'INPUT/nid_attachments'
INPUT_DB_NODE = 'INPUT/node_urls'
LOG_PATH = 'LOG/script.log'

# Preparing LOG
logging.basicConfig(filename=LOG_PATH, filemode='w', level=logging.WARNING)

# Preparation Steps

## Get attachments info
nid_dict={};
with open(INPUT_DB_ATT, 'r') as f:
    next(f) # skip headings
    reader = csv.reader(f, delimiter='\t')
    nodeid = ''
    attachments_url = []
    for nid, url in reader:
        if nodeid!=nid:
            nodeid = nid
            if len(attachments_url)!=0:
                nid_dict[nodeid] = attachments_url
                attachments_url = []
        attachments_url.append(url)
    # add last nodeid dict
    nid_dict[nodeid] = attachments_url

## Get node info
print("Preparing nodes...")
nodes=[]
nodeIds=[]
nodeUrls=[]
with open(INPUT_DB_NODE, 'r') as f:
    next(f) # skip headings
    reader = csv.reader(f, delimiter='\t')
    for node, directory in reader:
        nodes.append(node)
        nodeIds.append(node.split('/')[-1])
        nodeUrls.append(directory)
length = str(len(nodes))
print(length + " nodes found!")

# Iterate and Conversion
for nid, dirname in zip(nodeIds, nodeUrls):
    url_path = LIBI_URL_PREFIX + dirname

    # Pick out the main content
    page = requests.get(url_path)
    if page.status_code!=404:
        soup = BeautifulSoup(page.text, 'html.parser')
        title = soup.find(class_='title')
        content = soup.find(class_='content')

        # replace relative content path to absolute content path
        if content is not None:
            for link in content.find_all('a'):
                if link.has_attr('href') and link['href'].startswith("/"):
                    link['href'] = LIBI_URL + link['href']
            for img in content.find_all('img'):
                if img.has_attr('src') and img['src'].startswith("/"):
                    img['src'] = LIBI_URL + img['src']
        else:
            logging.warning('Content is none when converting nid:' + nid)
        resHtml = str(title) + str(content)

        # IS student application
        if STUDENT_APPLICATION_STR in str(content):
            file_path = OUTPUT_PATH_PREFIX + STUDENT_APPLICATION_PATH + dirname + PDF_SUFFIX
        else:
            file_path = OUTPUT_PATH_PREFIX + dirname + PDF_SUFFIX
        directory = os.path.dirname(file_path)

        # Create directory if it is not existed
        try:
            os.stat(directory)
        except:
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        # Convert webpage using pdf kit module
        print("Converting " + file_path) 
        try:
            pdfkit.from_string(resHtml, file_path, options=PDF_OPTIONS)
        except OSError:
            logging.warning('OSError when converting nid:' + nid)
        except Exception as e:
            raise

        # Download attachments if there are any
        if (nid in nid_dict):
            # Create attachments directory
            attachment_dir = OUTPUT_PATH_PREFIX + dirname + ATTACHMENT_DIR_SUFFIX
            try:
                os.stat(attachment_dir)
            except:
                try:
                    os.makedirs(attachment_dir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
            # Fetch attachments
            for att_url in nid_dict[nid]:
                attachment_path = attachment_dir + att_url.split('/')[-1]
                attachment_url = LIBI_URL_PREFIX + urllib.parse.quote(att_url)
                try:
                    urllib.request.urlretrieve(attachment_url, attachment_path)
                except HTTPError:
                    logging.warning('HTTPError when fetching attachments for nid:' + nid)
                    logging.warning('\tRelated attachment url:' + attachment_url)
                except Exception as e:
                    raise
            attachments_number = str(len(nid_dict[nid]))
            print('\t'+ attachments_number + ' attachments fetched for nid:' + nid)
    else:
        logging.warning('404 Error when converting nid:' + nid)
print("Job done!")