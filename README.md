# lapl-directories

Download metadata and PDFs for phone directories in the Los Angeles Public Library:

https://rescarta.lapl.org/

## Install

    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    
## Run

To generate a CSV of metadata for the titles, and download the PDFs for each page:

    ./crawl.py
    
NOTE: as a courtesy please enter your email address when prompted to let LAPL know you are crawling this content.


