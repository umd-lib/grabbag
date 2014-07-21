import xml.etree.ElementTree as ET
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime
import csv
from bs4 import BeautifulSoup

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2):
    raise Exception("This script requires Python 3.2 or greater")

BASE_URL = "http://www.presidency.ucsb.edu/ws/index.php"
BASE_URL_PRINT = "http://www.presidency.ucsb.edu/ws/print.php"
BASE_DIR = "speeches"

def main():
    query = sys.argv[1]
    
    if not os.path.isdir(BASE_DIR):
        os.mkdir(BASE_DIR)

    # Open output CSV file, named with the query used
    csvFileName = os.path.join(BASE_DIR, query.replace(' ','_') + '.csv')    
    with open(csvFileName, 'w') as csvFile:
        csvWriter = csv.writer(csvFile, quoting=csv.QUOTE_ALL)
        csvWriter.writerow(['PID','file name', 'date', 'leader', 'Speech', 'URL', 'Date (YYYMMDD)','Speech Number','Speech Unique ID'])

        # Execute the search using supplied query string, once per year
        nextYear = datetime.now().year + 1
        for year in range(1933, nextYear):
            if year == 1933:
                monthstart = '03'
                daystart = '04'
            else:
                monthstart = '01'
                daystart = '01'
    
            params = urllib.parse.urlencode({'searchterm' : query,
                                             'yearstart' : str(year),
                                             'monthstart' : monthstart,
                                             'daystart' : daystart,
                                             'yearend' : str(year),
                                             'monthend' : '12',
                                             'dayend' : '31'
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
            soup = BeautifulSoup(html)
            body = soup.find('body')
            text = body.get_text()

            # Write out to file
            with open(filePath, 'w') as fileTxt:
                fileTxt.write(text)
            
main()