#!/usr/bin/env python3

import json

for file in ('binaries.json', 'binaries-prange.json',
             'binaries-newspaper-pdf.json', 'binaries-newspaper-tiff.json'):

    c = {}

    with open(file, 'r') as fd:
        j = json.load(fd)

        for result in j['results']['bindings']:
            subject = result['subject']['value']
            size = int(result['size']['value'])

            if subject not in c:
                c[subject] = 0

            c[subject] += size


    l = sorted(c.items(), reverse=True, key=lambda x: x[1])

    total = 0
    print(file)
    for subject, size in l[:10]:
        print(subject, size)
        total += size
    print(f'total={total}')

