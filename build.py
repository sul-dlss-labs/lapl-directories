#!/usr/bin/env python

"""
This program walks the crawled data stored in the "data" directory, and adds
each page PDF to a single title PDF. The aggregated PDF is then written to the
data directory using the document ID.
"""

from pathlib import Path

import pypdf


def main():
    for doc_dir in document_dirs():
        print(f"generating pdf for {doc_dir}")

        pdf = pypdf.PdfWriter()
        for pdf_file in sorted(doc_dir.iterdir()):
            print(f"adding {pdf_file}")
            with pdf_file.open("rb") as fh:
                pdf.append(fh, pages=(0, 1))

        # turn the document directory into the document id by stripping the data
        # directory and converting the '/' to '_'
        output_path = Path("data") / (
            str(doc_dir).replace("data/", "").replace("/", "_") + ".pdf"
        )
        pdf.write(output_path.open("wb"))
        pdf.close()

        print(f"wrote {output_path}")


def document_dirs():
    return [Path(d) for d in Path("data").glob("*/*/*/*")]


main()
