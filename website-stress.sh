#!/bin/bash

# Simple website stress tester, using an XML sitemap
threads=10
while getopts s:t: flag
do
    case "${flag}" in
        s) sitemap=${OPTARG};;
        t) threads=${OPTARG};;
    esac
done

curl --silent "$sitemap" \
  | perl -n -e '/\<loc\>(.*)\<\/loc\>/ && print "curl -s -o /dev/null -w \"%{http_code}\\n\" $1\n";' \
  | ./mpbatch.py --log /tmp/website-stress.json --threads "$threads"

jq . < /tmp/website-stress.json | grep status | grep -v 200
