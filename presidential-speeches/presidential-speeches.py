#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime
import csv
from bs4 import BeautifulSoup
import yaml

with open('config.yml', 'r') as configfile:
    globals().update(yaml.safe_load(configfile))

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2):
    raise Exception("This script requires Python 3.2 or greater")

def main():
    if not os.path.isdir(BASE_DIR):
        os.mkdir(BASE_DIR)
    
    query = sys.argv[1] if len(sys.argv) > 1 else ''
    pres = PRESIDENCY if PRESIDENCY is not None else ''
    
    # Choose base for output CSV filename, depending on query parameters
    # If a searchterm is present, filename will be based on searchterm
    if query != '' and query != ' ':
       fileBase = query
    # If no searchterm, but a presidency has been specified use pres name
    elif pres != '':
        fileBase = ALL_PRESIDENTS[pres]
    # Otherwise, use the range of years being searched
    else:
        fileBase = "{0}-{1}".format(str(BEGIN_DATE.year), str(END_DATE.year))
    
    # Open output CSV file
    csvFileName = os.path.join(BASE_DIR, fileBase.replace(' ','_') + '.csv')
    print(csvFileName)
    
    with open(csvFileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, quoting=csv.QUOTE_ALL)
        csvWriter.writerow(['PID','file name','date','leader','Speech','URL',
            'Date (YYYMMDD)','Speech Number','Speech Unique ID'])

        # Execute the search using supplied query string, once per year
        for year in range(BEGIN_DATE.year, END_DATE.year + 1):
            monthstart = str(BEGIN_DATE.month) if year == BEGIN_DATE.year else '1'
            daystart = str(BEGIN_DATE.day) if year == BEGIN_DATE.year else '1'
            monthend = str(END_DATE.month) if year == END_DATE.year else '12'
            dayend = str(END_DATE.day) if year == END_DATE.year else '31'
                
            params = urllib.parse.urlencode({'searchterm' : query,
                                             'yearstart' : str(year),
                                             'monthstart' : monthstart,
                                             'daystart' : daystart,
                                             'yearend' : str(year),
                                             'monthend' : monthend,
                                             'dayend' : dayend,
                                             'pres' : pres
            })
            
            url = BASE_URL + "?" + params
            print("Search URL: ", url)
            
            with urllib.request.urlopen(url) as f:
            
                # Get results page html as a string
                html = f.read().decode("windows-1251")
        
                # Search the html for the list of documents
                for match in re.findall("<td.*?class=listdate.*?>(.*?)</td>.*?<td.*?class=listname.*?>(.*?)</td>.*?<a href='index.php\?pid=(\d+).*?class=listlink>(.*?)</a>", html, re.MULTILINE|re.IGNORECASE):
                    (dateString,leader,pid,speech) = match
                
                    # data cleanup
                    leader = leader.replace('&nbsp;','').strip()
                    
                    # if leader filter is set, cut processing loop short for 
                    # results not matching names in leader filter list
                    if len(LEADER_FILTER) > 0:
                        if leader not in LEADER_FILTER:
                            print("Skipping speech by {0}...".format(leader))
                            continue
                    
                    speech = speech.replace('&nbsp;','')
                    speech = re.sub(r'<.*?>', '', speech)
                    
                    date = datetime.strptime(dateString, "%B %d, %Y")  
        
                    getSpeech(csvWriter, date, leader, pid, speech)

def getSpeech(csvWriter, date, leader, pid, speech):
    '''Get a single speech as text and write metdata out to CSV'''

    # Create the filename and path to hold the text of the speech
    baseName = leader.replace(' ','_').replace('.','').replace(',','')
    directoryName = os.path.join(BASE_DIR, baseName)
    if not os.path.isdir(directoryName):
        os.mkdir(directoryName)
    
    fileName = baseName + "_" + date.strftime("%Y%m%d") + "_" + pid + ".txt"
     
    filePath = os.path.join(directoryName, fileName)

    # Get speech number, if there is one
    match = re.match("^(\d)+", speech)
    if match: 
        speechNum = match.group(0)   
        speechID = date.strftime("%Y%m%d") + "." + speechNum
        while len(speechID) < 13:
            speechID = speechID + "0"
    else:
        speechID = ""
        speechNum = ""

    # Write the CSV metdata entry
    row = [
           pid,
           filePath,
           date.strftime("%d-%b-%Y"),
           leader,
           speech,
           BASE_URL + "?" + urllib.parse.urlencode({'pid' : pid}),
           date.strftime("%Y%m%d"),
           speechNum,
           speechID
           ]
    csvWriter.writerow(row)

    # Get the text of the speech
    if os.path.isfile(filePath):
        print('Skipping: ', pid, filePath)
    else:
        urlPrint = BASE_URL_PRINT + "?" + urllib.parse.urlencode({'pid' : pid})
        print('Downloading: ', pid, filePath)
    
        with urllib.request.urlopen(urlPrint) as f:
        
            # Get results page html as a string
            html = f.read().decode("iso-8859-1")

            # Strip out html 
            soup = BeautifulSoup(html, 'html.parser')
            body = soup.find('body')
            text = body.get_text()

            # Write out to file
            with open(filePath, 'w') as fileTxt:
                fileTxt.write(text)
            
main()
