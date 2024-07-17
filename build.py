#!/usr/bin/env python

"""
This program walks the crawled data stored in the "data" directory, and adds
each page PDF to a single title PDF. The aggregated PDF is then written to the
data directory using the document ID.
"""

from pathlib import Path

import pypdf


def main():
    count = 0
    for doc_dir in document_dirs():
        count += 1 
        pdf = pypdf.PdfWriter()
        for pdf_file in sorted(doc_dir.iterdir()):
            with pdf_file.open("rb") as fh:
                pdf.append(fh, pages=(0, 1))

        # turn the document directory into the document id by stripping the data
        # directory and converting the '/' to '_'
        output_path = Path("data") / (
            str(doc_dir).replace("data/", "").replace("/", "_") + ".pdf"
        )
        pdf.write(output_path.open("wb"))
        pdf.close()

        print(f"{count:03n} {output_path.name}")


def document_dirs():
    return [Path(d) for d in Path("data").glob("*/*/*/*")]


main()
