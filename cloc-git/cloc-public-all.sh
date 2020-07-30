#!/usr/bin/env bash

# Count total files and lines of code in all public repositories for a
# GitHub organization
#
# requires jq and cloc to be installed, eg:
# brew install jq
# brew install cloc

ORG=umd-lib

# Get list of all public repositories

## TODO: determine number of pages automatically
cat /dev/null > repos.json

curl \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/orgs/${ORG}/repos?type=public&per_page=100&page=1" \
  >> repos.json

curl \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/orgs/${ORG}/repos?type=public&per_page=100&page=2" \
  >> repos.json

# Use cloc to gather counts for each repo

cat /dev/null > counts.json

for URL in $(cat repos.json | jq -r '.[].clone_url')
do
  echo $URL
  sh cloc-git.sh "$URL" >> counts.json
done

# Display summary counts

/bin/echo -n 'blank:   '
cat counts.json | jq '.SUM.blank' | paste -s -d + - | bc

/bin/echo -n 'comment: '
cat counts.json | jq '.SUM.comment' | paste -s -d + - | bc

/bin/echo -n 'code:    '
cat counts.json | jq '.SUM.code' | paste -s -d + - | bc

/bin/echo -n 'nFiles:  '
cat counts.json | jq '.SUM.nFiles' | paste -s -d + - | bc
