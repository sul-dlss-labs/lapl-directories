#!/usr/bin/env python3

import csv
import re
import sys

import requests_html

http = requests_html.HTMLSession()

def doc_ids():
    url = 'https://rescarta.lapl.org/ResCarta-Web/jsp/RcWebBrowse.jsp'
    params = {
        'browse_start': 0,
        'browse_items': 48,
        'browse_index': 96,
    }
    for browse_start in [0, 48, 96, 144]:
        params['browse_start'] = browse_start
        resp = http.post(url, data=params)
        yield from page_doc_ids(resp)


def page_doc_ids(resp):
    ids = set()
    for a in resp.html.find('a'):
        onclick = a.attrs.get('onclick', '')
        if m := re.match(r"^rcWebBrowse.viewObject\('.+?', '(.+)', \d+\);", onclick):
            ids.add(m.group(1))

    return list(ids)


def doc_metadata(doc_id):
    url = 'https://rescarta.lapl.org/ResCarta-Web/jsp/RcWebImageViewer.jsp'
    resp = http.get(url, params={"doc_id": doc_id})
    resp.html.render()

    title = resp.html.find('#rc-obj-title-div span', first=True).text
    num_pages = len(resp.html.find('.jqtree-folder ul li'))

    return {
        "title": title,
        "pages": num_pages
    }

output = csv.DictWriter(open('metadata.csv', 'w'), fieldnames=['title', 'pages'])
output.writeheader()
for doc_id in doc_ids():
    metadata = doc_metadata(doc_id)
    print(metadata)
    output.writerow(metadata)








