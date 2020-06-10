#!/bin/bash

FUSEKI=https://fcrepo.lib.umd.edu/fuseki/fedora4/query

s-query --service=$FUSEKI --query=binaries.rq > binaries.json
s-query --service=$FUSEKI --query=binaries-prange.rq > binaries-prange.json
s-query --service=$FUSEKI --query=binaries-newspaper-tiff.rq > binaries-newspaper-tiff.json
s-query --service=$FUSEKI --query=binaries-newspaper-pdf.rq > binaries-newspaper-pdf.json

python3 binaries.py
