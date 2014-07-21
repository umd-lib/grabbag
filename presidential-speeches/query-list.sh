#!/bin/bash

# Execute multiple queries in query-list.txt
while read query; do
  echo Querying "$query"
  python3.3 presidential-speeches.py "$query"
done < query-list.txt
