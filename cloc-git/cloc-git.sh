#!/usr/bin/env bash

# https://stackoverflow.com/questions/26881441/can-you-get-the-number-of-lines-of-code-from-a-github-repository#answer-29012789

git clone --depth 1 "$1" temp-linecount-repo &&
  cloc --json temp-linecount-repo &&
  rm -rf temp-linecount-repo