#!/usr/bin/env python3

"""
This program collects metadata about titles in the https://rescarta.lapl.org
websites and then downloads pdfs for each of the pages.

Please use your email address when prompted in case LAPL would like to get in
touch with you about the crawling.
"""

import csv
import logging
import pathlib
import re
import time
import tqdm

import requests_html


email = input("As a courtesy to LAPL enter your email address to use as a User-Agent: ")
http = requests_html.HTMLSession()
http.headers = {
    "User-Agent": "https://github.com/sul-dlss-labs/lapl-directories on behalf of {email}"
}


def main():
    logging.basicConfig(filename="crawl.log", level=logging.INFO)
    output = csv.DictWriter(
        open("metadata.csv", "w"),
        fieldnames=[
            "id",
            "url",
            "title",
            "num_pages",
            "type_of_resource",
            "genre_authority",
            "language",
            "date_captured",
            "place_of_publication",
            "subject_geographic",
            "subject_topic",
            "publisher_name",
            "collection",
            "volume",
            "genre",
            "date_published",
            "owner"
        ],
    )
    output.writeheader()
    for doc_id in doc_ids():
        logging.info(f"found doc_id {doc_id}")
        metadata = doc_metadata(doc_id)
        logging.info("found metadata {metadata}")
        output.writerow(metadata)
        download_pdfs(metadata)


def doc_ids():
    """
    Get all the document ids from the browse page.
    """
    url = "https://rescarta.lapl.org/ResCarta-Web/jsp/RcWebBrowse.jsp"
    params = {
        "browse_start": 0,
        "browse_items": 48,
        "browse_index": 96,
    }
    for browse_start in [0, 48, 96, 144]:
        params["browse_start"] = browse_start
        resp = http.post(url, data=params)
        yield from page_doc_ids(resp)


def page_doc_ids(resp):
    """
    Get all document ids on a specific browse page.
    """
    ids = set()
    for a in resp.html.find("a"):
        onclick = a.attrs.get("onclick", "")
        if m := re.match(r"^rcWebBrowse.viewObject\('.+?', '(.+)', \d+\);", onclick):
            ids.add(m.group(1))

    return list(ids)


def doc_metadata(doc_id):
    """
    Get the metadata for a given document.
    """
    url = "https://rescarta.lapl.org/ResCarta-Web/jsp/RcWebImageViewer.jsp"
    resp = http.get(url, params={"doc_id": doc_id})
    resp.html.render()

    metadata = {
        "url": f"https://rescarta.lapl.org/ResCarta-Web/jsp/RcWebImageViewer.jsp?doc_id={doc_id}",
        "title": resp.html.find("#rc-obj-title-div span", first=True).text,
        "num_pages": len(resp.html.find(".jqtree-folder ul li")) - 1
    }

    # get more metadata details from the pop out table
    url = "https://rescarta.lapl.org/ResCarta-Web/jsp/RcWebMetadataViewer.jsp"
    resp = http.get(url, params={"doc_id": doc_id, "pg_seq": 1})
    resp.html.render()

    for tr in resp.html.find('table tr'):
        cells = tr.find('td')
        name = cells[0].text.lower().replace(' ', '_')
        value = cells[1].text
        if name not in ['height', 'width']:
            metadata[name] = value

    return metadata


def download_pdfs(metadata):
    doc_id = metadata["id"]
    num_pages = metadata["num_pages"]
    title = metadata["title"]

    for page_num in tqdm.tqdm(range(1, num_pages + 1), desc=title[0:30]):
        output_dir = pathlib.Path(f"data/{doc_id}")
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)

        output_file = output_dir / ("%09i.pdf" % page_num)
        if output_file.is_file():
            logging.info(f"skipping {doc_id} page={page_num}")
            continue

        params = {"doc_id": doc_id, "pg_seq": page_num}

        resp = http.get(
            "https://rescarta.lapl.org/ResCarta-Web/servlet/PdfRenderer/file.pdf",
            params=params,
        )
        resp.raise_for_status()

        output_file.open("wb").write(resp.content)
        logging.info(f"downloaded {params}")

        # be nice
        time.sleep(1.5)


if __name__ == "__main__":
    main()
